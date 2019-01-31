#!/bin/bash

python=python
echo Testing python executable version
$python -c "import sys; exit(0 if sys.version_info > (3,6) else 1)"
if [ $? -ne 0 ]
then
    python=python3.6
fi

echo Upgrading pip
$python -m pip install --upgrade pip

echo Installing wheel and cx_Freeze
$python -m pip install wheel cx_Freeze

echo Updating version
$python version.py

echo Installing pros-cli requirements
$python -m pip install --upgrade -r requirements.txt

echo Building Wheel
$python setup.py bdist_wheel

echo Building Binary
$python build.py build_exe

echo Moving artifacts to ./out
mkdir -p ./out
rm -rf ./out/*
cp dist/pros_cli*.whl out
cp pros_cli*.zip out
