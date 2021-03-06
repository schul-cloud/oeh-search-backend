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


class Key(object):
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
        'first': 'object',
        'second': 'object',
        'name': 'str',
        'group': 'str'
    }

    attribute_map = {
        'first': 'first',
        'second': 'second',
        'name': 'name',
        'group': 'group'
    }

    def __init__(self, first=None, second=None, name=None, group=None):  # noqa: E501
        """Key - a model defined in Swagger"""  # noqa: E501
        self._first = None
        self._second = None
        self._name = None
        self._group = None
        self.discriminator = None
        if first is not None:
            self.first = first
        if second is not None:
            self.second = second
        if name is not None:
            self.name = name
        if group is not None:
            self.group = group

    @property
    def first(self):
        """Gets the first of this Key.  # noqa: E501


        :return: The first of this Key.  # noqa: E501
        :rtype: object
        """
        return self._first

    @first.setter
    def first(self, first):
        """Sets the first of this Key.


        :param first: The first of this Key.  # noqa: E501
        :type: object
        """

        self._first = first

    @property
    def second(self):
        """Gets the second of this Key.  # noqa: E501


        :return: The second of this Key.  # noqa: E501
        :rtype: object
        """
        return self._second

    @second.setter
    def second(self, second):
        """Sets the second of this Key.


        :param second: The second of this Key.  # noqa: E501
        :type: object
        """

        self._second = second

    @property
    def name(self):
        """Gets the name of this Key.  # noqa: E501


        :return: The name of this Key.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Key.


        :param name: The name of this Key.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def group(self):
        """Gets the group of this Key.  # noqa: E501


        :return: The group of this Key.  # noqa: E501
        :rtype: str
        """
        return self._group

    @group.setter
    def group(self, group):
        """Sets the group of this Key.


        :param group: The group of this Key.  # noqa: E501
        :type: str
        """

        self._group = group

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
        if issubclass(Key, dict):
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
        if not isinstance(other, Key):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
