import os, sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__))))
import run, plist

class Disk:
    def __init__(self):
        self.r = run.Run()
        self.diskdump = self.check_diskdump()
        self.full_os_version = self.r.run({"args":["sw_vers", "-productVersion"]})[0]
        if len(self.full_os_version.split(".")) < 3:
            # Ensure the format is XX.YY.ZZ
            self.full_os_version += ".0"
        self.os_version = ".".join(self.full_os_version.split(".")[:2])
        self.sudo_mount_version = "10.13.6"
        self.sudo_mount_types   = ["efi system partition"]
        self.disks = self.get_disks()

    def check_diskdump(self):
        ddpath = os.path.join(os.path.dirname(os.path.realpath(__file__)),"diskdump")
        if not os.path.exists(ddpath):
            raise FileNotFoundError("Could not locate diskdump")
        if "com.apple.quarantine" in self.r.run({"args":["xattr",ddpath]})[0]:
            self.r.run({"args":["xattr","-d","com.apple.quarantine",ddpath]})
        return ddpath

    def update(self):
        # Refresh our disk list
        self.disks = self.get_disks()
        return self.disks

    def get_disks(self):
        # Check for our binary - and ensure it's setup to run
        ddpath = os.path.join(os.path.dirname(os.path.realpath(__file__)),"diskdump")
        if not os.path.exists(ddpath): return {}
        # Get our "diskutil list" and diskdump info.  Run diskutil list first
        # as it takes longer - but will stall while waiting for disks to appear,
        # meaning our diskdump output will be better reflected.
        diskutil_list = self.r.run({"args":["diskutil","list"]})[0]
        diskstring = self.r.run({"args":[ddpath]})[0]
        if not diskstring: return {}
        diskdump = plist.loads(diskstring)
        last_disk = None
        for line in diskutil_list.split("\n"):
            if line.startswith("/dev/disk"):
                last_disk = line.split()[0].split("/")[-1]
            elif not last_disk:
                continue
            elif line.strip().startswith("Logical Volume on"):
                # Core Storage
                ps = line.split("Logical Volume on")[1].strip().split(", ")
                disk = self.get_disk(last_disk,disk_dict=diskdump)
                if disk: # Update parent disk
                    disk["container"] = True
                    disk["core_storage"] = True
                    disk["physical_stores"] = ps
                    # Save a reference to the physical stores
                    for s in ps:
                        store = self.get_disk(s,disk_dict=diskdump)
                        if store:
                            store["container_for"] = last_disk
                            store["core_storage_container_for"] = last_disk
            elif line.strip().startswith("Physical Store"):
                # APFS
                ps = line.split("Physical Store")[1].strip().split(", ")
                disk = self.get_disk(last_disk,disk_dict=diskdump)
                if disk: # Update parent disk
                    disk["container"] = True
                    disk["apfs"] = True
                    disk["physical_stores"] = ps
                    # Save a reference to the physical stores
                    for s in ps:
                        store = self.get_disk(s,disk_dict=diskdump)
                        if store:
                            store["container_for"] = last_disk
                            store["apfs_container_for"] = last_disk
        return diskdump

    def get_identifier(self, disk = None, disk_dict = None):
        # Should be able to take a mount point, disk name, or disk identifier,
        # and return the disk's identifier
        if isinstance(disk,dict): disk = disk.get("DAMediaBSDName")
        if not disk: return
        disk_dict = disk_dict or self.disks # Normalize the dict
        disk = disk[6:] if disk.lower().startswith("/dev/rdisk") else disk[5:] if disk.lower().startswith("/dev/disk") else disk
        if disk.lower() in disk_dict.get("AllDisks",[]): return disk
        for d in disk_dict.get("AllDisksAndPartitions", []):
            # Check the parent disk
            if any((disk.lower()==d.get(x,"").lower() for x in ("DAMediaBSDName","DAVolumeName","DAVolumeUUID","DAMediaUUID","DAVolumePath"))):
                return d.get("DAMediaBSDName")
            # Check the partitions
            for p in d.get("Partitions", []):
                if any((disk.lower()==p.get(x,"").lower() for x in ("DAMediaBSDName","DAVolumeName","DAVolumeUUID","DAMediaUUID","DAVolumePath"))):
                    return p.get("DAMediaBSDName")
        # At this point, we didn't find it
        return None

    def get_parent(self, disk = None, disk_dict = None):
        # For backward compatibility with the old disk.py approach
        return self.get_physical_parent_identifiers(disk,disk_dict=disk_dict)

    def get_parent_identifier(self, disk = None, disk_dict = None):
        # Resolves the passed disk value and returns the parent disk/container.
        # i.e. Passing disk5s2s1 would return disk5
        disk = self.get_identifier(disk,disk_dict=disk_dict)
        if not disk: return
        return "disk"+disk.lower().split("disk")[1].split("s")[0]

    def get_physical_parent_identifier(self, disk = None, disk_dict = None):
        # Returns the first hit from get_physical_parent_identifiers()
        return next(iter(self.get_physical_parent_identifiers(disk, disk_dict=disk_dict) or []), None)
        
    def get_physical_parent_identifiers(self, disk = None, disk_dict = None):
        # Resolves the passed disk to the physical parent disk identifiers.  Useful for APFS
        # and Core Storage volumes which are logical - and can span multiple disks.
        # If you have an APFS container on disk4 and its Physical Store lists
        # disk2s2, disk3s2 - this would return [disk2, disk3]
        return [self.get_identifier(x,disk_dict=disk_dict) for x in self.get_physical_parent_disks(disk,disk_dict=disk_dict)]

    def get_physical_parent_disks(self, disk = None, disk_dict = None):
        # Resolves the passed disk to the physical parent disk dicts.  Useful for APFS
        # and Core Storage volumes which are logcial and can span multiple physical
        # disks.  If you have an APFS container on disk4 and its Physical Store is on
        # disk2s2 and disk3s2 - this would return the disk dicts for disk2 and disk3.
        parent = self.get_parent_disk(disk, disk_dict=disk_dict)
        if not parent: return []
        if not "physical_stores" in parent: return [parent]
        return [self.get_parent_disk(x,disk_dict=disk_dict) for x in parent.get("physical_stores",[])]

    def get_parent_disk(self, disk = None, disk_dict = None):
        # Returns the dict info for the parent of the passed mount point, name, identifier, etc
        return self.get_disk(self.get_parent_identifier(disk,disk_dict=disk_dict),disk_dict=disk_dict)

    def get_disk(self, disk = None, disk_dict = None):
        # Returns the dict info for the passed mount point, name, identifier, etc
        disk = self.get_identifier(disk,disk_dict=disk_dict)
        if not disk: return
        parent = self.get_parent_identifier(disk,disk_dict=disk_dict)
        # Walk AllDisksAndPartitions, and return the first hit
        for d in (disk_dict or self.disks).get("AllDisksAndPartitions",[]):
            d_ident = d.get("DAMediaBSDName")
            if d_ident == disk:
                return d # Got the disk
            elif d_ident == parent:
                # Got the parent - iterate the partitions
                return next((p for p in d.get("Partitions",[]) if p.get("DAMediaBSDName")==disk),None)
        return None # Didn't find it

    def get_efis(self, disk = None, disk_dict = None):
        # Returns the identifiers for any EFI partitions attached to the
        # parent disk(s) of the passed disk
        efis = []
        for parent in self.get_physical_parent_identifiers(disk,disk_dict=disk_dict):
            parent_dict = self.get_disk(parent,disk_dict=disk_dict)
            if not parent_dict: continue
            for part in parent_dict.get("Partitions",[]):
                # Use the GUID instead of media name - as that can vary
                if part.get("DAMediaContent","").upper() == "C12A7328-F81F-11D2-BA4B-00A0C93EC93B":
                    efis.append(part["DAMediaBSDName"])
                # Normalize case for the DAMediaName;
                # macOS disks: "EFI System Partition", Windows disks: "EFI system partition"
                # Maybe use this approach as a fallback at some point - but for now, just use the GUID
                # if part.get("DAMediaName").lower() == "efi system partition":
                #     efis.append(part["DAMediaBSDName"])
        return efis

    def get_efi(self, disk = None, disk_dict = None):
        # Returns the identifier for the first EFI partition found for
        # the passed disk
        return next(iter(self.get_efis(disk,disk_dict=disk_dict) or []), None)

    def get_mounted_volumes(self, disk_dict = None):
        # Returns a list of mounted volumes
        return (disk_dict or self.disks).get("MountPointsFromDisks",[])

    def get_mounted_volume_dicts(self, disk_dict = None):
        # Returns a list of dicts of name, identifier, mount point dicts
        vol_list = []
        for v in (disk_dict or self.disks).get("MountPointsFromDisks"):
            i = self.get_disk(v,disk_dict=disk_dict)
            if not i: continue # Skip - as it didn't resolve
            mount_point = self.get_mount_point(i,disk_dict=disk_dict)
            # Check if we're either not mounted - or not mounted in /Volumes/
            if not v or not (v == "/" or v.lower().startswith("/volumes/")):
                continue
            vol = {
                "name": self.get_volume_name(i,disk_dict=disk_dict),
                "identifier": self.get_identifier(i,disk_dict=disk_dict),
                "mount_point": v,
                "disk_uuid": self.get_disk_uuid(i,disk_dict=disk_dict),
                "volume_uuid": self.get_volume_uuid(i,disk_dict=disk_dict)
            }
            if "container_for" in i: vol["container_for"] = i["container_for"]
            vol_list.append(vol)
        return sorted(vol_list,key=lambda x:x["identifier"])

    def get_disks_and_partitions_dict(self, disk_dict = None):
        # Returns a list of dictionaries like so:
        # { "disk0" : { 
        #   "container": true/false,
        #   "physical_stores": [
        #     "diskAsB",
        #     "diskXsY"
        #    ],
        #   "scheme": "Guid_partition_scheme",
        #   "partitions" : [ 
        #    { 
        #      "identifier" : "disk0s1", 
        #      "name" : "EFI", 
        #      "mount_point" : "/Volumes/EFI",
        #      "container_for": "diskCsD"
        #     } 
        #  ] } }
        disks = {}
        for d in sorted((disk_dict or self.disks).get("AllDisksAndPartitions"),key=lambda x:x.get("DAMediaBSDName")):
            if not "DAMediaBSDName" in d: continue # Malformed
            parent = d["DAMediaBSDName"]
            disks[parent] = {"partitions":[]}
            # Save if the disk is logical - and a l)ist of its physical stores
            for x in ("container","physical_stores"):
                if x in d: disks[parent][x] = d[x]
            disks[parent]["scheme"] = self.get_readable_partition_scheme(d,disk_dict=disk_dict)
            # Check if this disk is also a volume - i.e. also a leaf, and insert it in the partitions list
            partitions = d.get("Partitions",[])
            if d.get("DAMediaLeaf"):
                partitions.insert(0,d)
            for p in d.get("Partitions",[]):
                part = {
                    "name": self.get_volume_name(p,disk_dict=disk_dict),
                    "identifier": self.get_identifier(p,disk_dict=disk_dict),
                    "mount_point": self.get_mount_point(p,disk_dict=disk_dict),
                    "disk_uuid": self.get_disk_uuid(p,disk_dict=disk_dict),
                    "volume_uuid": self.get_volume_uuid(p,disk_dict=disk_dict)
                }
                if "container_for" in p: part["container_for"] = p["container_for"]
                disks[parent]["partitions"].append(part)
            disks[parent]["partitions"].sort(key=lambda x:x["identifier"])
        return disks

    def _get_value(self, disk = None, value = None, disk_dict = None):
        if not disk or not value: return # Missing info
        if isinstance(disk,dict): return disk.get(value)
        try: return self.get_disk(disk,disk_dict=disk_dict).get(value)
        except: return

    def _is_uuid(self, value):
        # Helper to return whether a passed value is a UUID
        # 7C3CFDDF-920A-4924-AED6-7CD4AF6E4512
        if not isinstance(value,str): return False # Wrong type
        value = value.lower()
        # Check that all chars are hex or the separator
        if not all((x in "-0123456789abcdef" for x in value)): return False
        len_list = (8,4,4,4,12)
        chunks   = value.split("-")
        # Make sure we have the right number of chunks - and
        # each chunk is the right length.
        if not len(chunks)==len(len_list): return False
        for i,chunk in enumerate(chunks):
            if not len(chunk)==len_list[i]: return False
        # Passed all the checks
        return True

    def get_partition_scheme(self, disk, allow_logical = True, disk_dict = None):
        # let's resolve the disk to its physical parents
        comm = self.get_parent_disk if allow_logical else self.get_physical_parent_disks
        p = comm(disk,disk_dict=disk_dict)
        if p:
            if isinstance(p,(list,tuple)): p = p[0] # Extract the first parent if need be
            if p.get("apfs"): return "APFS_container_scheme"
            elif p.get("core_storage"): return "Core_Storage_container_scheme"
            content = self.get_content(p,disk_dict=disk_dict)
            if content.lower().endswith("scheme"):
                return content

    def get_readable_partition_scheme(self, disk, allow_logical = True, disk_dict = None):
        s = self.get_partition_scheme(disk,disk_dict=disk_dict)
        if not s: return
        # We want to convert GUID_partition_scheme to GUID
        # We also want to translate FDisk to MBR
        joined = " ".join(["MBR" if x.lower() == "fdisk" else x.capitalize() if x!=x.upper() else x for x in s.replace("_"," ").split() if x])
        return joined

    def get_content(self, disk, disk_dict = None):
        # Check if we're on a whole disk first - as we'll need to use the
        if self._get_value(disk,"DAMediaWhole",disk_dict=disk_dict):
            return self._get_value(disk,"DAMediaContent",disk_dict=disk_dict)
        return self._get_value(disk,"DAMediaName",disk_dict=disk_dict)

    def get_volume_name(self, disk, disk_dict = None):
        return self._get_value(disk,"DAVolumeName",disk_dict=disk_dict)

    def get_volume_uuid(self, disk, disk_dict = None):
        return self._get_value(disk,"DAVolumeUUID",disk_dict=disk_dict)

    def get_disk_uuid(self, disk, disk_dict = None):
        return self._get_value(disk,"DAMediaUUID",disk_dict=disk_dict)

    def get_mount_point(self, disk, disk_dict = None):
        return self._get_value(disk,"DAVolumePath",disk_dict=disk_dict)

    def open_mount_point(self, disk, new_window = False, disk_dict = None):
        disk = self.get_identifier(disk,disk_dict=disk_dict)
        if not disk: return
        mount = self.get_mount_point(disk)
        if not mount: return
        return self.r.run({"args":["open", mount]})[2] == 0

    def compare_version(self, v1, v2):
        # Splits the version numbers by periods and compare each value
        # Allows 0.0.10 > 0.0.9 where normal string comparison would return false
        # Also strips out any non-numeric values from each segment to avoid conflicts
        #
        # Returns True if v1 > v2, None if v1 == v2, and False if v1 < v2
        if not all((isinstance(x,str) for x in (v1,v2))):
            # Wrong types
            return False
        v1_seg = v1.split(".")
        v2_seg = v2.split(".")
        # Pad with 0s to ensure common length
        v1_seg += ["0"]*(len(v2_seg)-len(v1_seg))
        v2_seg += ["0"]*(len(v1_seg)-len(v2_seg))
        # Compare each segment - stripping non-numbers as needed
        for i in range(len(v1_seg)):
            a,b = v1_seg[i],v2_seg[i]
            try: a = int("".join([x for x in a if x.isdigit()]))
            except: a = 0
            try: b = int("".join([x for x in b if x.isdigit()]))
            except: b = 0
            if a > b: return True
            if a < b: return False
        # If we're here, both versions are the same
        return None

    def needs_sudo(self, disk = None, disk_dict = None):
        # Default to EFI if we didn't pass a disk
        if not disk: return self.compare_version(self.full_os_version,self.sudo_mount_version) in (True,None)
        return self.compare_version(self.full_os_version,self.sudo_mount_version) in (True,None) and self.get_content(disk,disk_dict=disk_dict).lower() in self.sudo_mount_types

    def mount_partition(self, disk, disk_dict = None):
        disk = self.get_identifier(disk,disk_dict=disk_dict)
        if not disk: return
        sudo = self.needs_sudo(disk,disk_dict=disk_dict)
        out = self.r.run({"args":["diskutil","mount",disk],"sudo":sudo})
        self.update()
        return out

    def unmount_partition(self, disk, disk_dict = None):
        disk = self.get_identifier(disk,disk_dict=disk_dict)
        if not disk: return
        out = self.r.run({"args":["diskutil","unmount",disk]})
        self.update()
        return out

    def is_mounted(self, disk, disk_dict = None):
        disk = self.get_identifier(disk,disk_dict=disk_dict)
        if not disk: return
        m = self.get_mount_point(disk,disk_dict=disk_dict)
        return (m != None and len(m))

    def get_volumes(self, disk_dict = None):
        # Returns a list object with all volumes from disks
        return sorted((disk_dict or self.disks).get("VolumesFromDisks",[]))

if __name__ == '__main__':
    d = Disk()
    # Gather the args
    errors = []
    args = []
    for x in sys.argv[1:]:
        if x == "/":
            args.append(x)
            continue
        if x.endswith("/"):
            x = x[:-1]
        if not x.lower().startswith("/volumes/") or len(x.split("/")) > 3:
            errors.append("'{}' is not a volume.".format(x))
            continue
        if not os.path.exists(x):
            # Doesn't exist, skip it
            errors.append("'{}' does not exist.".format(x))
            continue
        args.append(x)
    mount_list = []
    needs_sudo = d.needs_sudo()
    for x in args:
        name = d.get_volume_name(x)
        if not name: name = "Untitled"
        name = name.replace('"','\\"') # Escape double quotes in names
        efi = d.get_efi(x)
        if efi: mount_list.append((efi,name,d.is_mounted(efi),"diskutil mount {}".format(efi)))
        else: errors.append("'{}' has no ESP.".format(name))
    if mount_list:
        # We have something to mount
        efis =  [x[-1] for x in mount_list if not x[2]] # Only mount those that aren't mounted
        names = [x[1]  for x in mount_list if not x[2]]
        if efis: # We have something to mount here
            command = "do shell script \"{}\" with prompt \"MountEFI would like to mount the ESP{} on {}\"{}".format(
                "; ".join(efis),
                "s" if len(names) > 1 else "",
                ", ".join(names),
                " with administrator privileges" if needs_sudo else "")
            o,e,r = d.r.run({"args":["osascript","-e",command]})
            if r > 0 and len(e.strip()) and e.strip().lower().endswith("(-128)"): exit() # User canceled, bail
            # Update the disks
            d.update()
        # Walk the mounts and find out which aren't mounted
        for efi,name,mounted,comm in mount_list:
            mounted_at = d.get_mount_point(efi)
            if mounted_at: d.open_mount_point(mounted_at)
            else: errors.append("ESP for '{}' failed to mount.".format(name))
    else:
        errors.append("No disks with ESPs selected.")
    if errors:
        # Display our errors before we leave
        d.r.run({"args":["osascript","-e","display dialog \"{}\" buttons {{\"OK\"}} default button \"OK\" with icon caution".format("\n".join(errors))]})
