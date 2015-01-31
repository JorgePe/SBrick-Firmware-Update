#!/usr/bin/env python

from __future__ import print_function
import sys, traceback, os, time
from subprocess import call, check_output
from time import sleep

# possible arguments for a next version

DEVICE_ID="00:07:80:2E:2F:19"                 # Bluetooth ID of the SBrick
BT_ADAPTER="hci1"                             # hci adapter to be used
FILE_NAME="sbrick-fw-4.2b2-1.3.2-122.ota"     # Firmware file to be used (OTA format)

DELAY = 0.008                                 # takes 65 seconds to upload v4.1 (100 kB) and 72s to upload v4.2b2 (110 kB)

#### GATT commands ####

READ_HW_VERSION = "gatttool --device=" + DEVICE_ID + " --adapter=" + BT_ADAPTER + " --char-read --handle=0x000c"
READ_FW_VERSION = "gatttool --device=" + DEVICE_ID + " --adapter=" + BT_ADAPTER + " --char-read --handle=0x000a"

# WRITEBLOCK command needs to be completed with a string
#  of 40 hexadecimal values (the 20-byte block to upload)

# The Bluetooth handles changed from firmware 4.0 to 4.2 (or perhaps 4.1)
# so we have to consider both

# SBrick Firmware 4.0 (original release)
WRITEBLOCK_40 = "gatttool --device=" + DEVICE_ID + " --adapter=" + BT_ADAPTER + " --char-write --handle=0x001e --value="
READTOTAL_40 = "gatttool --device=" + DEVICE_ID + " --adapter=" + BT_ADAPTER + " --char-read --handle=0x0021"
REBOOTDFU_40 = "gatttool --device=" + DEVICE_ID + " --adapter=" + BT_ADAPTER + " --char-write-req --handle=0x001b --value=03"

# SBrick Firmware 4.2 (end of January 2015)
WRITEBLOCK_42 = "gatttool --device=" + DEVICE_ID + " --adapter=" + BT_ADAPTER + " --char-write --handle=0x0016 --value="
READTOTAL_42 = "gatttool --device=" + DEVICE_ID + " --adapter=" + BT_ADAPTER + " --char-read --handle=0x0013"
REBOOTDFU_42 = "gatttool --device=" + DEVICE_ID + " --adapter=" + BT_ADAPTER + " --char-write-req --handle=0x0013 --value=03"
REBOOT_42 = "gatttool --device=" + DEVICE_ID + " --adapter=" + BT_ADAPTER + " --char-write --handle=0x001a --value=12"

# twoDigitHex
#   this function converts a number into a 2-char hexadecimal string
#

def twoDigitHex( number ):
    return '%02x' % number

def main():
  try:

    # find SBrick firmware version
    # should return something like 'Characteristic value/descriptor: 34 2e 30'
    # 34 = '4'  2E =' .'  30 = '0'
    # can have more chars for minor versions like 4.2b2 but will use just the first 3

    result=check_output(READ_HW_VERSION, shell=True)
    parsed_result=result.split(" ")
    SBRICK_HW_VS=(parsed_result[2]+parsed_result[3]+parsed_result[4]).decode("hex")

    result=check_output(READ_FW_VERSION, shell=True)
    parsed_result=result.split(" ")
    SBRICK_FW_VS=(parsed_result[2]+parsed_result[3]+parsed_result[4]).decode("hex")

    print("SBrick Hardware Version: " + SBRICK_HW_VS)
    print("SBrick Firmware Version: " + SBRICK_FW_VS)

    if(SBRICK_FW_VS == "4.0"):
      print("Will use 4.0 handles")
      WRITEBLOCK = WRITEBLOCK_40
      READTOTAL = READTOTAL_40
      REBOOTDFU = REBOOTDFU_40
    elif(SBRICK_FW_VS == "4.2"):
      print("Will use 4.2 handles")
      WRITEBLOCK = WRITEBLOCK_42
      READTOTAL = READTOTAL_42
      REBOOTDFU = REBOOTDFU_42
    else:
      print("Don't know how to handle this firmware version")
      sys.exit(0)

    answer=raw_input("Shell we proceed (Y/N) ? ")
    if((answer=="Y") or (answer=="y")):
      sleep(2.5)

      counter=0
      f = open(FILE_NAME, 'rb')
      i=0
      block=''

      start_time = time.localtime() 

      # read loop - it ends when reaches the end of the input file
    
      while True:
        value = f.read(1)  
        if not value:
          break

        i=i+1   
        block=block+twoDigitHex(ord(value))

        if(i==20):
          counter=counter+20

          call(WRITEBLOCK+block, shell=True)
        
          # this is optional - shows how many bytes and which blocks were sent
          # if you choose not to use you may need to increase DELAY at each iteration
          print(counter,block)

          i=0
          block=''

          # small delay to give SBrick time to process each block
          sleep(DELAY)
      
      # end of read loop
    
      f.close()
      end_time = time.localtime()

      # read DFU Pointer (how many bytes were transfered)
      # should return something like 'Characteristic value/descriptor: 00 00 00 00 \n'
      # First byte = LSB , Last byte = MSB
      result=check_output(READTOTAL, shell=True)

      # parse result and convert to integer
      parsed_result=result.split(" ")
      DFU_Pointer=int(parsed_result[5]+parsed_result[4]+parsed_result[3]+parsed_result[2],16)

      print("\nReport:")
      print(" Total bytes  :", counter)
      print(" DFU_Pointer  :", DFU_Pointer)
      print(" Upgrade (s)  :", time.mktime(end_time)-time.mktime(start_time))

      if(counter == DFU_Pointer):
        print(" Transfer succeeded. Rebooting to DFU mode...")
        call(REBOOTDFU, shell=True)
      else:
        if(SBRICK_FW_VS=="4.0"):
          print("Transfer failed. Please switch power of your SBrick then try again.")
        elif(SBRICK_FW_VS=="4.2"):
          print("Transfer failed. Rebooting, please try again...")
          call(REBOOT_42, shell=True)

    else:
      print("Goodbye!")

  except (KeyboardInterrupt, SystemExit):
    print("Exiting...")
  except Exception:
    traceback.print_exc(file=sys.stdout)

  sys.exit(0)

if __name__ == "__main__":
    main()
