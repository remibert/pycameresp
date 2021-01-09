# ! bash
export ROOT=`pwd`/firmware

python3 backupGitModif.py
cp -f -r -v patch/c/micropython/* $ROOT/micropython/
cp -f -r -v patch/c/esp-idf/*     $ROOT/esp-idf/
