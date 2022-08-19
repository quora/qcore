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

from . cimport helpers


cdef object miss
cdef object not_computed


cdef class LazyConstant:
    cdef public object value_provider
    cdef public object value

    cpdef get_value(self)
    cpdef compute(self)
    cpdef clear(self)


cdef class LRUCache:
    cdef int _capacity
    cdef object _item_evicted
    cdef object _dict

    cpdef get_capacity(self)
    cpdef get(self, key, default=?)
    cpdef clear(self, omit_item_evicted=?)

    cdef _evict_item(self, object key, object value)
    cdef inline _update_item(self, object key, object value)


@cython.locals(args_list=list, args_len=int, all_args_len=int, arg_name=str)
cpdef get_args_tuple(tuple args, dict kwargs, list arg_names, dict kwargs_defaults)
