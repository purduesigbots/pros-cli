@echo off

echo Installing wheel and cx_Freeze
pip install wheel cx_Freeze

echo Updating version
python version.py

echo Installing pros-cli requirements
pip install --upgrade -r requirements.txt

echo Building Wheel
python setup.py bdist_wheel

echo Building Binary
python build.py build_exe

echo Moving artifacts to ./out
mkdir -p ./out
rm -rf ./out/*
cp dist/pros_cli*.whl out
cp pros_cli*.zip out
