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

"""

Provides a metaclass that prevents inheritance from its instances.

"""


class DisallowInheritance(type):
    """Metaclass that disallows inheritance from classes using it."""

    def __init__(self, cl_name, bases, namespace):
        for cls in bases:
            if isinstance(cls, DisallowInheritance):
                message = (
                    "Class %s cannot be used as a base for newly defined class %s"
                    % (cls, cl_name)
                )
                raise TypeError(message)
        super().__init__(cl_name, bases, namespace)

    # Needed bcz of a six bug: https://github.com/benjaminp/six/issues/252
    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        return {}
