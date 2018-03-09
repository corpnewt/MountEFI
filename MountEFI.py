import subprocess
import plistlib
import sys
import os
import time
import json

class Disk:

    def __init__(self):
        self.diskutil = self.get_diskutil()
        self.disks = self.get_disks()
        self.os_version = ".".join(
            self._get_output(["sw_vers", "-productVersion"]).split(".")[:2]
        )
        self.can_apfs = True
        if self._compare_versions(self.os_version, "10.12"):
            # We're under 10.12 - no apfs - initialize some empty vars
            self.apfs = {"Containers" : []}
            self.can_apfs = False
        else:
            self.apfs  = self.get_apfs()

    def _compare_versions(self, vers1, vers2):
        # Helper method to compare ##.## strings
        #
        # vers1 < vers2 = True
        # vers1 = vers2 = None
        # vers1 > vers2 = False
        #
        try:
            v1_parts = vers1.split(".")
            v2_parts = vers2.split(".")
        except:
            # Formatted wrong - return None
            return None
        for i in range(len(v1_parts)):
            if int(v1_parts[i]) < int(v2_parts[i]):
                return True
            elif int(v1_parts[i]) > int(v2_parts[i]):
                return False
        # Never differed - return None, must be equal
        return None

    def _update_disks(self):
        self.disks = self.get_disks()
        if self.can_apfs:
            self.apfs  = self.get_apfs()

    def _get_output(self, comm, shell = False):
        try:
            if shell and type(comm) is list:
                comm = " ".join(comm)
            if not shell and type(comm) is str:
                comm = comm.split()
            p = subprocess.Popen(comm, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            c = p.communicate()
            # p = subprocess.run(comm, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if not p.returncode == 0:
                return c[1].decode("utf-8")
            return c[0].decode("utf-8")
        except:
            return c[1].decode("utf-8")

    def get_diskutil(self):
        # Returns the path to the diskutil binary
        return self._get_output(["which", "diskutil"]).split("\n")[0].split("\r")[0]

    def get_disks(self):
        # Returns a dictionary object of connected disks
        disk_list = self._get_output([self.diskutil, "list", "-plist"])
        if sys.version_info >= (3, 0):
            return plistlib.loads(disk_list.encode("utf-8"))
        else:
            return plistlib.readPlistFromString(disk_list.encode("utf-8"))

    def get_apfs(self):
        # Returns a dictionary object of apfs disks
        disk_list = self._get_output("echo y | " + self.diskutil + " apfs list -plist", True)
        p_list = disk_list.split("<?xml")
        if len(p_list) > 1:
            # We had text before the start - get only the plist info
            disk_list = "<?xml" + p_list[-1]
        if sys.version_info >= (3, 0):
            return plistlib.loads(disk_list.encode("utf-8"))
        else:
            return plistlib.readPlistFromString(disk_list.encode("utf-8"))

    def is_apfs(self, disk):
        if not disk:
            return False
        # Takes a disk identifier, and returns whether or not it's apfs
        for d in self.disks["AllDisksAndPartitions"]:
            if not "APFSVolumes" in d:
                continue
            if d.get("DeviceIdentifier", "").lower() == disk.lower():
                return True
            for a in d["APFSVolumes"]:
                if a["DeviceIdentifier"].lower() == disk.lower():
                    return True
        return False

    def is_core_storage(self, disk):
        if not disk:
            return False
        # Takes a disk identifier, and returns whether or not it's a core storage volume
        disk_info = self._get_output([self.diskutil, "info", "-plist", disk])
        if sys.version_info >= (3, 0):
            disk_plist = plistlib.loads(disk_info.encode("utf-8"))
        else:
            disk_plist = plistlib.readPlistFromString(disk_info.encode("utf-8"))
        return "CoreStoragePVs" in disk_plist

    def get_identifier(self, disk):
        # Should be able to take a mount point, disk name, or disk identifier,
        # and return the disk's parent
        # Iterate!!
        if not disk:
            return None
        for d in self.disks["AllDisksAndPartitions"]:
            if d.get("DeviceIdentifier", "").lower() == disk.lower() or d.get("VolumeName", "").lower() == disk.lower():
                return d["DeviceIdentifier"]
            if "APFSVolumes" in d:
                for a in d["APFSVolumes"]:
                    if "DeviceIdentifier" in a and a["DeviceIdentifier"].lower() == disk.lower():
                        return a.get("DeviceIdentifier", None)
                    if "VolumeName" in a and a["VolumeName"].lower() == disk.lower():
                        return a.get("DeviceIdentifier", None)
                    if "MountPoint" in a and a["MountPoint"].lower() == disk.lower():
                        return a.get("DeviceIdentifier", None)
            if "Partitions" in d:
                for p in d["Partitions"]:
                    if "DeviceIdentifier" in p and p["DeviceIdentifier"].lower() == disk.lower():
                        return p.get("DeviceIdentifier", None)
                    if "VolumeName" in p and p["VolumeName"].lower() == disk.lower():
                        return p.get("DeviceIdentifier", None)
                    if "MountPoint" in p and p["MountPoint"].lower() == disk.lower():
                        return p.get("DeviceIdentifier", None)
        # At this point, we didn't find it
        return None

    def get_physical_store(self, disk):
        disk_id = self.get_identifier(disk)
        if not disk_id:
            return None
        if not self.is_apfs(disk_id):
            return None
        # We have apfs - let's get the Physical Store
        for a in self.apfs["Containers"]:
            # Check if it's the whole container
            if a.get("ContainerReference", "").lower() == disk_id.lower():
                # Got a container ref - check if we have a designated physical store
                if a.get("DesignatedPhysicalStore", None):
                    # We do, return that
                    return a["DesignatedPhysicalStore"]
                if len(a.get("PhysicalStores", [])):
                    # We got a physical store list
                    return a["PhysicalStores"][0].get("DeviceIdentifier", None)
            # Check through each volume and return the parent's physical store
            for v in a.get("Volumes", []):
                if v.get("DeviceIdentifier", "").lower() == disk_id.lower():
                    if a.get("DesignatedPhysicalStore", None):
                        # We do, return that
                        return a["DesignatedPhysicalStore"]
                    if len(a.get("PhysicalStores", [])):
                        # We got a physical store list
                        return a["PhysicalStores"][0].get("DeviceIdentifier", None)

    def get_core_storage_pv(self, disk):
        disk_id = self.get_identifier(disk)
        if not disk_id:
            return None
        if not self.is_core_storage(disk_id):
            return None
        # We have a core storage volume - let's get the PVDisk
        disk_info = self._get_output([self.diskutil, "info", "-plist", disk_id])
        if sys.version_info >= (3, 0):
            disk_plist = plistlib.loads(disk_info.encode("utf-8"))
        else:
            disk_plist = plistlib.readPlistFromString(disk_info.encode("utf-8"))
        if len(disk_plist.get("CoreStoragePVs", [])):
            return disk_plist["CoreStoragePVs"][0].get("CoreStoragePVDisk", None)
        return None

    def get_parent(self, disk):
        # Disk can be a mount point, disk name, or disk identifier
        disk_id = self.get_identifier(disk)
        if not disk_id:
            return None
        if self.is_apfs(disk_id):
            # We have apfs - let's get the container ref
            for a in self.apfs["Containers"]:
                # Check if it's the whole container
                if "ContainerReference" in a and a["ContainerReference"].lower() == disk_id.lower():
                    return a["ContainerReference"]
                # Check through each volume and return the parent's container ref
                if "Volumes" in a:
                    for v in a["Volumes"]:
                        if "DeviceIdentifier" in v and v["DeviceIdentifier"].lower() == disk_id.lower():
                            return a["ContainerReference"]
        else:
            # Not apfs - go through all volumes and whole disks
            for d in self.disks["AllDisksAndPartitions"]:
                if "DeviceIdentifier" in d and d["DeviceIdentifier"].lower() == disk_id.lower():
                    return d["DeviceIdentifier"]
                if "Partitions" in d:
                    for p in d["Partitions"]:
                        if "DeviceIdentifier" in p and p["DeviceIdentifier"].lower() == disk_id.lower():
                            return d["DeviceIdentifier"]
        # Didn't find anything
        return None

    def get_efi(self, disk):
        disk_id = self.get_identifier(disk)
        if not disk_id:
            return None
        if self.is_apfs(disk_id):
            disk_id = self.get_parent(self.get_physical_store(disk_id))
        elif self.is_core_storage(disk_id):
            disk_id = self.get_parent(self.get_core_storage_pv(disk_id))
        else:
            disk_id = self.get_parent(disk_id)
        if not disk_id:
            return None
        # At this point - we should have the parent
        for d in self.disks["AllDisksAndPartitions"]:
            if d.get("DeviceIdentifier", "").lower() == disk_id.lower():
                # Found our disk
                for p in d.get("Partitions", []):
                    if p.get("Content", "").lower() == "efi":
                        return p.get("DeviceIdentifier", None)
        return None

    def mount_partition(self, disk):
        disk_id = self.get_identifier(disk)
        if not disk_id:
            return None
        return self._get_output([self.diskutil, "mount", disk_id])

    def unmount_partition(self, disk):
        disk_id = self.get_identifier(disk)
        if not disk_id:
            return None
        return self._get_output([self.diskutil, "unmount", disk_id])

    def get_volumes(self):
        # Returns a list object with all volumes from disks
        return self.disks["VolumesFromDisks"]

    def get_volume_name(self, disk):
        # Returns the volume name of the passed ident if one exists
        disk_id = self.get_identifier(disk)
        if not disk_id:
            return None
        for d in self.disks["AllDisksAndPartitions"]:
            if "DeviceIdentifier" in d and d["DeviceIdentifier"].lower() == disk_id.lower():
                # Whole disk - no mounts
                return None
            if "APFSVolumes" in d:
                for a in d["APFSVolumes"]:
                    if "DeviceIdentifier" in a and a["DeviceIdentifier"].lower() == disk_id.lower():
                        return a.get("VolumeName", None)
            if "Partitions" in d:
                for p in d["Partitions"]:
                    if "DeviceIdentifier" in p and p["DeviceIdentifier"].lower() == disk_id.lower():
                        return p.get("VolumeName", None)

    def get_mounted_volumes(self):
        # Returns a list of mounted volumes
        vol_list = self._get_output(["ls", "-1", "/Volumes"]).split("\n")
        if vol_list[len(vol_list)-1] == "":
            vol_list.pop(len(vol_list)-1)
        return vol_list

# Helper methods
def grab(prompt):
    if sys.version_info >= (3, 0):
        return input(prompt)
    else:
        return str(raw_input(prompt))

# Header drawing method
def head(text = "CorpTool", width = 50):
    os.system("clear")
    print("  {}".format("#"*width))
    mid_len = int(round(width/2-len(text)/2)-2)
    middle = " #{}{}{}#".format(" "*mid_len, text, " "*((width - mid_len - len(text))-2))
    print(middle)
    print("#"*width)

# Main menu
def main():
    # Refresh volumes
    d = Disk()
    head("MountEFI")
    print(" ")
    # List the volumes
    num = 0
    vols = d.get_mounted_volumes()
    for v in vols:
        num += 1
        print("{}. {}".format(num, v))
    print(" ")
    print("Q. Quit\n")
    default = d.get_volume_name("/")
    if not default:
        default = "/"
    print("NOTE: Appending \"q\" to the end of a choice will quit")
    print("      after mount.  For example, \"1q\" would mount")
    print("      the first option's EFI, then quit.  This ONLY")
    print("      works when you use the number, not the path or")
    print("      disk number.\n")
    select = grab("Please select a volume (default is {}):  ".format(default))

    if select.lower() == "q":
        custom_quit()

    head("MountEFI")
    print(" ")

    quit_after = False
    if select == "":
        select = "/"
    try:
        select = int(select)
    except:
        try:
            qcheck = select[-1]
            select = int(select[:-1])
            if qcheck.lower() == "q":
                quit_after = True
        except:
            pass
    if type(select) is int:
        # Check if we're out of bounds
        if select < 1 or select > len(vols):
            # OOB
            return
        efi = d.get_efi(vols[select-1])
        if not efi:
            print("{} has no EFI partition...".format(vols[select-1]))
        else:
            print(d.mount_partition(efi))
        time.sleep(3)
        if quit_after:
            custom_quit()
        return
    else:
        # Maybe it's a volume name/mount point/ident/etc
        disk_ident = d.get_identifier(select)
        if not disk_ident:
            return
        efi = d.get_efi(disk_ident)
        if not efi:
            print("{} has no EFI partition...".format(d.get_parent(disk_ident)))
        else:
            print(d.mount_partition(d.get_efi(disk_ident)))
        time.sleep(3)
        return

def custom_quit():
    head("MountEFI")
    print("by CorpNewt\n")
    print("Thanks for testing it out, for bugs/comments/complaints")
    print("send me a message on Reddit, or check out my GitHub:\n")
    print("www.reddit.com/u/corpnewt")
    print("www.github.com/corpnewt\n")
    print("Have a nice day/night!\n\n")
    exit(0)

if len(sys.argv) > 1:
    # We started with args - assume the arg passed is the disk to mount
    d = Disk()
    d.mount_partition(d.get_efi(sys.argv[1]))
    exit(0)

# Start the loop and keep it going
while True:
    main()
