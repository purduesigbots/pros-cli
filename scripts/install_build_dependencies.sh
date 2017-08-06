echo =============== INSTALLING PYTHON3 ===============

sudo apt-get install -y python3 python3-dev python3-pip libssl-dev

if [ $? -ne 0 ]
then
	echo apt install failed to run, maybe need root privileges?
	exit 1
fi

echo =============== DONE INSTALLING PYTHON3 ===============

echo =============== INSTALLING pip-vex ===============
sudo pip3 install vex

if [ $? -ne 0 ]
then
	echo failed to install vex
	exit 1
fi
echo =============== DONE INSTALLING vex ===============


echo BUILD DEPENDENCIES FINISHED INSTALLING
echo To build, you should now be able to use 'vex -mr foo ./scripts/build.sh'
