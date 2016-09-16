# Copyright 2016 Quora, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__doc__ = """

Provides a base class overriding some useful dunder methods.

"""


class InspectableClass(object):
    """Class that provides commonly useful dunder methods.

    This creates a useful repr/str representation, implements equality checking, and provides
    hashing.

    """
    _excluded_attributes = set()  # these are not used in equality checking and repr

    def _filtered_dict(self):
        excluded = self._excluded_attributes
        return sorted(
            ((k, v) for k, v in self.__dict__.items() if k not in excluded),
            key=lambda pair: pair[0]
        )

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join(
                '%s=%r' % pair
                for pair in self._filtered_dict()
            )
        )

    def __str__(self):
        return repr(self)

    def __hash__(self):
        return hash(tuple(self._filtered_dict()))

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self._filtered_dict() == other._filtered_dict()

    def __ne__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self._filtered_dict() != other._filtered_dict()
