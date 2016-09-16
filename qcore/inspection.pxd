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


cpdef object get_original_fn(object fn)

@cython.locals(_full_name_=str)
cpdef str get_full_name(object src)

@cython.locals(result=str, first=bint)
cpdef str get_function_call_str(fn, tuple args, dict kwargs)
@cython.locals(result=str, first=bint)
cpdef str get_function_call_repr(fn, tuple args, dict kwargs)

cpdef object getargspec(object func)

cpdef bint is_cython_or_generator(object fn) except -1
@cython.locals(name=str)
cpdef bint is_cython_function(object fn) except -1

cpdef bint is_cython_class(object cls) except -1

cpdef bint is_classmethod(object fn) except -1

cpdef wraps(object wrapped, object assigned=?, object updated=?)
