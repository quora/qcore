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

all: test

install: clean
	python setup.py sdist
	pip install --upgrade dist/qcore*.gz

install64: clean
	python64 setup.py sdist
	pip64 install --upgrade dist/qcore*.gz

clean:
	rm -rf dist/
	rm -f qcore/*.so
	rm -f qcore/*.c

test:
	python setup.py build_ext --inplace
	mv *.so qcore/
	python -m nose
