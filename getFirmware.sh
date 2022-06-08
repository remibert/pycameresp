# ! bash
if [ -n "$PYCAMERESP_FIRMWARE" ]; then
	export ROOT=$PYCAMERESP_FIRMWARE
else
	export ROOT=`pwd`/firmware
fi

export ESPIDF=$ROOT/esp-idf

mkdir $ROOT
cd $ROOT

echo "*************"
echo "Install tools"
echo "*************"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
	sudo apt-get update                  --fix-missing -y
	sudo apt-get install git             --fix-missing -y
	sudo apt-get install wget            --fix-missing -y
	sudo apt-get install make            --fix-missing -y
	sudo apt-get install libncurses-dev  --fix-missing -y
	sudo apt-get install flex bison      --fix-missing -y
	sudo apt-get install gperf           --fix-missing -y
	sudo apt-get install scite           --fix-missing -y
	sudo apt-get install python3-pip     --fix-missing -y
	sudo apt-get install python3-tk      --fix-missing -y
	sudo apt-get install python3-venv    --fix-missing -y
	sudo apt-get install cmake           --fix-missing -y
	pip3 install pyqt6
	pip3 install pyinstaller
	pip3 install esptool
	pip3 install pyserial
	pip3 install requests
fi

echo "***************"
echo "Get Micropython"
echo "***************"
git clone https://github.com/micropython/micropython.git
cd $ROOT/micropython
git checkout a1afb337d2629a781cf4e171b7db7f05eeacc78f # Version greater than 1.18 OK

echo "*************************"
echo "Get micropython submodule"
echo "*************************"
cd ports/esp32
git submodule update --init --recursive
cd $ROOT

echo "*************"
echo "Get espressif"
echo "*************"
cd $ROOT
git clone -b v4.4.1 --recursive https://github.com/espressif/esp-idf.git

echo "****************"
echo "Get esp32 camera"
echo "****************"
cd $ROOT
git clone https://github.com/espressif/esp32-camera.git esp32-camera
cd esp32-camera
# v2.0.1
git checkout 1ac48e5397ee22a59a18a314c4acf44c23dfe946
cd $ESPIDF/components
ln -s $ROOT/esp32-camera esp32-camera
