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

import cython
from cpython cimport bool

from . cimport inspection
from .helpers cimport none, empty_tuple, empty_dict


cdef object _time_offset

cpdef inline object get_time_offset()
cpdef inline object set_time_offset(object offset)
cpdef inline object add_time_offset(object offset)

cdef class TimeOffset:
    cdef object offset


cpdef object utime()
cpdef object true_utime()

# NOTE: Can't cpdef this because of nested function.
#
# cpdef execute_with_timeout(fn, tuple args=?, dict kwargs=?, timeout=?,
#         bool fail_if_no_timer=?,
#         signal_type=?,
#         timer_type=?,
#         timeout_exception_cls=?)
