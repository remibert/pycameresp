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
	pip3 install serial
	pip3 install pyqt6
	pip3 install pyinstaller
	pip3 install esptool
	pip3 install pyserial
fi

echo "***************"
echo "Get Micropython"
echo "***************"
git clone https://github.com/micropython/micropython.git
cd $ROOT/micropython
git checkout 7c54b6428058a236b8a48c93c255948ece7e718b #  Version 1.17 OK
# git checkout d42cba0d22cac812cc5a12f4670010b45932eafa # Problem PWM
# git checkout 0d9429f44cd23f5cfdd80d53adccbf384e23665a # Problem PWM

echo "*************************"
echo "Get micropython submodule"
echo "*************************"
cd ports/esp32
git submodule update --init --recursive
cd $ROOT
ln -s $ROOT/micropython/ports/esp32 esp32

echo "*************"
echo "Get espressif"
echo "*************"
cd $ROOT
git clone https://github.com/espressif/esp-idf.git
cd $ESPIDF
#~ git checkout 52f1f68dc7f647def4bd3ff14bf145f87fe99995 # Version v4.3-beta1 (bug) 
#~ git checkout c40f2590bf759ff60ef122afa79b4ec04e7633d2 # Version v4.2 (OK)        
git checkout 7ab8f793ca5b026f37ae812bcc103e3aa698d164 # Version v4.2.2 (OK)
#~ git checkout 2e74914051d14ec2290fc751a8486fb51d73a31e # Version v4.3.1 (Seems work, one time I had a problem with camera, Leaves very little RAM on an esp32)
#~ git checkout c8315e01107c10898947a817d5cf763cdd3f5a4f # Version v4.4-dev (bug)   


echo "***********************"
echo "Get submodule espressif"
echo "***********************"
cd $ESPIDF
git submodule update --init --recursive
./install.sh

echo "****************"
echo "Get esp32 camera"
echo "****************"
cd $ROOT
git clone https://github.com/espressif/esp32-camera.git esp32-camera
cd esp32-camera
# After the version 722497cb19383cd4ee6b5d57bb73148b5af41b24 
# all version until 1eb90a8849496e5d4c9b1ee10ab9e60ca756dca0 have contrast problem in part of image
git checkout 722497cb19383cd4ee6b5d57bb73148b5af41b24
cd $ESPIDF/components
ln -s $ROOT/esp32-camera esp32-camera

echo "************"
echo "Get Home kit"
echo "************"
cd $ROOT
git clone https://github.com/espressif/esp-homekit-sdk.git
cd esp-homekit-sdk
git checkout c62f64dea6669547182e932dfded0a3a912a1951
git submodule update --init --recursive

cd $ESPIDF/components
ln -s $ROOT/esp-homekit-sdk/components/homekit/esp_hap_apple_profiles esp_hap_apple_profiles
ln -s $ROOT/esp-homekit-sdk/components/homekit/esp_hap_core           esp_hap_core
ln -s $ROOT/esp-homekit-sdk/components/homekit/esp_hap_extras         esp_hap_extras
ln -s $ROOT/esp-homekit-sdk/components/homekit/esp_hap_platform       esp_hap_platform
ln -s $ROOT/esp-homekit-sdk/components/homekit/hkdf-sha               hkdf-sha
ln -s $ROOT/esp-homekit-sdk/components/homekit/json_generator         json_generator
ln -s $ROOT/esp-homekit-sdk/components/homekit/json_parser            json_parser
ln -s $ROOT/esp-homekit-sdk/components/homekit/mu_srp                 mu_srp

echo "*************"
echo "Get pyparsing"
echo "*************"
cd $ROOT
pip3 install pyparsing==2.3.1

echo "***************"
echo "Init virtualenv"
echo "***************"
cd $ROOT
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
	pip3 install --upgrade pip
	pip3 install -r $ESPIDF/requirements.txt
	pip3 install virtualenv
else
	pip install --upgrade pip
	pip install -r $ESPIDF/requirements.txt
	pip install virtualenv
fi