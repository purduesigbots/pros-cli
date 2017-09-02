$root = $MyInvocation.MyCommand.Definition | Split-Path -Parent | Split-Path -Parent

Set-Location $root
Write-Output "Installing wheel and cx_Freeze"
pip3 install wheel cx_Freeze

Write-Output "Updating version"
python3 version.py

Write-Output "Installing pros-cli requirements"
pip3 install --upgrade -r requirements.txt

Write-Output "Building wheel"
python3 setup.py bdist_wheel

Write-Output "Bulding binary"
python3 build.py build_exe

Write-Output "Moving artifacts to ./out"
Remove-Item -Recurse -Force -Path .\out
New-Item ./out -ItemType directory | Out-Null
Remove-Item .\out\* -Recurse
Copy-Item dist\pros_cli*.whl .\out
Copy-Item .\pros_cli*.zip .\out

Set-Location $root\out
python3 ../version.py
Set-Location $root
