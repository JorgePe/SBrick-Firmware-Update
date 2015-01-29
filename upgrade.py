#!/usr/bin/env python

import sys, traceback, os
from subprocess import call
from time import sleep

# possible arguments

DEVICE_ID="00:07:80:2E:30:3F"                 # Bluetooth ID of the SBrick
BT_ADAPTER="hci1"                             # hci adapter to be used
FILE_NAME="sbrick-fw-4.2b2-1.3.2-122.ota"     # Firmware file to be used (OTA format)

DELAY=0.005                                   # assure a small pause between each 20-byte block write

# gatttool command
#   it needs to be completed with a string of 40 chars containing the hexadecimal values of the
#   20-byte block to be written

WRITEBLOCK = "gatttool --device=" + DEVICE_ID + " --adapter=" + "BT_ADAPTER" + " --char-write --handle=0x001e --value="

# twoDigitHex
#   this function converts a number into a 2-char hexadecimal string
#

def twoDigitHex( number ):
    return '%02x' % number

def main():
  try:

    counter=1
    f = open(FILE_NAME, 'rb')
    i=0
    block=''

    # read loop - it ends when reaches the end of the input file
    
    while True:
      value = f.read(1)  
      if not value:
        break

      i=i+1
      counter=counter+1
      
      block=block+twoDigitHex(ord(value))

      if(i==20):
        call(WRITEBLOCK+block, shell=True)
        
        # this is optional - shows how many bytes and which commands were sent
        # if you choose not to use then increase DELAY a bit
        print(counter,' ',WRITEBLOCK+block)

        i=0
        block=''

      sleep(DELAY)
      
    # end of read loop
    
    f.close()

    print("Total bytes: ", counter)
    

  except (KeyboardInterrupt, SystemExit):
    print("Exiting...")
  except Exception:
    traceback.print_exc(file=sys.stdout)

  sys.exit(0)

if __name__ == "__main__":
    main()

