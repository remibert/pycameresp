# ! bash
if [ -n "$PYCAMERESP_FIRMWARE" ]; then
	export ROOT=$PYCAMERESP_FIRMWARE
else
	export ROOT=`pwd`/firmware
fi

cp -f -r -v -p patch/python/micropython/* "$ROOT/micropython/"
# python3 scripts/backupGitModif.py  "$ROOT"
python3 scripts/patchInisetup.py   "$ROOT"
cp -f -r -v -p modules/lib/* "$ROOT/micropython/ports/esp32/modules/"