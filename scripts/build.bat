@echo off

set root=%~dp0..

set python=python
echo Testing python executable version
python -c "import sys; exit(0 if sys.version_info > (3,5) else 1)"
if errorlevel 1 set python=python3

echo Installing wheel and cx_Freeze
git clone --branch 5.0.2 https://github.com/anthony-tuininga/cx_Freeze.git
pip3 install --upgrade cx_Freeze\.
pip3 install --upgrade wheel

echo Updating version
%python% %root%\version.py

echo Installing pros-cli requirements
pip3 install --upgrade -r %root%\requirements.txt

echo Building Wheel
%python% %root%\setup.py bdist_wheel

echo Building Binary
%python% %root%\build.py build_exe

echo Moving artifacts to .\out
if not exist %root%\out mkdir %root%\out
del /Q %root%\out\*.*
copy %root%\dist\pros_cli*.whl %root%\out\
copy %root%\pros_cli*.zip %root%\out\

cd out
%python% %root%\version.py
cd ..

