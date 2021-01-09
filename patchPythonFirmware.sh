# ! bash
export ROOT=`pwd`/firmware

python3 backupGitModif.py
cp -f -r -v patch/python/micropython/* $ROOT/micropython/
cp -f -r -v modules/lib/* $ROOT/micropython/ports/esp32/modules/