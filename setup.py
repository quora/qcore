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

from setuptools import setup, find_packages
from setuptools.extension import Extension

import codecs
import os


CYTHON_MODULES = ['helpers', 'microtime', 'events', 'decorators', 'caching', 'inspection']


DATA_FILES = ['%s.pxd' % module for module in CYTHON_MODULES]


VERSION = '0.4.2'


EXTENSIONS = [
    Extension(
        'qcore.%s' % module,
        ['qcore/%s.py' % module]
    ) for module in CYTHON_MODULES
]


if __name__ == '__main__':
    with codecs.open('./README.rst', encoding='utf-8') as f:
        long_description = f.read()

    setup(
        name='qcore',
        version=VERSION,
        author='Quora, Inc.',
        author_email='asynq@quora.com',
        description='Quora\'s core utility library',
        long_description=long_description,
        url='https://github.com/quora/qcore',
        license='Apache Software License',
        classifiers=[
            'License :: OSI Approved :: Apache Software License',

            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],
        keywords='quora core common utility',
        packages=find_packages(),
        package_data={'qcore': DATA_FILES},
        ext_modules=EXTENSIONS,
        setup_requires=['Cython'],
        install_requires=['Cython', 'inspect2', 'setuptools', 'six'],
    )
