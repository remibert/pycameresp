[Main page](/README.md) | [CamFlasher](/doc/CAMFLASHER.md)

# Shell

The software embeds a shell executed on the device. 

The shell can be used remotely with telnet, or with a usb connection with the [CamFlasher](tools/camflasher/README.md).

![ShellEdit.gif](/images/ShellEdit.gif "Shell and text editor")

In default mode pycameresp is running, it runs servers, wifi manager and motion detection.

To enter the shell you have to suspend the servers in progress, to do this press any key when you see the message : **Press key to start command line**.

It may take a few seconds especially in the boot phase, retry press key if it does not start, and you should see :

```
<<<<<<<<<< Enter shell >>>>>>>>>>
/=>
```

The prompt of shell is : 
```
=>
```

To edit a script, just enter
```
=> edit myscript.py
```
Press **escape** to exit from text editor, **F5** execute the script currently being edited (execution looks for a main function and executes it). ([See editor](/doc/EDITOR.md))

To return to server mode use **exit** command :
```
/=> exit
<<<<<<<<<< Exit  shell >>>>>>>>>>
```

If you done **Ctrl-C** or **quit** command you will find the prompt python, after that you must reboot to restart the servers.

To start the shell directly from python :
```
>>> from shell import sh
>>> sh()
```


# Commands :

commands    | help
------------|---------
cat         | display the content of file
cd          | change directory
cls         | clear screen
cp          | copy file
date        | get the system date or synchronize with Ntp
deepsleep   | deepsleep of board
df          | display free disk space
dump        | display hexadecimal dump of the content of file
edit        | start editor with selected file
eval        | evaluation python string
exec        | execute python string
exit        | exit of shell
exporter    | transfer files from device to computer (only available with camflasher)
find        | find a file
flashinfo   | flash informations
gc          | garbage collection
grep        | grep text in many files
help        | list all command available
host2ip     | convert hostname in ip address
importer    | transfer files from computer to device (only available with camflasher)
ip2host     | convert ip address in hostname
ll          | list files with details
ls          | list files
man         | manual of one command
meminfo     | memory informations
mkdir       | create directory
mount       | mount sd card
mv          | move file
ping        | ping host
pwd         | current directory
reboot      | reboot board
rm          | remove file
rmdir       | remove directory
run         | execute python script
setdate     | set date and time
sysinfo     | system informations
temperature | device temperature
umount      | umount sd card
uptime      | the amount of time system is running
