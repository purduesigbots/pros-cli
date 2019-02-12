$root = $MyInvocation.MyCommand.Definition | Split-Path -Parent | Split-Path -Parent

$python = 'python'
Write-Information 'Testing python executable version'
& $python -c "import sys; exit(0 if sys.version_info >= (3,6) else 1)"
if ( -not $? ) {
    $python='python36'
}

Set-Location $root
Write-Information "Upgrading pip"
& $python -m pip install --upgrade pip

Write-Information "Installing wheel and cx_Freeze"
& $python -m pip install wheel cx_Freeze

Write-Information "Updating version"
& $python version.py

Write-Information "Installing pros-cli requirements"
& $python -m pip install --upgrade -r requirements.txt

Write-Information "Building wheel"
& $python setup.py bdist_wheel

Write-Information "Bulding binary"
& $python build.py build_exe

Write-Information "Adding vcruntime140.dll to zip"
7z a $(Get-ChildItem -Name ".\pros_cli*.zip") C:\Windows\System32\vcruntime140.dll

Write-Information "Moving artifacts to ./out"

if (Test-Path .\out) { Remove-Item -Recurse -Force -Path .\out | Out-Null }
New-Item ./out -ItemType directory | Out-Null
Remove-Item .\out\* -Recurse | Out-Null

Copy-Item dist\pros_cli*.whl .\out
Copy-Item .\pros_cli*.zip .\out

Set-Location $root\out
& $python ../version.py
Set-Location $root
