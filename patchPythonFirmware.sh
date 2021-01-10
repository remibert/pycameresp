# ! bash
export ROOT=`pwd`/firmware

python3 backupGitModif.py
cp -f -r -v -p patch/python/micropython/* $ROOT/micropython/
cp -f -r -v -p modules/lib/* $ROOT/micropython/ports/esp32/modules/