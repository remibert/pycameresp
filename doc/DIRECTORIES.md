[Main page](/README.md) | [CamFlasher](/doc/CAMFLASHER.md)

# Directories

Below are the directory details :
- **patch/c** : patch to be applied to the C sources of the firmware.
- **patch/python** : patch to be applied to embed the python scripts in the firmware.
- **firmware** : contains all the firmware sources when using the getFirmware.sh command. The generated firmwares are stored in this directory.
- **doc** : documentation extracted from python scripts
- **tools/camflasher** : tool to flash easily the firmware or use embedded shell
- **images** : images used into the documentation
- **modules/www** : html page used to create the source file of the html templates.
- **modules/simul** : python scripts to simulate on linux or osx, it allows debugging on vscode.
- **modules/lib/shell** : shell and editor python sources
- **modules/lib/htmltemplate** : html templates python sources
- **modules/lib/webpage** : web pages python sources
- **modules/lib/video** : camera python sources
- **modules/lib/motion** : motion detection python sources
- **modules/lib/tools** : tools used for all python sources
- **modules/lib/server** : Ftp, Http, Pushover, Telnet, Ntp synchronization, user and session python sources
- **modules/lib/wifi** : Wifi and accesspoint python sources
- **modules/config** : Configuration saved in this directory

On a standard micropython firmware, copy all the files of the modules directory with its tree structure, 
into the flash memory of the board.
