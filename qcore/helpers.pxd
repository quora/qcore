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


cdef list empty_list
cdef tuple empty_tuple
cdef dict empty_dict


cdef class MarkerObject:
    cdef unicode name

cdef MarkerObject none
cdef MarkerObject miss
cdef MarkerObject same
cdef MarkerObject unspecified


cdef class EmptyContext:
    cpdef __enter__(self)
    cpdef __exit__(self, exc_type, exc_val, exc_tb)

cdef EmptyContext empty_context


cdef class CythonCachedHashWrapper:
    cdef object _value
    cdef int _hash

    cpdef object value(self)
    cpdef object hash(self)

cdef object CachedHashWrapper


cdef class _ScopedValueOverrideContext(object)  # Forward declaration

cdef class ScopedValue:
    cdef object _value

    cpdef object get(self)
    cpdef set(self, object value)
    cpdef object override(self, object value)

cdef class _ScopedValueOverrideContext:
    cdef ScopedValue _target
    cdef object _value
    cdef object _old_value


cdef class _PropertyOverrideContext:
    cdef object _target
    cdef object _property_name
    cdef object _value
    cdef object _old_value

cdef object override  # Alias of PropertyOverrideContext


cpdef object ellipsis(object source, int max_length)
cpdef object safe_str(object source, int max_length=?)
cpdef object safe_repr(object source, int max_length=?)


cpdef dict_to_object(dict source)
