echo =============== INSTALLING PYTHON3 ===============

sudo apt-get install -y python3.6 python3.6-dev libssl-dev

if [ $? -ne 0 ]
then
	echo apt install failed to run, maybe need root privileges?
	exit 1
fi

curl https://bootstrap.pypa.io/get-pip.py | sudo python3.6

if [ $? -ne 0 ]
then
    python3.6 -m pip
    if [ $? -ne 0 ]
    then
        echo get-pip install failed to install, maybe need root privileges?
        exit 1
    fi
fi

echo =============== DONE INSTALLING PYTHON3 ===============

echo =============== INSTALLING pip-vex ===============
python3.6 -m pip install --user vex

if [ $? -ne 0 ]
then
	echo failed to install vex
	exit 1
fi
echo =============== DONE INSTALLING vex ===============


echo BUILD DEPENDENCIES FINISHED INSTALLING
echo To build, you should now be able to use 'vex -mr foo ./scripts/build.sh'
