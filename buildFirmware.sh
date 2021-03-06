# ! bash
if [ $# = 1 ]
then
	export BOARD=$1
else
	export BOARD=ESP32CAM
fi
# GENERIC
# GENERIC_SPIRAM
if [ -n "$PYCAMERESP_FIRMWARE" ]; then
	export ROOT=$PYCAMERESP_FIRMWARE
else
	export ROOT=`pwd`/firmware
fi

export ESPIDF=$ROOT/esp-idf
export IDF_PATH=$ROOT/esp-idf

echo "********************"
echo "Init env micropython"
echo "********************"
cd $ROOT/micropython/ports/esp32
python3 -m venv build-venv
source build-venv/bin/activate

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

echo "**************"
echo "Init export.sh"
echo "**************"
cd $ROOT/micropython/ports/esp32
source $ESPIDF/export.sh

echo "***************"
echo "Build mpy-cross"
echo "***************"
cd $ROOT/micropython/mpy-cross
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
	make mpy-cross V=1
else
	make mpy-cross
fi

echo "****************"
echo "Build submodules"
echo "****************"
cd $ROOT/micropython/ports/esp32
make submodules

echo "**************"
echo "Build " $BOARD
echo "**************"
make BOARD=$BOARD
cd $ROOT
cp $ROOT/micropython/ports/esp32/build-$BOARD/firmware.bin $BOARD-firmware.bin
