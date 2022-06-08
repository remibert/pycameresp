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

export PYCAMERESP_PATH=`pwd`
export ESPIDF=$ROOT/esp-idf
export IDF_PATH=$ROOT/esp-idf

echo "***************"
echo "Install esp-idf"
echo "***************"
cd $ESPIDF
./install.sh
source export.sh

echo "***************"
echo "Build mpy-cross"
echo "***************"
cd $ROOT/micropython
make -C mpy-cross

echo "**************"
echo "Build " $BOARD
echo "**************"
cd $ROOT/micropython/ports/esp32
make submodules
make BOARD=$BOARD
cd $ROOT
cp $ROOT/micropython/ports/esp32/build-$BOARD/firmware.bin $BOARD-firmware.bin

echo "******************"
echo "Build install zips"
echo "******************"
python3 "$PYCAMERESP_PATH/scripts/zip_mpy.py" $ROOT $BOARD "$PYCAMERESP_PATH"

