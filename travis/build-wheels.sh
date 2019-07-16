#!/bin/bash
set -e -x

PYBIN=/opt/python/$PYVER/bin

"${PYBIN}/pip" install --upgrade setuptools  # work around https://github.com/pypa/setuptools/issues/1086

# Compile wheels
"${PYBIN}/pip" install -r /io/requirements.txt

# Install dependencies of qcore
"${PYBIN}/pip" install Cython tox 'typing; python_version < "3.5"'

"${PYBIN}/pip" wheel /io/ -w wheelhouse/

# Bundle external shared libraries into the wheels
for whl in wheelhouse/*-$PYVER-*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
done

# Copy plain wheels into the wheelhouse
for whl in wheelhouse/*-py2.py3-*.whl; do
    cp "$whl" /io/wheelhouse
done

# Install packages and test
"${PYBIN}/pip" install qcore --no-index -f /io/wheelhouse
(cd "$HOME"; "${PYBIN}/nosetests" qcore)

if [[ "$PYVER" =~ "^cp36-" ]]; then
    (cd "/io"; "${PYBIN}/mypy" qcore)
fi
