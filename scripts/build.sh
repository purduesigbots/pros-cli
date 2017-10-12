#!/bin/bash

python=python
echo Testing python executable version
python -c "import sys; exit(0 if sys.version_info > (3,5) else 1)"
if [ $? -ne 0 ]
then
    python=python3
fi

echo Installing wheel and cx_Freeze
pip3 install wheel cx_Freeze

echo Updating version
$python version.py

echo Installing pros-cli requirements
pip3 install --upgrade -r requirements.txt

echo Building Wheel
$python setup.py bdist_wheel

echo Building Binary
$python build.py build_exe

echo Moving artifacts to ./out
mkdir -p ./out
rm -rf ./out/*
cp dist/pros_cli*.whl out
cp pros_cli*.zip out
