$root = $MyInvocation.MyCommand.Definition | Split-Path -Parent | Split-Path -Parent

$python = python
Write-Output Testing python executable version
python -c "import sys; exit(0 if sys.version_info > (3,5) else 1)"
if ( -not $? ) {
    $python=python3
}

Set-Location $root
Write-Output "Installing wheel and cx_Freeze"
pip3 install wheel cx_Freeze

Write-Output "Updating version"
& $python version.py

Write-Output "Installing pros-cli requirements"
pip3 install --upgrade -r requirements.txt

Write-Output "Building wheel"
& $python setup.py bdist_wheel

Write-Output "Bulding binary"
& $python build.py build_exe

Write-Output "Moving artifacts to ./out"
Remove-Item -Recurse -Force -Path .\out
New-Item ./out -ItemType directory | Out-Null
Remove-Item .\out\* -Recurse
Copy-Item dist\pros_cli*.whl .\out
Copy-Item .\pros_cli*.zip .\out

Set-Location $root\out
& $python ../version.py
Set-Location $root
