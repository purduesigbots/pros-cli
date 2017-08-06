echo Installing wheel and cx_Freeze
pip3 install wheel cx_Freeze

echo Updating version
python3 version.py

echo Installing pros-cli requirements
pip3 install --upgrade -r requirements.txt

echo Building wheel
python3 setup.py bdist_wheel

echo Bulding binary
python3 build.py build_exe

echo Moving artifacts to ./out
New-Item ./out -ItemType directory
Remove-Item ./out/* -Recurse
Copy-Item dist\pros_cli*.whl .\out
Copy-Item .\pros_cli*.zip .\out

