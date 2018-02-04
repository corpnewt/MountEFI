#!/bin/bash

# Turn on case-insensitive matching
shopt -s nocasematch
# turn on extended globbing
shopt -s extglob

scriptName="MountEFI - CorpNewt"
scriptMessage="Select drive containing an EFI to mount:"

function mainMenu () {
    pickDisk selectedDrive "$scriptName" "$scriptMessage"
    #echo "$selectedDrive"
    efiIdent=""
    efiIdent="$( getEFIIdentifier "$selectedDrive" )"
    
    if [[ "$efiIdent" == "" ]]; then
        driveName="$( getDiskName "$selectedDrive" )"
        clear
        echo \#\#\# ERROR \#\#\#
        echo
        echo The drive \""$driveName"\" contains
        echo no EFI partition.
        echo
        echo Press [enter] to exit...
        read nothing
        customQuit
    fi
    
    mountEFI "$efiIdent"
    
    sleep 3
    customQuit
}

function customQuit () {
	clear
	echo \#\#\# MountEFI \#\#\#
	echo by CorpNewt
	echo 
	echo Thanks for testing it out, for bugs/comments/complaints
	echo send me a message on Reddit, or check out my GitHub:
	echo 
	echo www.reddit.com/u/corpnewt
	echo www.github.com/corpnewt
	echo 
	echo Have a nice day/night!
	echo 
	echo 
	shopt -u extglob
	shopt -u nocasematch
	exit $?
}

function displayWarning () {
	clear
	echo \#\#\# WARNING \#\#\#
	echo 
	echo This script is provided with NO WARRANTY whatsoever.
	echo I am not responsible for ANY problems or issues you
	echo may encounter, or any damages as a result of running
	echo this script.
	echo 
	echo To ACCEPT this warning and FULL RESPONSIBILITY for
	echo using this script, press [enter].
	echo 
	read -p "To REFUSE, close this script."
	mainMenu
}

function mountEFI () {
    clear
    echo \#\#\# MountEFI - CorpNewt \#\#\#
    echo
    echo Mounting \""$1"\"...
    echo
    diskutil mount "$1"
    echo
}

function silentMount () {
    
    local __disk="$1"
            
    if [[ "$( isDisk "$__disk" )" == "0" ]]; then
        #Valid disk - let's get the ident and mount
        local __diskIdent="$( getDiskIdentifier "$__disk" )"
        #Mount - but suppress all output
        diskutil mount "$__diskIdent" >/dev/null 2>/dev/null
        #exit with the error code from diskutil
        exit $?
    else
        #Not a valid disk - exit with error code 1
        exit 1
    fi
}


###################################################
###               Disk Functions                ###
###################################################

function pickDisk () { 
    #$1 = callback drive picked
    #$2 = title
    #$3 = prompt


    local __returnVar="$1"
    local __scriptName="$2"
    local __message="$3"

    clear
    echo \#\#\# "$__scriptName" \#\#\#
    echo
    echo "$__message"
    echo 
    
    local driveList="$( cd /Volumes/; ls -1 | grep "^[^.]" )"
    unset driveArray
    IFS=$'\n' read -rd '' -a driveArray <<<"$driveList"
    
    #driveCount="${#driveArray[@]}"
    local driveCount=0
    local driveIndex=0
    
    for aDrive in "${driveArray[@]}"
    do
        (( driveCount++ ))
        echo "$driveCount". "$aDrive"
    done
    
    driveIndex=$(( driveCount-1 ))
    
    #ls /volumes/
    echo 
    echo 
    read drive

    if [[ "$drive" == "" ]]; then
        drive="/"
        #pickDrive
    fi
    
    #Notice - must have the single brackets or this
    #won't accurately tell if $drive is a number.
    if [ "$drive" -eq "$drive" ] 2>/dev/null; then
        #We have a number - check if it's in the array
        if [  "$drive" -le "$driveCount" ] && [  "$drive" -gt "0" ]; then
            drive="${driveArray[ (( $drive-1 )) ]}"
        else
            echo Index "$drive" out of range, checking for drive name...
        fi
    fi
    
    if [[ "$( isDisk "$drive" )" != "0" ]]; then
        if [[ "$( volumeName "$drive" )" ]]; then
			# We have a valid disk
			drive="$( volumeName "$drive" )"
			#setDisk "$drive"
		else
			# No disk available there
			echo \""$drive"\" is not a valid disk name, identifier
			echo or mount point.
			echo 
			read -p "Press [enter] to return to drive selection..."
			pickDisk "$1" "$2" "$3"
		fi
    fi

    # We have a valid drive - return it's diskIdent
    
    eval $__returnVar="$( getDiskIdentifier "$drive" )"

}

function isDisk () {
	# This function checks our passed variable
	# to see if it is a disk
	# Accepts mount point, diskXsX and an empty variable
	# If empty, defaults to "/"
	local __disk="$1"
	if [[ "$__disk" == "" ]]; then
		__disk="/"
	fi
	# Here we run diskutil info on our __disk and see what the
	# exit code is.  If it's "0", we're good.
	diskutil info "$__disk" &>/dev/null
	# Return the diskutil exit code
	echo $?
}

function volumeName () {
	# This is a last-resort function to check if maybe
	# Just the name of a volume was passed.
	local __disk="$1"
	if [[ ! -d "$__disk" ]]; then
		if [ -d "/volumes/$__disk" ]; then
			#It was just volume name
			echo "/Volumes/$__disk"
		fi
	else
		echo "$__disk"
	fi
}

function getDiskMounted () {
	local __disk="$1"
	# If variable is empty, set it to "/"
	if [[ "$__disk" == "" ]]; then
		__disk="/"
	fi
	# Output the "Volume Name" of __disk
	echo "$( diskutil info "$__disk" | grep 'Mounted' | cut -d : -f 2 | sed 's/^ *//g' | sed 's/ *$//g' )"
}

function getDiskName () {
	local __disk="$1"
	# If variable is empty, set it to "/"
	if [[ "$__disk" == "" ]]; then
		__disk="/"
	fi
	# Output the "Volume Name" of __disk
	echo "$( diskutil info "$__disk" | grep 'Volume Name' | cut -d : -f 2 | sed 's/^ *//g' | sed 's/ *$//g' )"
}

function getDiskMountPoint () {
	local __disk="$1"
	# If variable is empty, set it to "/"
	if [[ "$__disk" == "" ]]; then
		__disk="/"
	fi
	# Output the "Mount Point" of __disk
	echo "$( diskutil info "$__disk" | grep 'Mount Point' | cut -d : -f 2 | sed 's/^ *//g' | sed 's/ *$//g' )"
}

function getDiskIdentifier () {
	local __disk="$1"
	# If variable is empty, set it to "/"
	if [[ "$__disk" == "" ]]; then
		__disk="/"
	fi
	# Output the "Mount Point" of __disk
	echo "$( diskutil info "$__disk" | grep 'Device Identifier' | cut -d : -f 2 | sed 's/^ *//g' | sed 's/ *$//g' )"
}

function getDiskNumbers () {
	local __disk="$1"
	# If variable is empty, set it to "/"
	if [[ "$__disk" == "" ]]; then
		__disk="/"
	fi
	# Output the "Device Identifier" of __disk
	# If our disk is "disk0s1", it would output "0s1"
	echo "$( getDiskIdentifier "$__disk" | cut -d k -f 2 )"
}

function getDiskNumber () {
	local __disk="$1"
	# If variable is empty, set it to "/"
	if [[ "$__disk" == "" ]]; then
		__disk="/"
	fi
	# Get __disk identifier numbers
	local __diskNumbers="$( getDiskNumbers "$__disk" )"
	# return the first number
	echo "$( echo "$__diskNumbers" | cut -d s -f 1 )"
}

function getPartitionNumber () {
	local __disk="$1"
	# If variable is empty, set it to "/"
	if [[ "$__disk" == "" ]]; then
		__disk="/"
	fi
	# Get __disk identifier numbers
	local __diskNumbers="$( getDiskNumbers "$__disk" )"
	# return the second number
	echo "$( echo "$__diskNumbers" | cut -d s -f 2 )"	
}

function getPartitionType () {
	local __disk="$1"
	# If variable is empty, set it to "/"
	if [[ "$__disk" == "" ]]; then
		__disk="/"
	fi
	# Output the "Volume Name" of __disk
	echo "$( diskutil info "$__disk" | grep 'Partition Type' | cut -d : -f 2 | sed 's/^ *//g' | sed 's/ *$//g' )"
}

function getEFIIdentifier () {
	local __disk="$1"
	# If variable is empty, set it to "/"
	if [[ "$__disk" == "" ]]; then
		__disk="/"
	fi

	# Check if we are on an APFS volume
	local __tempNum="$( getDiskNumber "$__disk" )"
	local __apfsDisk="$( getPhysicalStore "disk$__tempNum" )"
	if [[ "$__apfsDisk" != "" ]]; then
		__disk="$__apfsDisk"
	fi

	local __diskName="$( getDiskName "$__disk" )"
	local __diskNum="$( getDiskNumber "$__disk" )"

	# Output the "Device Identifier" for the EFI partition of __disk
	endOfDisk="0"
	i=1
	while [[ "$endOfDisk" == "0" ]]; do
		# Iterate through all partitions of the disk, and return those that
		# are EFI
		local __currentDisk=disk"$__diskNum"s"$i"
		# Check if it's a valid disk, and if not, exit the loop
		if [[ "$( isDisk "$__currentDisk" )" != "0" ]]; then
			endOfDisk="true"
			continue
		fi

		local __currentDiskType="$( getPartitionType "$__currentDisk" )"

		if [ "$__currentDiskType" == "EFI" ]; then
			echo "$( getDiskIdentifier "$__currentDisk" )"
		fi
		i="$( expr $i + 1 )"
	done
}

function getPhysicalStore () {
	# Helper function to get the physical disk for apfs volume
	local __disk="$1"
	local __diskName="$( getDiskName "$__disk" )"
	local __diskNum="$( getDiskNumber "$__disk" )"
	# If variable is empty, set it to "/"
	if [[ "$__disk" == "" ]]; then
		__disk="/"
	fi
	# Output the physical store disk, if any
	__tempDisk="$( diskutil apfs list "$__disk" 2>/dev/null | grep 'APFS Physical Store Disk' | cut -d : -f 2 | sed 's/^ *//g' | sed 's/ *$//g' )"
	__finalDisk=""
	if [[ "$__tempDisk" != "" ]]; then
		__tempDiskNumber="$( getDiskNumber "$__tempDisk" )"
		__finalDisk="disk$__tempDiskNumber"
	fi
	echo $__finalDisk
}

###################################################
###             End Disk Functions              ###
###################################################

if [[ "$1" == "-mount" ]]; then
    if [[ "$2" != "" ]]; then
        #We're mounting via command line.
        #Hide all prompts and warnings.
        silentMount "$2"
    else
        exit 1
    fi
fi

displayWarning
