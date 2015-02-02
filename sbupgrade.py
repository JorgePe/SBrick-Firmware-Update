#!/usr/bin/env python

from __future__ import print_function
import sys, traceback, os, time, getopt
from subprocess import call, check_output, CalledProcessError
from time import sleep

##########################################################################
# sbupgrade.py -a BT_ADAPTER -d DEVICE_ID -f FIRMWARE_FILE -t DELAY
##########################################################################
# command line arguments:
#
# BT_ADAPTER         hci adapter to be used (like 'hci0' or 'hci1')
#                    you can use 'hciconfig -a' to know your adapter
#
# DEVICE_ID          Bluetooth ID of the SBrick (like '00:07:80:2E:2F:19')
#                    you can use 'hcitool -i hci0 lescan' to scan Blutooth Low Energy devices and get the IDs
#
# FIRMWARE_FILE      Firmware OTA file to be used (like 'sbrick-fw-4.2b2-1.3.2-122.ota')
#
# DELAY              pause between each 20-byte block transfer
#                    with a 8ms pause it takes 65 seconds to upload v4.1 (100 kB)
#                    and 72s to upload v4.2b2 (110 kB)
#
##########################################################################

# exit codes
EXIT_OK   = 0
EXIT_ARGS = 2
EXIT_FILE = 3
EXIT_HW   = 4
EXIT_FW   = 5
EXIT_FWID = 6                                 # Unknows Firmware ID - not safe to proceed


#######################################################################
# Function: twoDigitHex
#######################################################################
#   this function converts a number into a 2-char hexadecimal string
#
def twoDigitHex( number ):
    return '%02x' % number
#
#######################################################################

#######################################################################
# Function print_help
#######################################################################
#
def print_help():
  print('')
  print('sbupgrade - SBrick firmware upgrade utility')
  print('Usage:')
  print('   sbupgrade.py -a <adapter> -d <device> -f <file> -t <delay>')
  print('')
  print('   <adapter>         HCI adapter, e.g. hci0')
  print('   <device>          SBrick Bluetooh Addres, e.g. AA:BB:CC:DD:EE:FF')
  print('   <file>            firmware OTA file, e.g. sbrick-fw-4.2.ota')
  print('   <delay>           delay time in milliseconds, e.g. 8')
  print('')
#
#######################################################################


#######################################################################
# Function print_version
#######################################################################
#
def print_version():
  print('')
  print('SBrick Upgrade Tool 0.2 - Jorge Pereira - January 2015')
#
#######################################################################


#######################################################################
# SBrick GATT Functions
#######################################################################
#
#   The SBrick Bluetooth handles changed from firmware 4.0 to 4.2 (or perhaps 4.1)
#   so we have to consider both (except for SBrickReboot, not implemented in 4.0)
#
#######################################################################
# Function SBrickWriteBlock
#######################################################################
#
def SBrickWriteBlock(BTAdapter, SBrickID, FirmwareVersion, Block):
  if (FirmwareVersion == "4.0"):
    call("gatttool --device=" + SBrickID + " --adapter=" + BTAdapter + " --char-write --handle=0x001e --value=" + Block, shell=True)
  elif (FirmwareVersion == "4.2"):
    call("gatttool --device=" + SBrickID + " --adapter=" + BTAdapter + " --char-write --handle=0x0016 --value=" + Block, shell=True)
  return 0
#
#######################################################################
# Function SBrickReadDFUPointer
#######################################################################
#
def SBrickReadDFUPointer(BTAdapter, SBrickID, FirmwareVersion):
  if (FirmwareVersion == "4.0"):
    return check_output("gatttool --device=" + SBrickID + " --adapter=" + BTAdapter + " --char-read --handle=0x0021", shell=True)
  elif (FirmwareVersion == "4.2"):
    return check_output("gatttool --device=" + SBrickID + " --adapter=" + BTAdapter + " --char-read --handle=0x0013", shell=True)
  else:
    return -1
#
#######################################################################
# Function SBrickRebootDFU
#######################################################################
#
def SBrickRebootDFU (BTAdapter, SBrickID, FirmwareVersion):
  if (FirmwareVersion == "4.0"):
    call("gatttool --device=" + SBrickID + " --adapter=" + BTAdapter + " --char-write-req --handle=0x001b --value=03", shell=True)
  elif (FirmwareVersion == "4.2"):
    call("gatttool --device=" + SBrickID + " --adapter=" + BTAdapter + " --char-write-req --handle=0x0013 --value=03", shell=True)
  return 0
#
#######################################################################
# Function SBrickReboot
#######################################################################
#
def SBrickReboot (BTAdapter, SBrickID, FirmwareVersion):
  if (FirmwareVersion == "4.0"):
    return -1
  elif (FirmwareVersion == "4.2"):
    call("gatttool --device=" + SBrickID + " --adapter=" + BTAdapter + " --char-write --handle=0x001a --value=12", shell=True)
  return 0
#
#######################################################################
# Function SBrickGetFw
#######################################################################
#
def SBrickGetFw (BTAdapter, SBrickID):
  return check_output("gatttool --device=" + SBrickID + " --adapter=" + BTAdapter + " --char-read --handle=0x000a", shell=True)
#
#######################################################################
# Function SBrickGetHw
#######################################################################
#
def SBrickGetHw (BTAdapter, SBrickID):
  return check_output("gatttool --device=" + SBrickID + " --adapter=" + BTAdapter + " --char-read --handle=0x000c", shell=True)
#
#######################################################################



################
# Main program #
################

def main(argv):
  BT_ADAPTER = ''
  DEVICE_ID = ''
  FIRMWARE_FILE = ''
  DELAY = 0.008

  try:
    opts, args = getopt.getopt(argv,"hva:d:f:t:")

  except getopt.GetoptError:
    print_help()
    sys.exit(EXIT_ARGS)

  try:
    for opt, arg in opts:
      if opt == '-h':
        print_help()
        sys.exit(EXIT_OK)
      if opt == '-v':
        print_version()
        sys.exit(EXIT_OK)
      elif opt == '-a':
        BT_ADAPTER = arg
      elif opt == '-d':
        DEVICE_ID = arg
      elif opt == '-f':
        FIRMWARE_FILE = arg
      elif opt == '-t':
        DELAY = float(arg)/1000

    if( BT_ADAPTER=='')or(DEVICE_ID=='')or(FIRMWARE_FILE=='')or(DELAY==''):
      print_help()
      sys.exit(EXIT_ARGS)
    else:
      print('')
      print('sbupgrade - SBrick firmware upgrade utility')
      print(' Adapter:    ', BT_ADAPTER)
      print(' Device:     ', DEVICE_ID)
      print(' Firmware:   ', FIRMWARE_FILE)
      print(' Delay:      ', DELAY)

    # find SBrick hardware and firmware version
    # should return something like 'Characteristic value/descriptor: 34 2e 30'
    # 34 = '4'  2E =' .'  30 = '0'
    # can have more chars for minor versions like 4.2b2 but will use just the first 3

    try:
      result=SBrickGetHw(BT_ADAPTER,DEVICE_ID)
      parsed_result=result.split(" ")
      SBRICK_HW_VS=(parsed_result[2]+parsed_result[3]+parsed_result[4]).decode("hex")
    except CalledProcessError:
      print("Could not read SBrick hardware version")
      exit(EXIT_HW)

    try:
      result=SBrickGetFw(BT_ADAPTER,DEVICE_ID)
      parsed_result=result.split(" ")
      SBRICK_FW_VS=(parsed_result[2]+parsed_result[3]+parsed_result[4]).decode("hex")
    except CalledProcessError:
      print("Could not read SBrick firmware version")
      exit(EXIT_FW)

    print(' SBrick Hw:   ' + SBRICK_HW_VS)
    print(' SBrick Fw:   ' + SBRICK_FW_VS)

    if(SBRICK_FW_VS == "4.0"):
      print("Will use SBrick firmware 4.0 handles")
    elif(SBRICK_FW_VS == "4.2"):
      print("Will use SBrick firmware 4.2 handles")
    else:
      print("Don't know how to handle this firmware version")
      sys.exit(EXIT_FWID)

    answer=raw_input("Shell we proceed (Y/N) ? ")
    if((answer=="Y") or (answer=="y")):
      print('Proceeding in 5 seconds...')
      sleep(5)

      try:
        f = open(FIRMWARE_FILE, 'rb')

      except IOError:
        print("Problem opening firmware file "+FIRMWARE_FILE)
        exit(EXIT_FILE)

      i=0
      counter=0
      block=''

      # we measure the time it takes to transfer the fimware file to the SBrick
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

          SBrickWriteBlock(BT_ADAPTER, DEVICE_ID, SBRICK_FW_VS, block)

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

      print('Transfer completed. Checking status...')

      # read DFU Pointer (how many bytes were transfered)
      # should return something like 'Characteristic value/descriptor: 00 00 00 00 \n'
      # format is First byte = LSB ... Last byte = MSB
      # we parse the result and convert to intger

      parsed_result=SBrickReadDFUPointer(BT_ADAPTER, DEVICE_ID, SBRICK_FW_VS).split(" ")
      DFU_Pointer=int(parsed_result[5]+parsed_result[4]+parsed_result[3]+parsed_result[2],16)

      print("\nReport:")
      print(" Total bytes  :", counter)
      print(" DFU_Pointer  :", DFU_Pointer)
      print(" Upgrade (s)  :", time.mktime(end_time)-time.mktime(start_time))

      if(counter == DFU_Pointer):
        print(" Transfer succeeded. Rebooting to DFU mode...")
        SBrickRebootDFU(BT_ADAPTER, DEVICE_ID, SBRICK_FW_VS)
      else:
        if(SBRICK_FW_VS=="4.0"):
          print("Transfer failed. Please switch power of your SBrick then try again.")
        elif(SBRICK_FW_VS=="4.2"):
          print("Transfer failed. Rebooting, please try again...")
          SBrickReboot(BT_ADAPTER, DEVICE_ID, SBRICK_FW_VS)

    else:
      print('Will NOT proceed.')

  except (KeyboardInterrupt, SystemExit):
    print("Goodbye!")
    print('')
  except Exception:
    traceback.print_exc(file=sys.stdout)

  sys.exit(EXIT_OK)

if __name__ == "__main__":
   main(sys.argv[1:])
