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

echo "**************"
echo "Init export.sh"
echo "**************"
cd $ROOT/micropython/ports/esp32
source $ESPIDF/export.sh


