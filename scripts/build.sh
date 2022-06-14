#!/bin/bash

python=python
echo Testing python executable version
$python -c "import sys; exit(0 if sys.version_info > (3,6) else 1)"
if [ $? -ne 0 ]
then
    python=python3.6
fi
pipinstall="pip install --user"
echo Upgrading pip
$python -m $pipinstall --upgrade pip

# echo Installing wheel and cx_Freeze
# $python -m $pipinstall wheel cx_Freeze

echo Installing wheel and pyinstaller
$python -m $pipinstall wheel pyinstaller

echo Updating version
$python version.py

echo Installing pros-cli requirements
$python -m $pipinstall --upgrade -r requirements.txt

echo Building Wheel
$python setup.py bdist_wheel

echo Building Binary
pyinstaller --target-arch universal2 pros/cli/main.py
pyinstaller --target-arch universal2 --onefile pros/cli/compile_commands/intercept-cc.py


echo Moving artifacts to ./out
mkdir -p ./out
rm -rf ./out/*
cp dist/pros_cli*.whl out
cp pros_cli*.zip out
