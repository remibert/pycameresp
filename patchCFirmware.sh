# ! bash
if [ -n "$PYCAMERESP_FIRMWARE" ]; then
	export ROOT=$PYCAMERESP_FIRMWARE
else
	export ROOT=`pwd`/firmware
fi

python3 scripts/backupGitModif.py          "$ROOT"
cp -f -r -v -p patch/c/micropython/*       "$ROOT/micropython/"
cp -f -r -v -p patch/c/esp-idf/*           "$ROOT/esp-idf/"
cp -f -r -v -p patch/c/esp-homekit-sdk/*   "$ROOT/esp-homekit-sdk/"


