import os

import pandas as pd
from requests.auth import HTTPBasicAuth
import requests
import time
import json
import logging

from scrapy.utils.project import get_project_settings

from schulcloud.users_groups import get_project_root


class UserGroupCreator:
    """
    This script creates users and groups, whilst associating users to the right groups as well.
    """

    # Describes the users, groups, and their relations, i.e., which user belongs to which group.
    filepath_relations = str(get_project_root()) + "/schulcloud/users_groups/user_group_mapping_edusharing.xlsx"

    # Describes the users and their passwords.
    filepath_passwords = str(get_project_root()) + "/schulcloud/users_groups/.users_passwords_edusharing.xlsx"

    jsessionid = None
    jsessionid_last_update = None

    def execute(self):
        """
        This method creates users and groups and associates the former to the latter using the list provided in the
        user_group_mapping.xls.
        """

        # First, we read the data. TODO: If files are not available locally fetch them from 1Password.
        #  (credentials should exist in .env)
        df_passwords = self._read_excel(self.filepath_passwords)
        df_relations = self._read_excel(self.filepath_relations)

        # Second, we create users. TODO: if the user exists, update the password. Then we need the old password.
        #   List of items: userX
        users = sorted(list(df_passwords["username"].dropna().unique()))
        #   List of items: (userN, passwordN)
        users_passwords = sorted([tuple(x) for x in df_passwords[["username", "password"]].dropna().to_numpy()])
        self.process_users(users, users_passwords)

        # Third, we create groups. TODO: if the group exists, just add the additional users or delete previous users?.
        #   List of items: groupX
        groups = list(df_relations["merlin edu-sharing group"].dropna().unique())
        groups.extend(list(df_relations["antares edu-sharing group"].dropna().unique()))
        groups.sort()
        self.process_groups(groups)

        # Fourth, we associate the users with their corresponding groups. TODO: user to groups dictionary
        #   List of items: (userX, groupY). A user can be associated with multiple groups and vice versa.
        users_groups = [tuple(x) for x in df_relations[["username", "merlin edu-sharing group"]].dropna().to_numpy()]
        users_groups.extend([tuple(x) for x in df_relations[["username", "antares edu-sharing group"]].dropna().to_numpy()])
        self.process_user_group_relations(users_groups)

    @staticmethod
    def _read_excel(filepath):
        if not os.path.exists(filepath):
            logging.error(filepath + " is not available. Please request the latest up-to-date file. Exiting.")
            exit(-1)
        table = pd.read_excel(filepath, 0)
        cols = table.columns
        conv = dict(zip(cols, [str] * len(cols)))  # List of items: (columnX, str)
        return pd.read_excel(filepath, 0, converters=conv)

    def process_users(self, users, users_passwords):
        # 1. Create them.
        for user in users:
            if not self._user_exists(user):
                self._create_user(user)
        # 2. Add passwords.
        for user, password in users_passwords:
            self._modify_password(user, None, password)

    def _create_user(self, user):
        self.process_authentication()

        url = get_project_settings().get("EDU_SHARING_BASE_URL") + "rest/iam/v1/people/-home-/" + user

        data = {
            "primaryAffiliation": "function",
            "sizeQuota": 1047527424,
            "firstName": user,
            "lastName": user,
            "email": user + "@hpi.de",
            "avatar": "",
            "about": ""
        }
        x = requests.post(url, headers=self._get_standard_headers(), data=json.dumps(data, indent=4),
                          cookies=self._get_standard_cookies())

        if x.status_code == 200:
            logging.info("User " + user + " has been created successfully.")

    def _user_exists(self, user):
        self.process_authentication()

        url = get_project_settings().get("EDU_SHARING_BASE_URL") + "rest/iam/v1/people/-home-/" + user

        x = requests.get(url, headers=self._get_standard_headers(), cookies=self._get_standard_cookies())

        return True if x.status_code == 200 else False

    def _modify_password(self, user, old_password, new_password):
        """
        As long as the password is the same there is no problem in re-setting it.
        """

        self.process_authentication()

        url = get_project_settings().get("EDU_SHARING_BASE_URL") + "rest/iam/v1/people/-home-/" + user + "/credential"

        data = {"newPassword": new_password}
        if old_password is not None:
            data["oldPassword"] = old_password

        x = requests.put(url, headers=self._get_standard_headers(), data=json.dumps(data, indent=4),
                         cookies=self._get_standard_cookies())

        if x.status_code == 200:
            logging.info("User's " + user + " password has been set/modified successfully.")

    def process_groups(self, groups):
        for group in groups:
            if not self._group_exists(group):
                self._create_group(group)

    def _create_group(self, group):
        self.process_authentication()

        url = get_project_settings().get("EDU_SHARING_BASE_URL") + "rest/iam/v1/groups/-home-/" + group

        data = {
            "groupEmail": group + "@hpi.de",
            "displayName": group
        }

        x = requests.post(url, headers=self._get_standard_headers(), data=json.dumps(data, indent=4),
                          cookies=self._get_standard_cookies())

        if x.status_code == 200:
            logging.info("Group " + group + " has been created successfully.")

    def _group_exists(self, group):
        self.process_authentication()

        url = get_project_settings().get("EDU_SHARING_BASE_URL") + "rest/iam/v1/groups/-home-/" + group

        x = requests.get(url, headers=self._get_standard_headers(), cookies=self._get_standard_cookies())

        return True if x.status_code == 200 else False

    def process_user_group_relations(self, users_groups):
        # Add users to group.
        for user, group in users_groups:
            self._add_user_to_group(user, group)

    def _add_user_to_group(self, user, group):
        self.process_authentication()

        url = get_project_settings().get("EDU_SHARING_BASE_URL") + "rest/iam/v1/groups/-home-/" + group + "/members/" + user

        x = requests.put(url, headers=self._get_standard_headers(), cookies=self._get_standard_cookies())

        if x.status_code == 200:
            logging.info("User " + user + " has been added successfully to group " + group + ".")

    def process_authentication(self):
        # First call
        if self.jsessionid is None or \
                (self.jsessionid_last_update is not None and
                 self.jsessionid_last_update - time.time() >= 3600):  # or it has expired

            self.jsessionid_last_update = time.time()

            # Step 1. Check if you are authenticated.
            ses = requests.session()
            response = ses.get(get_project_settings().get("EDU_SHARING_BASE_URL") +
                               'rest/authentication/v1/validateSession',
                               auth=HTTPBasicAuth('admin', 'admin'),
                               headers={
                                   "Accept": "application/json"
                               }
                               )
            self.jsessionid = ses.cookies['JSESSIONID']

    @staticmethod
    def _get_standard_headers():
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _get_standard_cookies(self):
        return {"JSESSIONID": self.jsessionid}


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    ugc = UserGroupCreator()
    ugc.execute()

    # ugc._create_user("test_user_1")
    # ugc._modify_password("test_user_1", None, "new_password")
    # ugc._create_group("test_group_1")
    # ugc._add_user_to_group("test_user_1", "test_group_1")
