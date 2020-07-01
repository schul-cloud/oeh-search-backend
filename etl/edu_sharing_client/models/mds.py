# coding: utf-8

"""
    edu-sharing Repository REST API

    The public restful API of the edu-sharing repository.  # noqa: E501

    OpenAPI spec version: 1.1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class Mds(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'types': 'list[MdsType]',
        'ref': 'MdsRef',
        'forms': 'list[MdsForm]',
        'lists': 'list[MdsList]',
        'views': 'list[MdsView]',
        'queries': 'MdsQueries'
    }

    attribute_map = {
        'types': 'types',
        'ref': 'ref',
        'forms': 'forms',
        'lists': 'lists',
        'views': 'views',
        'queries': 'queries'
    }

    def __init__(self, types=None, ref=None, forms=None, lists=None, views=None, queries=None):  # noqa: E501
        """Mds - a model defined in Swagger"""  # noqa: E501

        self._types = None
        self._ref = None
        self._forms = None
        self._lists = None
        self._views = None
        self._queries = None
        self.discriminator = None

        self.types = types
        self.ref = ref
        self.forms = forms
        self.lists = lists
        self.views = views
        self.queries = queries

    @property
    def types(self):
        """Gets the types of this Mds.  # noqa: E501


        :return: The types of this Mds.  # noqa: E501
        :rtype: list[MdsType]
        """
        return self._types

    @types.setter
    def types(self, types):
        """Sets the types of this Mds.


        :param types: The types of this Mds.  # noqa: E501
        :type: list[MdsType]
        """
        if types is None:
            raise ValueError("Invalid value for `types`, must not be `None`")  # noqa: E501

        self._types = types

    @property
    def ref(self):
        """Gets the ref of this Mds.  # noqa: E501


        :return: The ref of this Mds.  # noqa: E501
        :rtype: MdsRef
        """
        return self._ref

    @ref.setter
    def ref(self, ref):
        """Sets the ref of this Mds.


        :param ref: The ref of this Mds.  # noqa: E501
        :type: MdsRef
        """
        if ref is None:
            raise ValueError("Invalid value for `ref`, must not be `None`")  # noqa: E501

        self._ref = ref

    @property
    def forms(self):
        """Gets the forms of this Mds.  # noqa: E501


        :return: The forms of this Mds.  # noqa: E501
        :rtype: list[MdsForm]
        """
        return self._forms

    @forms.setter
    def forms(self, forms):
        """Sets the forms of this Mds.


        :param forms: The forms of this Mds.  # noqa: E501
        :type: list[MdsForm]
        """
        if forms is None:
            raise ValueError("Invalid value for `forms`, must not be `None`")  # noqa: E501

        self._forms = forms

    @property
    def lists(self):
        """Gets the lists of this Mds.  # noqa: E501


        :return: The lists of this Mds.  # noqa: E501
        :rtype: list[MdsList]
        """
        return self._lists

    @lists.setter
    def lists(self, lists):
        """Sets the lists of this Mds.


        :param lists: The lists of this Mds.  # noqa: E501
        :type: list[MdsList]
        """
        if lists is None:
            raise ValueError("Invalid value for `lists`, must not be `None`")  # noqa: E501

        self._lists = lists

    @property
    def views(self):
        """Gets the views of this Mds.  # noqa: E501


        :return: The views of this Mds.  # noqa: E501
        :rtype: list[MdsView]
        """
        return self._views

    @views.setter
    def views(self, views):
        """Sets the views of this Mds.


        :param views: The views of this Mds.  # noqa: E501
        :type: list[MdsView]
        """
        if views is None:
            raise ValueError("Invalid value for `views`, must not be `None`")  # noqa: E501

        self._views = views

    @property
    def queries(self):
        """Gets the queries of this Mds.  # noqa: E501


        :return: The queries of this Mds.  # noqa: E501
        :rtype: MdsQueries
        """
        return self._queries

    @queries.setter
    def queries(self, queries):
        """Sets the queries of this Mds.


        :param queries: The queries of this Mds.  # noqa: E501
        :type: MdsQueries
        """
        if queries is None:
            raise ValueError("Invalid value for `queries`, must not be `None`")  # noqa: E501

        self._queries = queries

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(Mds, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Mds):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other