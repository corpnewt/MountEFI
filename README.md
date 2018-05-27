# MountEFI
An *even* more robust edition of my previous MountEFI scripts.

Other scripts can call this script to do a silent mount - and receive a 0 on succes, or 1 (or higher) on failure.

For example:  If another script calls `MountEFI.command disk0` then my script would mount without user interaction, and return a 0 on success, or a 1 on failure.  This can also take multiple EFIs to mount - `MountEFI.command disk0 / disk3` would mount the EFIs connected to `disk0`, the boot drive (`/`), and `disk3` if they exist.

***

## To install:

Do the following one line at a time in Terminal:

    git clone https://github.com/corpnewt/MountEFI
    cd MountEFI
    chmod +x MountEFI.command
    
Then run with either `./MountEFI.command` or by double-clicking *MountEFI.command*
