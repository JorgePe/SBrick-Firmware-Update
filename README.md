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

The 4.2 firmware file has ~110 kB. It takes 70~75 seconds to transfer it to the SBrick, depending on the DELAY value you use.
When the transfer ends the script checks if the SBrick did received all that bytes. If OK, it issues a "Reboot into DFU mode". If not OK, it issues an ordinary reboot but only if the SBrick is already running firmware 4.2 because the original firmware (4.0) can't.  

You can use a mobile tool like the Nordic nRF Master Control Panel to confirm that the update succeeded, just read UUID 0x2a26	(Firmware Revision String).

Please note that after a firmware upgrade things may change - from 4.0 to 4.2 most handles changed and I had to remap my control scripts to the new handles. This script knows 4.0 and 4.2 handles but if you upgrade to a more recent firmware (let's say 4.6) it might became totally useless after that.

You can find the handles for each UUID characteristic with the gatttool:

$ gatttool --device XX:XX:XX:XX:XX:XX --adapter=hciX --characteristics


