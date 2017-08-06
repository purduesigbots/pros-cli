try {
   if(get-command pip3) { echo "found pip3" }
   else {
    echo "Couldn't find pip3. Make sure it's installed and available from PATH"
    exit 1
   }
} catch {
    echo "Couldn't find pip3. Make sure it's installed and available from PATH"
    exit 1
}

pip3 install vex

echo "Done installing build dependencies"
echo "You should now be able to build the cli using 'vex -mr foo ./scripts/build.bat'"

