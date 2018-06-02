$root = $MyInvocation.MyCommand.Definition | Split-Path -Parent | Split-Path -Parent
if(Test-Path -Path $root\out) {
    Remove-Item -Recurse -Force -Path $root\out
}
