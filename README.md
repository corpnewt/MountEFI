# MountEFI
A more robust edition of my previous MountEFI script

Added my usual collection of disk functions - plus some experimentation with callback functions.

-

~~Todo:~~

~~In the future, I plan to allow input/output based on another script.~~

__Feature added.__  Other scripts can now call this script to do a silent mount - and receive a 0 on succes, or 1 (or higher) on failure.

For example:  If another script calls `MountEFI -mount disk0s1` then my script would mount without user interaction, and return a 0 on success, or a 1 on failure.

***

## To install:

Do the following one line at a time in Terminal:

    git clone https://github.com/corpnewt/MountEFI
    cd MountEFI
    chmod +x MountEFI.command
    
Then run with either `./MountEFI.command` or by double-clicking *MountEFI.command*
