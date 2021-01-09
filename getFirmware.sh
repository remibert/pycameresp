# ! bash
export ROOT=`pwd`/firmware
export ESPIDF=$ROOT/esp-idf

mkdir $ROOT
cd $ROOT

echo "*************"
echo "Install tools"
echo "*************"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
	sudo apt-get update --fix-missing
	sudo apt-get install git wget make libncurses-dev flex bison gperf python scite git python3-pip python3-tk python3-venv
	pip3 install serial
fi

echo "***************"
echo "Get Micropython"
echo "***************"
git clone https://github.com/micropython/micropython.git

echo "********************"
echo "Checkout micropython"
echo "********************"
cd $ROOT/micropython
git checkout f7aafc0628f2008d015b32b0c0253a13f748d436

echo "*************************"
echo "Get micropython submodule"
echo "*************************"
cd $ROOT/micropython/ports/esp32
git submodule update --init --recursive

echo "*************"
echo "Get espressif"
echo "*************"
cd $ROOT
git clone https://github.com/espressif/esp-idf.git

echo "**************************"
echo "Checkout version espressif"
echo "**************************"
cd $ESPIDF
# Version 4.0.1
git checkout 4c81978a3e2220674a432a588292a4c860eef27b

echo "***********************"
echo "Get submodule espressif"
echo "***********************"
git submodule update --init --recursive
./install.sh

echo "****************"
echo "Get esp32 camera"
echo "****************"
cd $ESPIDF/components
git clone https://github.com/espressif/esp32-camera.git esp32-camera

echo "*********************"
echo "Checkout esp32 camera"
echo "*********************"
cd $ESPIDF/components/esp32-camera
git checkout 010709376a131c12c14bb074b6c5be82d2241338
cd $ROOT

pip3 install pyparsing==2.3.1
