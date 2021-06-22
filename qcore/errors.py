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

Common exception types.

"""

__all__ = [
    "ArgumentError",
    "OperationError",
    "NotSupportedError",
    "SecurityError",
    "PermissionError",
    "TimeoutError",
    "prepare_for_reraise",
    "reraise",
]

import sys


class ArgumentError(RuntimeError):
    """An error related to one of the provided arguments."""

    pass


class OperationError(RuntimeError):
    """Indicates the impossibility to perform the action."""

    pass


class NotSupportedError(OperationError):
    """An attempt to use an unsupported feature."""

    pass


class SecurityError(OperationError):
    """The action can't be performed due to security restrictions."""

    pass


class PermissionError(SecurityError):
    """The action can't be performed because of lack of required permissions."""

    pass


class TimeoutError(RuntimeError):
    """An error indicating that function was interrupted because of timeout."""

    pass


def prepare_for_reraise(error, exc_info=None):
    """Prepares the exception for re-raising with reraise method.

    This method attaches type and traceback info to the error object
    so that reraise can properly reraise it using this info.

    """
    if not hasattr(error, "_type_"):
        if exc_info is None:
            exc_info = sys.exc_info()
        error._type_ = exc_info[0]
        error._traceback = exc_info[2]
    return error


__traceback_hide__ = True


def reraise(error):
    """Re-raises the error that was processed by prepare_for_reraise earlier."""
    if hasattr(error, "_type_"):
        raise error.with_traceback(error._traceback)
    raise error
