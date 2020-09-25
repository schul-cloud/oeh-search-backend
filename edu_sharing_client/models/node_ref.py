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


class NodeRef(object):
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
        'repo': 'str',
        'id': 'str',
        'archived': 'bool',
        'is_home_repo': 'bool'
    }

    attribute_map = {
        'repo': 'repo',
        'id': 'id',
        'archived': 'archived',
        'is_home_repo': 'isHomeRepo'
    }

    def __init__(self, repo=None, id=None, archived=False, is_home_repo=False):  # noqa: E501
        """NodeRef - a model defined in Swagger"""  # noqa: E501
        self._repo = None
        self._id = None
        self._archived = None
        self._is_home_repo = None
        self.discriminator = None
        self.repo = repo
        self.id = id
        self.archived = archived
        if is_home_repo is not None:
            self.is_home_repo = is_home_repo

    @property
    def repo(self):
        """Gets the repo of this NodeRef.  # noqa: E501


        :return: The repo of this NodeRef.  # noqa: E501
        :rtype: str
        """
        return self._repo

    @repo.setter
    def repo(self, repo):
        """Sets the repo of this NodeRef.


        :param repo: The repo of this NodeRef.  # noqa: E501
        :type: str
        """
        if repo is None:
            raise ValueError("Invalid value for `repo`, must not be `None`")  # noqa: E501

        self._repo = repo

    @property
    def id(self):
        """Gets the id of this NodeRef.  # noqa: E501


        :return: The id of this NodeRef.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this NodeRef.


        :param id: The id of this NodeRef.  # noqa: E501
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def archived(self):
        """Gets the archived of this NodeRef.  # noqa: E501


        :return: The archived of this NodeRef.  # noqa: E501
        :rtype: bool
        """
        return self._archived

    @archived.setter
    def archived(self, archived):
        """Sets the archived of this NodeRef.


        :param archived: The archived of this NodeRef.  # noqa: E501
        :type: bool
        """
        if archived is None:
            raise ValueError("Invalid value for `archived`, must not be `None`")  # noqa: E501

        self._archived = archived

    @property
    def is_home_repo(self):
        """Gets the is_home_repo of this NodeRef.  # noqa: E501


        :return: The is_home_repo of this NodeRef.  # noqa: E501
        :rtype: bool
        """
        return self._is_home_repo

    @is_home_repo.setter
    def is_home_repo(self, is_home_repo):
        """Sets the is_home_repo of this NodeRef.


        :param is_home_repo: The is_home_repo of this NodeRef.  # noqa: E501
        :type: bool
        """

        self._is_home_repo = is_home_repo

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
        if issubclass(NodeRef, dict):
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
        if not isinstance(other, NodeRef):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other