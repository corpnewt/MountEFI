import subprocess
import plistlib
import sys
import os
import time

class Disk:

    def __init__(self):
        self.diskutil = self.get_diskutil()
        self.disks = self.get_disks()
        self.apfs  = self.get_apfs()

    def _update_disks(self):
        self.disks = self.get_disks()
        self.apfs  = self.get_apfs()

    def _get_output(self, comm):
        try:
            p = subprocess.Popen(comm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        return plistlib.loads(disk_list.encode("utf-8"))

    def get_apfs(self):
        # Returns a dictionary object of apfs disks
        disk_list = self._get_output([self.diskutil, "apfs", "list", "-plist"])
        return plistlib.loads(disk_list.encode("utf-8"))

    def is_apfs(self, disk):
        # Takes a disk identifier, and returns whether or not it's apfs
        for d in self.disks["AllDisksAndPartitions"]:
            if not "APFSVolumes" in d:
                continue
            if "DeviceIdentifier" in d and d["DeviceIdentifier"].lower() == disk.lower():
                return True
            for a in d["APFSVolumes"]:
                if a["DeviceIdentifier"].lower() == disk.lower():
                    return True
        return False

    def get_identifier(self, disk):
        # Should be able to take a mount point, disk name, or disk identifier,
        # and return the disk's parent
        # Iterate!!
        for d in self.disks["AllDisksAndPartitions"]:
            if "DeviceIdentifier" in d and d["DeviceIdentifier"].lower() == disk.lower():
                return d["DeviceIdentifier"]
            if "APFSVolumes" in d:
                for a in d["APFSVolumes"]:
                    if "DeviceIdentifier" in a and a["DeviceIdentifier"].lower() == disk.lower():
                        return a["DeviceIdentifier"]
                    if "VolumeName" in a and a["VolumeName"].lower() == disk.lower():
                        return a["DeviceIdentifier"]
                    if "MountPoint" in a and a["MountPoint"].lower() == disk.lower():
                        return a["DeviceIdentifier"]
            if "Partitions" in d:
                for p in d["Partitions"]:
                    if "DeviceIdentifier" in p and p["DeviceIdentifier"].lower() == disk.lower():
                        return p["DeviceIdentifier"]
                    if "VolumeName" in p and p["VolumeName"].lower() == disk.lower():
                        return p["DeviceIdentifier"]
                    if "MountPoint" in p and p["MountPoint"].lower() == disk.lower():
                        return p["DeviceIdentifier"]
        # At this point, we didn't find it
        return None

    def get_physical_store(self, disk):
        disk_id = self.get_identifier(disk)
        if not disk_id:
            return None
        if self.is_apfs(disk_id):
            # We have apfs - let's get the Physical Store
            for a in self.apfs["Containers"]:
                # Check if it's the whole container
                if "ContainerReference" in a and a["ContainerReference"].lower() == disk_id.lower():
                    return a["DesignatedPhysicalStore"]
                # Check through each volume and return the parent's physical store
                if "Volumes" in a:
                    for v in a["Volumes"]:
                        if "DeviceIdentifier" in v and v["DeviceIdentifier"].lower() == disk_id.lower():
                            return a["DesignatedPhysicalStore"]
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
        else:
            disk_id = self.get_parent(disk_id)
        if not disk_id:
            return None
        # At this point - we should have the parent
        for d in self.disks["AllDisksAndPartitions"]:
            if d["DeviceIdentifier"].lower() == disk_id.lower():
                # Found our disk
                if not "Partitions" in d:
                    return None
                for p in d["Partitions"]:
                    if "Content" in p and p["Content"].lower() == "efi":
                        return p["DeviceIdentifier"]
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
                        if "VolumeName" in a:
                            return a["VolumeName"]
                        else:
                            return None
            if "Partitions" in d:
                for p in d["Partitions"]:
                    if "DeviceIdentifier" in p and p["DeviceIdentifier"].lower() == disk_id.lower():
                        if "VolumeName" in p:
                            return p["VolumeName"]
                        else:
                            return None

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
    select = grab("Please select a volume (default is {}):  ".format(default))

    if select.lower() == "q":
        custom_quit()

    head("MountEFI")
    print(" ")

    if select == "":
        select = "/"
    try:
        select = int(select)
    except:
        pass
    if type(select) is int:
        # Check if we're out of bounds
        if select < 0 or select >= len(vols):
            # OOB
            return
        print(d.mount_partition(d.get_efi(vols[select-1])))
        time.sleep(3)
        custom_quit()
    else:
        # Maybe it's a volume name/mount point/ident/etc
        disk_ident = d.get_identifier(select)
        if not disk_ident:
            return
        print(d.mount_partition(d.get_efi(disk_ident)))
        time.sleep(3)
        custom_quit()

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