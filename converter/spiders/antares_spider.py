import os

import xmltodict as xmltodict
from lxml import etree
from scrapy.spiders import CrawlSpider
from scrapy.utils.project import get_project_settings
from w3lib.http import basic_auth_header
import datetime

from converter.constants import Constants
from converter.items import *
from converter.pipelines import ProcessThumbnailPipeline
from converter.spiders import get_project_root
from converter.spiders.lom_base import LomBase


import pandas as pd


class AntaresSpider(CrawlSpider, LomBase):
    """
    This crawler fetches data from the Antares content source, which provides us paginated XML data per State (Land) and
    County (Kreis). For every element in the returned XML array we call LomBase.parse(), which in return calls methods,
    such as getId(), getBase() etc.

    Author: Ioannis Koumarelas, ioannis.koumarelas@hpi.de, Schul-Cloud, Content (/Embla) team.
    """

    name = "antares_spider"
    url = "https://www.antares.net/"  # the url which will be linked as the primary link to your source (should be the main url of your site)
    friendlyName = "Antares"  # name as shown in the search ui
    version = "1.0"  # the version of your crawler, used to identify if a reimport is necessary
    apiUrl = "https://arix.datenbank-bildungsmedien.net/%state/%county"
    dataForm = "xmlstatement=<harvest start='%start' count='%count' mime='text/html' />"

    limit = 100

    execution_per_state_county_list = []  # [{"state": "X", "county": "Y", ..., "start": "0"})]
    state_county_counter = 0

    antares_code_to_value_mapping = None
    antares_state_counties = None

    id_to_prepared_dict = {}
    thumbnail_cache = {}

    def __init__(self, **kwargs):
        LomBase.__init__(self, **kwargs)
        self.antares_code_to_value_mapping = self.read_antares_code_mapping()
        self.antares_state_counties = self.read_antares_states_counties()

        # If a proxy is available replace the API's URL.
        if "HPI_SCHUL_CLOUD_PROXY" in get_project_settings():
            self.apiUrl = self.apiUrl.replace("https://arix.datenbank-bildungsmedien.net",
                                              get_project_settings().get("HPI_SCHUL_CLOUD_PROXY"))

        for li in self.antares_state_counties:
            self.execution_per_state_county_list.append({
                "state": li["Land abbreviation"],
                "state_DISPLAYNAME": li["Land"],
                "county": li["KFZ KZ"],
                "county_DISPLAYNAME": li["Kreis"],
                "page": 0
            })


    def _proxify_request(self, request):
        settings = get_project_settings()

        proxy_username = settings.get("HPI_SCHUL_CLOUD_PROXY_USERNAME")
        proxy_password = settings.get("HPI_SCHUL_CLOUD_PROXY_PASSWORD")

        # If a proxy server solution is used.

        # proxy = settings.get("HPI_SCHUL_CLOUD_PROXY")
        # request.meta["proxy"] = proxy
        # request.headers["Proxy-Authorization"] = basic_auth_header(proxy_username, proxy_password)

        # Else if a proxy endpoint is used, which automatically forwards our requests, we do not need to specify the
        #   hostname as a proxy server. However, authorization is still needed to keep the portal protected.
        request.headers["Authorization"] = basic_auth_header(proxy_username, proxy_password)

        return request

    def start_requests(self):
        yield self._proxify_request(scrapy.Request(
            url=self.apiUrl
                .replace("%state", self.execution_per_state_county_list[self.state_county_counter]["state"])
                .replace("%county", self.execution_per_state_county_list[self.state_county_counter]["county"]),
            body=self.dataForm
                .replace("%start", str(self.execution_per_state_county_list[self.state_county_counter]["page"] * self.limit))
                .replace("%count", str(self.limit - 1)),
            callback=self.parse,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
            encoding='utf-8'
        ))

    def parse(self, response: scrapy.http.Response):
        logging.info("Parsing URL: " + response.url)

        state_county_info = self.execution_per_state_county_list[self.state_county_counter]
        logging.info(
            "Of state: " + state_county_info["state"] +
            ", county: " + state_county_info["county"] +
            ", and page: " + str(state_county_info["page"])
        )

        root = etree.XML(response.body)
        tree = etree.ElementTree(root)

        # Convert items to dictionaries, whilst also preparing their values.
        elements = tree.xpath("/result/*")
        if len(elements) > 0:
            now = datetime.datetime.now()

            for element in elements:
                prepared_dict = {"id": "- Not defined yet! -"}
                element_xml_str = etree.tostring(element, pretty_print=True, encoding="unicode")
                try:
                    prepared_dict = xmltodict.parse(element_xml_str)

                    # Preparing the values here helps for all following logic across the methods.
                    prepared_dict = self.prepare_element(prepared_dict,
                                                         antares_code_to_value_mapping=self.antares_code_to_value_mapping)

                    # If license has expired, skip it!
                    if "lizenz_bis" in prepared_dict:
                        license_expiration_date = datetime.datetime.strptime(prepared_dict["lizenz_bis"], '%Y-%m-%d')
                        if license_expiration_date <= now:
                            logging.info("Item's license has already expired. Skipping!")
                            continue
                        else:
                            logging.debug("Item's license is valid!")

                    prepared_dict["element_xml_str"] = element_xml_str

                    copy_response = response.copy()

                    # In case XML string representation is preferred:
                    copy_response._set_body(element_xml_str)

                    # If the element has been met in a former state/county we should already have the thumbnail.
                    if "prefetched_thumbnail" not in prepared_dict:
                        obtained_thumbnail = self._request_thumbnail(prepared_dict, copy_response)
                        prepared_dict["prefetched_thumbnail"] = obtained_thumbnail["thumbnail"]
                        self.thumbnail_cache[prepared_dict["mmdatei"]] = prepared_dict["prefetched_thumbnail"]

                    self.id_to_prepared_dict[prepared_dict["id"]] = prepared_dict

                    # Passing the dictionary for easier access to attributes.
                    copy_response.meta["item"] = prepared_dict

                    if self.hasChanged(copy_response):
                        yield self.handleEntry(copy_response)

                    # Has to be called for every individual instance that needs to be saved to the database.
                    LomBase.parse(self, copy_response)
                except Exception as e:
                    logging.info("Issues with the element: " + (str(prepared_dict["id"]) if "id" in prepared_dict else ""))
                    logging.info(e)

        # If "more" in response, continue paginating.
        if "more" in root.attrib and root.attrib["more"] == "more":
            self.execution_per_state_county_list[self.state_county_counter]["page"] += 1

        # Else if more states/counties are available, proceed with them.
        elif self.state_county_counter + 1 < len(self.execution_per_state_county_list):
            self.state_county_counter += 1

        # Finally, if none of the former options are true, stop the execution of this spider by not yielding further
        #   requests!
        else:
            return

        yield self._proxify_request(scrapy.Request(
            url=self.apiUrl
                .replace("%state", self.execution_per_state_county_list[self.state_county_counter]["state"])
                .replace("%county", self.execution_per_state_county_list[self.state_county_counter]["county"]),
            body=self.dataForm
                .replace("%start", str(self.execution_per_state_county_list[self.state_county_counter]["page"] * self.limit))
                .replace("%count", str(self.limit - 1)),
            callback=self.parse,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
            encoding='utf-8')
        )

    def prepare_element(self, element_dict, antares_code_to_value_mapping):
        prepared_dict = dict()

        # Add the content's ID, which is an attribute of the <r> XML element.
        prepared_dict["id"] = element_dict["r"]["@identifier"]

        # Add the content's fields, which are children of the <f> XML element.
        for field_dict in element_dict["r"]["f"]:
            if len(field_dict) > 1:
                # @n denotes the attribute's name and #text its value.
                prepared_dict[field_dict["@n"]] = field_dict["#text"]

        # Decode fields from ["adressat", "geb", "typ"] the Antares value encoding.
        for field in ["adressat", "geb", "typ"]:
            if field in prepared_dict:
                prepared_dict[field] = self.decode_antares_field(field, prepared_dict[field], antares_code_to_value_mapping)

        # Get content's URLs using the notch process. * currently not used *
        # content_urls_dict = self._execute_get_url_via_notch(prepared_dict["id"])
        # prepared_dict["size"] = content_urls_dict["size"]
        # prepared_dict["download_url"] = content_urls_dict["download"]
        # prepared_dict["direct_url"] = content_urls_dict["direct"]

        # Fake URL, to make sure that the nodes get different IDs and to remind ourselves that the final URL is
        #   generated at the SchulCloud side.
        prepared_dict["direct_url"] = "URL_dynamically_generated_at_client_side/" + prepared_dict["id"]

        # If this item was met again in some other state/county, please take into account any extra information.

        state = self.execution_per_state_county_list[self.state_county_counter]["state"]
        county = self.execution_per_state_county_list[self.state_county_counter]["county"]

        prepared_dict["states_counties"] = [(state, county)]
        if prepared_dict["id"] in self.id_to_prepared_dict:
            prepared_dict_former = self.id_to_prepared_dict[prepared_dict["id"]]

            # a: Get the total states and counties met.
            prepared_dict["states_counties"].extend(prepared_dict_former["states_counties"])

            logging.info("Added extra states_counties: " + str(prepared_dict["states_counties"]))

            # b: Get any thumbnail information already acquired.
            prepared_dict["prefetched_thumbnail"] = prepared_dict_former["prefetched_thumbnail"]
        else:
            # Alternatively, we may have just met the thumbnail URL in the past. In this case, we should re-use it.
            content_url = prepared_dict.get("mmdatei", None)

            if content_url is not None and content_url in self.thumbnail_cache:
                prepared_dict["prefetched_thumbnail"] = self.thumbnail_cache[prepared_dict["mmdatei"]]
                logging.debug("Thumbnail URL " + content_url + " has been already requested.")

        return prepared_dict

    def getId(self, response):
        element_dict = dict(response.meta["item"])  # Element response as a Python dict.
        return element_dict["id"]

    def getHash(self, response):
        """ Since we have no 'last_modified' date from the elements we cannot do something better.
            Therefore, the current implementation takes into account (1) the code version and (2) the item's ID. """
        return (
            hash(self.version)
            + hash(self.getId(response))
        )

    def mapResponse(self, response):
        r = ResponseItemLoader(response=response)
        r.add_value("status", response.status)
        r.add_value("headers", response.headers)
        r.add_value("url", self.getUri(response))
        return r

    def handleEntry(self, response):
        return LomBase.parse(self, response)

    def getBase(self, response):
        base = LomBase.getBase(self, response)

        element_dict = dict(response.meta["item"])  # Element response as a Python dict.

        # base.add_value("thumbnail", element_dict.get("mmdatei", ""))  # get or default
        base.add_value("thumbnail", element_dict["prefetched_thumbnail"])

        return base

    def getLOMGeneral(self, response):
        general = LomBase.getLOMGeneral(self, response)

        element_dict = dict(response.meta["item"])  # Element response as a Python dict.

        general.add_value("title", element_dict["titel"])
        # TODO consider --> general.add_value("title", element_dict["sertitel"] + " - " + element_dict["titel"])

        general.add_value("description", element_dict["text"])

        return general

    def getUri(self, response=None) -> str:
        element_dict = dict(response.meta["item"])  # Element response as a Python dict.

        return element_dict["direct_url"]

    def getLicense(self, response=None) -> LicenseItemLoader:
        license = LomBase.getLicense(self, response)

        license.replace_value('internal', Constants.LICENSE_NONPUBLIC)  # private

        return license

    def getLOMTechnical(self, response=None) -> LomTechnicalItemLoader:
        technical = LomBase.getLOMTechnical(self, response)

        technical.add_value("format", "text/html")
        technical.add_value("location", self.getUri(response))
        technical.add_value("size", len(response.body))

        return technical

    def getValuespaces(self, response):
        valuespaces = LomBase.getValuespaces(self, response)

        element_dict = response.meta["item"]  # Element response as a Python dict.

        if "adressat" in element_dict:
            valuespaces.add_value("intendedEndUserRole", element_dict["adressat"])
        if "geb" in element_dict:
            valuespaces.add_value("discipline", element_dict["geb"])
        if "typ" in element_dict:
            valuespaces.add_value("learningResourceType", element_dict["typ"])

        return valuespaces

    def getPermissions(self, response=None) -> PermissionItemLoader:
        """
        In case license information, in the form of state (Lands) and counties (Kreis) codes, is available. This changes
        the permissions according to the groups. For more information regarding the available county codes please
        consult relevant state edupool instances.
        """

        permissions = LomBase.getPermissions(self, response)

        permissions.replace_value("public", False)
        permissions.add_value("autoCreateGroups", True)

        element_dict = response.meta["item"]  # Element response as a Python dict.

        # TODO: Translate state and county to their DISPLAYNAME? Slight preprocessing on the values might help.
        states_counties = element_dict["states_counties"]

        groups = set()

        for (state, county) in states_counties:
            # TODO: In Merlin it's called LowerSaxony, here you just use the abbreviation.
            groups.add(state + "-private")
            groups.add("antares_" + state + "_" + county)

        permissions.add_value("groups", sorted(list(groups)))

        return permissions

    def read_antares_code_mapping(self):
        """
        Read value encodings. The values follow the following format:
        englisch	20001
        naturwissenschaften	320 380 460 080 100 <--- (multiple values are provided with a simple white space in-between)
        ..., etc.

        """

        filename = "antares_value_encoding.csv"
        filepath = str(get_project_root()) + "/schulcloud/resources/" + filename
        if not os.path.exists(filepath):
            logging.error(
                "Please provide the antares value encoding file (" + filename + ") in the directory /schulcloud/resources"
            )
            exit(-1)

        antares_code_to_value_mapping = {}
        with open(filepath, "rt") as fin:
            lines = fin.readlines()
            for line in lines[1:]:  # First line contains header.
                key, codes_str = line.replace("\n", "").replace("\"", "").replace("\'", "").split(",")
                codes = codes_str.split(" ")
                for code in codes:
                    antares_code_to_value_mapping[code] = key

        return antares_code_to_value_mapping

    def read_antares_states_counties(self) -> list:
        """
        * WARNING: Please provide this file locally before starting the execution of this spider! *

        Read state-county mapping. This file includes the states and counties that should be crawled (/harvested).
        The values follow the following format:

        Land abbreviation, Land, KFZ KZ, Kreis
        (in English: state_abbreviation  state    county_abbreviation    county)
        MML Mustermanland   MMC Mustermancounty
        BSL Bobsmithland   BSC Bobsmithcounty
        ..., etc.

        Example available also in /schulcloud/resources

        """
        filename = "antares_state_kreis_harvestable_list.csv"
        filepath = str(get_project_root()) + "/schulcloud/resources/" + filename
        if not os.path.exists(filepath):
            logging.error("Please provide the antares state-county list file ("+filename+") in the directory "
                                                                                         "/schulcloud/resources")
            exit(-1)
        df = pd.read_csv(filepath, sep=",")
        df.dropna(inplace=True)
        records = df.to_dict('records')
        return records


    def decode_antares_field(self, field, current_value, antares_code_to_value_mapping):
        """
        Converts antares OEF codes as described in the provided documentation ARIX_1_4.docx. Further resources available
        in the:
            1. German LOM standard http://sodis.de/lom-de/LOM-DE.doc
            2. https://wiki.dnb.de/display/DINIAGKIM/OER-Metadatengruppe
            3. https://dini-ag-kim.github.io/hs-oer-lom-profil/latest/.
            4. http://agmud.de/eaf-erweitertes-austauschformat/   file: eafmed.txt

        TODO: Needs further refinement for special data preparation of ranges in adressat, as well as for geb and typ.
        """
        decoded_values = set()

        if field == "adressat":
            context_values = []

            # Convert "ab Klasse X" to AX, AX+1, ..., A13 (which is the maximum value)
            if current_value.startswith("ab Klasse "):
                starting_class = int(current_value.replace("ab Klasse ", "").strip())
                for edu_class in range(starting_class, 13+1):
                    context_values.append("A" + str(edu_class))
            else:
                # Convert A(value1-value2) --> ["value1", "value2"]
                edu_range = current_value[2:-1].split("-")
                # Convert range to separate values
                context_values = ["A" + str(x) for x in range(int(edu_range[0].strip()), int(edu_range[1].strip())+1)]

            for v in context_values:
                decoded_values.add(antares_code_to_value_mapping[v])
        elif field == "geb" or field == "typ":
            for v in current_value.split(","):
                v = v.strip().lstrip("0")  # Remove redundant white-space and zero padding from the left. E.g., 060->60
                if v not in antares_code_to_value_mapping:
                    logging.warning("Wrong Antares encoding value \"" + v + "\" for attribute " + field)
                else:
                    decoded_values.add(antares_code_to_value_mapping[v])
        else:
            logging.error("Wrong field passed to method \"decode_antares_field\"")

        return sorted(list(decoded_values))

    def _request_thumbnail(self, prepared_dict, response):
        response.meta["item"] = prepared_dict
        lom_technical = self.getLOMTechnical(response)

        url = None
        if "mmdatei" in prepared_dict:
            url = prepared_dict["mmdatei"]

        ptp = ProcessThumbnailPipeline()
        item = {}
        if url is not None:
            item["thumbnail"] = url
        item["lom"] = {"technical": lom_technical}
        return ptp._get_thumbnail(item)


    # def _execute_get_url_via_notch(self, content_id: str, state: str, county: str) -> dict:
    #     """
    #     * We do not currently need this method during crawling/harvesting. It is handled in the SchulCloud side,
    #     as the URLs are temporary. *
    #
    #     Using the steps described here we can obtain access to the content element's file. Briefly the followed steps
    #     include:
    #     (a) Use the content's ID to obtain the encoded content's ID and the notch.
    #     (b) Using the obtained notch and your private shared secret calculate MD5 of passphrase (variable notch_secret).
    #     """
    #     url = "https://arix.datenbank-bildungsmedien.net/" + state + "/" + county
    #     headers = {"Content-Type": "application/x-www-form-urlencoded"}
    #
    #     # Step 1: Get the notch.
    #     body = "xmlstatement=<notch identifier='" + content_id + "'/>"
    #     x = requests.post(url=url, data=body, headers=headers)
    #     x_dict = xmltodict.parse(x.text)
    #
    #     encoded_content_id = x_dict["notch"]["@id"]
    #     notch = x_dict["notch"]["#text"]
    #
    #     # Step 2: Calculate passphrase
    #     settings = get_project_settings()
    #     shared_secret = settings.get("ANTARES_SHARED_SECRET", settings.get("ANTARES_SHARED_SECRET"))
    #     notch_secret = notch + ':' + shared_secret  # a. Concatenate notch with shared secret.
    #     notch_secret_bytes = notch_secret.encode()  # b. Encode to bytes.
    #     md5_representation = hashlib.md5(notch_secret_bytes)  # c. Calculate md5 representation.
    #     md5_hex = md5_representation.hexdigest()  # d. Get Hexadecimal representation.
    #
    #     # Step 3: Request URLs using the MD5 Hexadecimal representation.
    #     body_with_encoded_values = "xmlstatement=<link id='" + encoded_content_id + "'>" + md5_hex + "</link>"
    #     x_of_encoded_values = requests.post(url=url, data=body_with_encoded_values, headers=headers)
    #     x_dict_of_encoded_values = xmltodict.parse(x_of_encoded_values.text)
    #
    #     # Step 4: Gather the returned information.
    #     content_dict = {}
    #     content_dict["size"] = x_dict_of_encoded_values["link"]["@size"]
    #     content_dict[x_dict_of_encoded_values["link"]["a"][0]["#text"]] = x_dict_of_encoded_values["link"]["a"][0][
    #         "@href"]
    #     content_dict[x_dict_of_encoded_values["link"]["a"][1]["#text"]] = x_dict_of_encoded_values["link"]["a"][1][
    #         "@href"]
    #
    #     return content_dict


