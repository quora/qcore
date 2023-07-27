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

from setuptools import setup
from setuptools.extension import Extension

import glob
import os.path


CYTHON_MODULES = [
    "helpers",
    "microtime",
    "events",
    "decorators",
    "caching",
    "inspection",
]


DATA_FILES = (
    ["py.typed"]
    + ["%s.pxd" % module for module in CYTHON_MODULES]
    + [os.path.relpath(f, "qcore/") for f in glob.glob("qcore/*.pyi")]
)


VERSION = "1.10.0"


EXTENSIONS = [
    Extension("qcore.%s" % module, ["qcore/%s.py" % module])
    for module in CYTHON_MODULES
]


if __name__ == "__main__":
    for extension in EXTENSIONS:
        extension.cython_directives = {"language_level": "3"}

    with open("./README.rst", encoding="utf-8") as f:
        long_description = f.read()

    setup(
        name="qcore",
        version=VERSION,
        author="Quora, Inc.",
        author_email="asynq@quora.com",
        description="Quora's core utility library",
        long_description=long_description,
        long_description_content_type="text/x-rst",
        url="https://github.com/quora/qcore",
        license="Apache Software License",
        classifiers=[
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
        ],
        keywords="quora core common utility",
        packages=["qcore", "qcore.tests"],
        package_data={"qcore": DATA_FILES},
        ext_modules=EXTENSIONS,
        setup_requires=["Cython"],
    )
