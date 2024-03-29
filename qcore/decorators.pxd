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


cdef class DecoratorBase:
    cdef public object fn
    cdef public object type

    cpdef str name(self)
    cpdef bint is_decorator(self) except -1

cdef class DecoratorBinder:
    cdef public DecoratorBase decorator
    cdef public object instance

    cpdef str name(self)
    cpdef bint is_decorator(self) except -1


cdef inline void _update_wrapper(object wrapper, object wrapped)
