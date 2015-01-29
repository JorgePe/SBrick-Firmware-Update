# SBrick-Firmware-Update
Python script to update Vengit SBrick firmware from linux system using BlueZ 5 gatttool

I'm just an amateur programmer so be carefull if you choose to use my code

This works only in linux because it uses the gatttool command to talk with Bluetooth Low Energy devices.
Recent linux Bluetooth stack (BlueZ) is needed, at least version 5.
I've been using gatttool with
 Ubuntu 14.04 and 14.10 on my laptop
 ev3dev (jessie-based) on LEGO Mindstorms EV3
 Raspbian (attention: also jessie-based, not the default) on Raspberry Pi
 
You need a Bluetooth adapter that talks BLE (any BT 4.0 should do, I mostly use a generic "Targus" USB dongle,
  lsusb says: 0a5c:21e8 Broadcom Corp. BCM20702A0 Bluetooth 4.0)

You also need to know:
 - the hci ID of your BT adapter (usualy hci0 if you just have one but use 'hciconfig -a')
 - the Bluetooth ID of your SBrick (use 'hcitool -i hci0 lescan' or a BLE tool like Nordic nRF Master Control Panel on your mobile phone)
 - the file name [and path] of your .ota firmware file [I put mine at the same folder of the script]

My first firmware file had 112640 bytes. It takes a while to transfer it to the SBrick, between 2 to 10 minutes depending on the DELAY value you use.
When the transfer ends you need to check if the SBrick did received all that bytes. Have not yet found a way but that is not critical.
Then you need to send a "Reboot into DFU mode". My script doesn't do that yet. You can use a mobile tool like the Nordic nRF Master Control Panel to write "3" or "0x03" at "OTA control - f7bf3564-fb6d-4e53-88a4-5e37e0326063" characteristic. The Sbrick will reboot, check the firmware integrity and if OK it applies it. If not OK, lets try again with slower speeds (I've achieved it at first try).

