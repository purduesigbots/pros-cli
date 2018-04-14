try {
   if(get-command python36) { Write-Information "found python36" }
   else {
    Write-Error "Couldn't find python36. Make sure it's installed and available from PATH"
    exit 1
   }
} catch {
    Write-Error "Couldn't find python36. Make sure it's installed and available from PATH"
    exit 1
}

python36 -m pip install --upgrade vex

Write-Information "Done installing build dependencies"
Write-Information "You should now be able to build the cli using 'python36 -m vex -mr foo ./scripts/build.bat'"
