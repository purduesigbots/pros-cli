#!/bin/bash

echo Installing wheel and cx_Freeze
pip3 install wheel cx_Freeze

echo Updating version
python3 version.py

echo Installing pros-cli requirements
pip3 install --upgrade -r requirements.txt

echo Building Wheel
python3 setup.py bdist_wheel

echo Building Binary
python3 build.py build_exe

echo Moving artifacts to ./out
mkdir -p ./out
rm -rf ./out/*
cp dist/pros_cli*.whl out
cp pros_cli*.zip out
