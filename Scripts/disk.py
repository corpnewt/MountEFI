import os, sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__))))
import run, plist

# Info pulled from: https://en.wikipedia.org/wiki/GUID_Partition_Table#Partition_type_GUIDs
GPT_GUIDS = {
    "-": {
      "00000000-0000-0000-0000-000000000000": "Unused entry",
      "024DEE41-33E7-11D3-9D69-0008C781F39F": "MBR",
      "C12A7328-F81F-11D2-BA4B-00A0C93EC93B": "EFI",
      "21686148-6449-6E6F-744E-656564454649": "BIOS boot",
      "D3BFE2DE-3DAF-11DF-BA40-E3A556D89593": "Intel Fast Flash",
      "F4019732-066E-4E12-8273-346C5641494F": "Sony boot",
      "BFBFAFE7-A34F-448A-9A5B-6213EB736C22": "Lenovo boot"
    },
    "Windows": {
      "E3C9E316-0B5C-4DB8-817D-F92DF00215AE": "Microsoft Reserved",
      "EBD0A0A2-B9E5-4433-87C0-68B6B72699C7": "Microsoft basic data",
      "5808C8AA-7E8F-42E0-85D2-E1E90434CFB3": "Logical Disk Manager metadata",
      "AF9B60A0-1431-4F62-BC68-3311714A69AD": "Logical Disk Manager data",
      "DE94BBA4-06D1-4D40-A16A-BFD50179D6AC": "Windows Recovery",
      "37AFFC90-EF7D-4E96-91C3-2D7AE055B174": "IBM General Parallel File System",
      "E75CAF8F-F680-4CEE-AFA3-B001E56EFC2D": "Storage Spaces",
      "558D43C5-A1AC-43C0-AAC8-D1472B2923D1": "Storage Replica"
    },
    "HP-UX": {
      "75894C1E-3AEB-11D3-B7C1-7B03A0000000": "Data",
      "E2A1E728-32E3-11D6-A682-7B03A0000000": "Service"
    },
    "Linux": {
      "0FC63DAF-8483-4772-8E79-3D69D8477DE4": "Linux filesystem data",
      "A19D880F-05FC-4D3B-A006-743F0F84911E": "RAID",
      "44479540-F297-41B2-9AF7-D131D5F0458A": "Root (x86)",
      "4F68BCE3-E8CD-4DB1-96E7-FBCAF984B709": "Root (x86-64)",
      "69DAD710-2CE4-4E3C-B16C-21A1D49ABED3": "Root (32-bit ARM)",
      "B921B045-1DF0-41C3-AF44-4C6F280D3FAE": "Root (64-bit ARM/AArch64)",
      "BC13C2FF-59E6-4262-A352-B275FD6F7172": "/boot",
      "0657FD6D-A4AB-43C4-84E5-0933C84B4F4F": "Swap",
      "E6D6D379-F507-44C2-A23C-238F2A3DF928": "Logical Volume Manager",
      "933AC7E1-2EB4-4F13-B844-0E14E2AEF915": "/home",
      "3B8F8425-20E0-4F3B-907F-1A25A76F98E8": "/srv",
      "7FFEC5C9-2D00-49B7-8941-3EA10A5586B7": "Plain dm-crypt",
      "CA7D7CCB-63ED-4C53-861C-1742536059CC": "LUKS",
      "8DA63339-0007-60C0-C436-083AC8230908": "Reserved"
    },
    "FreeBSD": {
      "83BD6B9D-7F41-11DC-BE0B-001560B84F0F": "Boot",
      "516E7CB4-6ECF-11D6-8FF8-00022D09712B": "BSD disklabel",
      "516E7CB5-6ECF-11D6-8FF8-00022D09712B": "Swap",
      "516E7CB6-6ECF-11D6-8FF8-00022D09712B": "Unix File System",
      "516E7CB8-6ECF-11D6-8FF8-00022D09712B": "Vinum volume manager",
      "516E7CBA-6ECF-11D6-8FF8-00022D09712B": "ZFS",
      "74BA7DD9-A689-11E1-BD04-00E081286ACF": "nandfs"
    },
    "macOS Darwin": {
      "48465300-0000-11AA-AA11-00306543ECAC": "Apple HFS+",
      "7C3457EF-0000-11AA-AA11-00306543ECAC": "Apple APFS container",
      "55465300-0000-11AA-AA11-00306543ECAC": "Apple UFS container",
      "6A898CC3-1DD2-11B2-99A6-080020736631": "ZFS",
      "52414944-0000-11AA-AA11-00306543ECAC": "Apple RAID",
      "52414944-5F4F-11AA-AA11-00306543ECAC": "Apple RAID, offline",
      "426F6F74-0000-11AA-AA11-00306543ECAC": "Apple Boot",
      "4C616265-6C00-11AA-AA11-00306543ECAC": "Apple Label",
      "5265636F-7665-11AA-AA11-00306543ECAC": "Apple TV Recovery",
      "53746F72-6167-11AA-AA11-00306543ECAC": "Apple Core Storage Container",
      "69646961-6700-11AA-AA11-00306543ECAC": "Apple APFS Preboot",
      "52637672-7900-11AA-AA11-00306543ECAC": "Apple APFS Recovery"
    },
    "Solaris illumos": {
      "6A82CB45-1DD2-11B2-99A6-080020736631": "Boot",
      "6A85CF4D-1DD2-11B2-99A6-080020736631": "Root",
      "6A87C46F-1DD2-11B2-99A6-080020736631": "Swap",
      "6A8B642B-1DD2-11B2-99A6-080020736631": "Backup",
      "6A898CC3-1DD2-11B2-99A6-080020736631": "/usr",
      "6A8EF2E9-1DD2-11B2-99A6-080020736631": "/var",
      "6A90BA39-1DD2-11B2-99A6-080020736631": "/home",
      "6A9283A5-1DD2-11B2-99A6-080020736631": "Alternate sector",
      "6A945A3B-1DD2-11B2-99A6-080020736631": "Reserved",
      "6A9630D1-1DD2-11B2-99A6-080020736631": "Reserved",
      "6A980767-1DD2-11B2-99A6-080020736631": "Reserved",
      "6A96237F-1DD2-11B2-99A6-080020736631": "Reserved",
      "6A8D2AC7-1DD2-11B2-99A6-080020736631": "Reserved"
    },
    "NetBSD": {
      "49F48D32-B10E-11DC-B99B-0019D1879648": "Swap",
      "49F48D5A-B10E-11DC-B99B-0019D1879648": "FFS",
      "49F48D82-B10E-11DC-B99B-0019D1879648": "LFS",
      "49F48DAA-B10E-11DC-B99B-0019D1879648": "RAID",
      "2DB519C4-B10F-11DC-B99B-0019D1879648": "Concatenated",
      "2DB519EC-B10F-11DC-B99B-0019D1879648": "Encrypted"
    },
    "ChromeOS": {
      "FE3A2A5D-4F32-41A7-B725-ACCC3285A309": "ChromeOS kernel",
      "3CB8E202-3B7E-47DD-8A3C-7FF2A13CFCEC": "ChromeOS rootfs",
      "CAB6E88E-ABF3-4102-A07A-D4BB9BE3C1D3": "ChromeOS firmware",
      "2E0A753D-9E48-43B0-8337-B15192CB1B5E": "ChromeOS future use",
      "09845860-705F-4BB5-B16C-8A8A099CAF52": "ChromeOS miniOS",
      "3F0F8318-F146-4E6B-8222-C28C8F02E0D5": "ChromeOS hibernate"
    },
    "Container Linux by CoreOS": {
      "5DFBF5F4-2848-4BAC-AA5E-0D9A20B745A6": "/usr",
      "3884DD41-8582-4404-B9A8-E9B84F2DF50E": "Resizable rootfs",
      "C95DC21A-DF0E-4340-8D7B-26CBFA9A03E0": "OEM customizations",
      "BE9067B9-EA49-4F15-B4F6-F36F8C9E1818": "Root filesystem on RAID"
    },
    "Haiku": {
      "42465331-3BA3-10F1-802A-4861696B7521": "Haiku BFS"
    },
    "MidnightBSD": {
      "85D5E45E-237C-11E1-B4B3-E89A8F7FC3A7": "Boot",
      "85D5E45A-237C-11E1-B4B3-E89A8F7FC3A7": "Data",
      "85D5E45B-237C-11E1-B4B3-E89A8F7FC3A7": "Swap",
      "0394EF8B-237E-11E1-B4B3-E89A8F7FC3A7": "Unix File System",
      "85D5E45C-237C-11E1-B4B3-E89A8F7FC3A7": "Vinum volume manager",
      "85D5E45D-237C-11E1-B4B3-E89A8F7FC3A7": "ZFS"
    },
    "Ceph": {
      "45B0969E-9B03-4F30-B4C6-B4B80CEFF106": "Journal",
      "45B0969E-9B03-4F30-B4C6-5EC00CEFF106": "dm-crypt journal",
      "4FBD7E29-9D25-41B8-AFD0-062C0CEFF05D": "OSD",
      "4FBD7E29-9D25-41B8-AFD0-5EC00CEFF05D": "dm-crypt OSD",
      "89C57F98-2FE5-4DC0-89C1-F3AD0CEFF2BE": "Disk in creation",
      "89C57F98-2FE5-4DC0-89C1-5EC00CEFF2BE": "dm-crypt disk in creation",
      "CAFECAFE-9B03-4F30-B4C6-B4B80CEFF106": "Block",
      "30CD0809-C2B2-499C-8879-2D6B78529876": "Block DB",
      "5CE17FCE-4087-4169-B7FF-056CC58473F9": "Block write-ahead log",
      "FB3AABF9-D25F-47CC-BF5E-721D1816496B": "Lockbox for dm-crypt keys",
      "4FBD7E29-8AE0-4982-BF9D-5A8D867AF560": "Multipath OSD",
      "45B0969E-8AE0-4982-BF9D-5A8D867AF560": "Multipath journal",
      "CAFECAFE-8AE0-4982-BF9D-5A8D867AF560": "Multipath block",
      "7F4A666A-16F3-47A2-8445-152EF4D03F6C": "Multipath block",
      "EC6D6385-E346-45DC-BE91-DA2A7C8B3261": "Multipath block DB",
      "01B41E1B-002A-453C-9F17-88793989FF8F": "Multipath block write-ahead log",
      "CAFECAFE-9B03-4F30-B4C6-5EC00CEFF106": "dm-crypt block",
      "93B0052D-02D9-4D8A-A43B-33A3EE4DFBC3": "dm-crypt block DB",
      "306E8683-4FE2-4330-B7C0-00A917C16966": "dm-crypt block write-ahead log",
      "45B0969E-9B03-4F30-B4C6-35865CEFF106": "dm-crypt LUKS journal",
      "CAFECAFE-9B03-4F30-B4C6-35865CEFF106": "dm-crypt LUKS block",
      "166418DA-C469-4022-ADF4-B30AFD37F176": "dm-crypt LUKS block DB",
      "86A32090-3647-40B9-BBBD-38D8C573AA86": "dm-crypt LUKS block write-ahead log",
      "4FBD7E29-9D25-41B8-AFD0-35865CEFF05D": "dm-crypt LUKS OSD"
    },
    "OpenBSD": {
      "824CC7A0-36A8-11E3-890A-952519AD3F61": "Data"
    },
    "QNX": {
      "CEF5A9AD-73BC-4601-89F3-CDEEEEE321A1": "Power-safe (QNX6) file system"
    },
    "Plan 9": {
      "C91818F9-8025-47AF-89D2-F030D7000C2C": "Plan 9"
    },
    "VMware ESX": {
      "9D275380-40AD-11DB-BF97-000C2911D1B8": "vmkcore",
      "AA31E02A-400F-11DB-9590-000C2911D1B8": "VMFS filesystem",
      "9198EFFC-31C0-11DB-8F78-000C2911D1B8": "VMware Reserved"
    },
    "Android-IA": {
      "2568845D-2332-4675-BC39-8FA5A4748D15": "Bootloader",
      "114EAFFE-1552-4022-B26E-9B053604CF84": "Bootloader2",
      "49A4D17F-93A3-45C1-A0DE-F50B2EBE2599": "Boot",
      "4177C722-9E92-4AAB-8644-43502BFD5506": "Recovery",
      "EF32A33B-A409-486C-9141-9FFB711F6266": "Misc",
      "20AC26BE-20B7-11E3-84C5-6CFDB94711E9": "Metadata",
      "38F428E6-D326-425D-9140-6E0EA133647C": "System",
      "A893EF21-E428-470A-9E55-0668FD91A2D9": "Cache",
      "DC76DDA9-5AC1-491C-AF42-A82591580C0D": "Data",
      "EBC597D0-2053-4B15-8B64-E0AAC75F4DB1": "Persistent",
      "C5A0AEEC-13EA-11E5-A1B1-001E67CA0C3C": "Vendor",
      "BD59408B-4514-490D-BF12-9878D963F378": "Config",
      "8F68CC74-C5E5-48DA-BE91-A0C8C15E9C80": "Factory",
      "9FDAA6EF-4B3F-40D2-BA8D-BFF16BFB887B": "Factory",
      "767941D0-2085-11E3-AD3B-6CFDB94711E9": "Fastboot / Tertiary",
      "AC6D7924-EB71-4DF8-B48D-E267B27148FF": "OEM"
    },
    "Android 6.0+ ARM": {
      "19A710A2-B3CA-11E4-B026-10604B889DCF": "Android Meta",
      "193D1EA4-B3CA-11E4-B075-10604B889DCF": "Android EXT"
    },
    "Open Network Install Environment (ONIE)": {
      "7412F7D5-A156-4B13-81DC-867174929325": "Boot",
      "D4E6E2CD-4469-46F3-B5CB-1BFF57AFC149": "Config"
    },
    "PowerPC": {
      "9E1A2D38-C612-4316-AA26-8B49521E5A8B": "PReP boot"
    },
    "freedesktop.org OSes (Linux, etc.)": {
      "BC13C2FF-59E6-4262-A352-B275FD6F7172": "Shared boot loader configuration"
    },
    "Atari TOS": {
      "734E5AFE-F61A-11E6-BC64-92361F002671": "Basic data"
    },
    "VeraCrypt": {
      "8C8F8EFF-AC95-4770-814A-21994F2DBC8F": "Encrypted data"
    },
    "OS/2": {
      "90B6FF38-B98F-4358-A21F-48F35B4A8AD3": "ArcaOS Type 1"
    },
    "Storage Performance Development Kit (SPDK)": {
      "7C5222BD-8F5D-4087-9C00-BF9843C7B58C": "SPDK block device"
    },
    "barebox bootloader": {
      "4778ED65-BF42-45FA-9C5B-287A1DC4AAB1": "barebox-state"
    },
    "U-Boot bootloader": {
      "3DE21764-95BD-54BD-A5C3-4ABE786F38A8": "U-Boot"
    },
    "SoftRAID": {
      "B6FA30DA-92D2-4A9A-96F1-871EC6486200": "SoftRAID_Status",
      "2E313465-19B9-463F-8126-8A7993773801": "SoftRAID_Scratch",
      "FA709C7E-65B1-4593-BFD5-E71D61DE9B02": "SoftRAID_Volume",
      "BBBA6DF5-F46F-4A89-8F59-8765B2727503": "SoftRAID_Cache"
    },
    "Fuchsia standard partitions": {
      "FE8A2634-5E2E-46BA-99E3-3A192091A350": "Bootloader",
      "D9FD4535-106C-4CEC-8D37-DFC020CA87CB": "Durable mutable encrypted system data",
      "A409E16B-78AA-4ACC-995C-302352621A41": "Durable mutable bootloader data",
      "F95D940E-CABA-4578-9B93-BB6C90F29D3E": "Factory-provisioned read-only system data",
      "10B8DBAA-D2BF-42A9-98C6-A7C5DB3701E7": "Factory-provisioned read-only bootloader data",
      "49FD7CB8-DF15-4E73-B9D9-992070127F0F": "Fuchsia Volume Manager",
      "421A8BFC-85D9-4D85-ACDA-B64EEC0133E9": "Verified boot metadata",
      "9B37FFF6-2E58-466A-983A-F7926D0B04E0": "Zircon boot image"
    },
    "Fuchsia legacy partitions": {
      "C12A7328-F81F-11D2-BA4B-00A0C93EC93B": "fuchsia-esp",
      "606B000B-B7C7-4653-A7D5-B737332C899D": "fuchsia-system",
      "08185F0C-892D-428A-A789-DBEEC8F55E6A": "fuchsia-data",
      "48435546-4953-2041-494E-5354414C4C52": "fuchsia-install",
      "2967380E-134C-4CBB-B6DA-17E7CE1CA45D": "fuchsia-blob",
      "41D0E340-57E3-954E-8C1E-17ECAC44CFF5": "fuchsia-fvm",
      "DE30CC86-1F4A-4A31-93C4-66F147D33E05": "Zircon boot image",
      "23CC04DF-C278-4CE7-8471-897D1A4BCDF7": "Zircon boot image",
      "A0E5CF57-2DEF-46BE-A80C-A2067C37CD49": "Zircon boot image",
      "4E5E989E-4C86-11E8-A15B-480FCF35F8E6": "sys-config",
      "5A3A90BE-4C86-11E8-A15B-480FCF35F8E6": "factory-config",
      "5ECE94FE-4C86-11E8-A15B-480FCF35F8E6": "bootloader",
      "8B94D043-30BE-4871-9DFA-D69556E8C1F3": "guid-test",
      "A13B4D9A-EC5F-11E8-97D8-6C3BE52705BF": "Verified boot metadata",
      "A288ABF2-EC5F-11E8-97D8-6C3BE52705BF": "Verified boot metadata",
      "6A2460C3-CD11-4E8B-80A8-12CCE268ED0A": "Verified boot metadata",
      "1D75395D-F2C6-476B-A8B7-45CC1C97B476": "misc",
      "900B0FC5-90CD-4D4F-84F9-9F8ED579DB88": "emmc-boot1",
      "B2B2E8D1-7C10-4EBC-A2D0-4614568260AD": "emmc-boot2"
    }
}

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
        self.efi_guids = ["C12A7328-F81F-11D2-BA4B-00A0C93EC93B"]
        self.disks = self.get_disks()

    def is_guid(self, guid = None):
        try:
            guid_parts = guid.split("-")
            assert len(guid_parts) == 5
            assert len(guid_parts[0]) == 8
            assert all((len(x) == 4 for x in guid_parts[1:4]))
            assert len(guid_parts[-1]) == 12
            assert all((x in "0123456789ABCDEF" for x in "".join(guid_parts)))
        except: # Not a GUID - return
            return False
        return True

    def get_size(self, size, suffix=None, use_1024=False, round_to=1, strip_zeroes=True):
        # size is the number of bytes
        # suffix is the target suffix to locate (B, KB, MB, etc) - if found
        # use_2014 denotes whether or not we display in MiB vs MB
        # round_to is the number of dedimal points to round our result to (0-15)
        # strip_zeroes denotes whether we strip out zeroes 

        # Failsafe in case our size is unknown
        if size == -1:
            return "Unknown"
        # Get our suffixes based on use_1024
        ext = ["B","KiB","MiB","GiB","TiB","PiB"] if use_1024 else ["B","KB","MB","GB","TB","PB"]
        div = 1024 if use_1024 else 1000
        s = float(size)
        s_dict = {} # Initialize our dict
        # Iterate the ext list, and divide by 1000 or 1024 each time to setup the dict {ext:val}
        for e in ext:
            s_dict[e] = s
            s /= div
        # Get our suffix if provided - will be set to None if not found, or if started as None
        suffix = next((x for x in ext if x.lower() == suffix.lower()),None) if suffix else suffix
        # Get the largest value that's still over 1
        biggest = suffix if suffix else next((x for x in ext[::-1] if s_dict[x] >= 1), "B")
        # Determine our rounding approach - first make sure it's an int; default to 2 on error
        try:round_to=int(round_to)
        except:round_to=2
        round_to = 0 if round_to < 0 else 15 if round_to > 15 else round_to # Ensure it's between 0 and 15
        bval = round(s_dict[biggest], round_to)
        # Split our number based on decimal points
        a,b = str(bval).split(".")
        # Check if we need to strip or pad zeroes
        b = b.rstrip("0") if strip_zeroes else b.ljust(round_to,"0") if round_to > 0 else ""
        return "{:,}{} {}".format(int(a),"" if not b else "."+b,biggest)

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
                if part.get("DAMediaContent","").upper() in self.efi_guids:
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

    def get_partition_type(self, disk = None, disk_dict = None):
        # Checks if we have a matched DAMediaContent GUID in the GPT_GUIDS dict, and returns
        # the resolved type.  If it doesn't match - and is a GUID, we return it as is.  If it's
        # not a GUID - we return none.
        disk = self.get_disk(disk,disk_dict=disk_dict)
        if not disk: return
        guid = disk.get("DAMediaContent","").upper()
        # Ensure we have a GUID
        if not self.is_guid(guid): return
        # At this point - we have a GUID
        for os in GPT_GUIDS:
            if guid in GPT_GUIDS[os]:
                return GPT_GUIDS[os][guid]
        # We didn't find it - return the GUID as-is
        return guid

    def get_volume_type(self, disk = None, disk_dict = None):
        # Returns teh DAVolumeType or DAVolumeKind of the passed disk if any
        disk = self.get_disk(disk,disk_dict=disk_dict)
        if not disk: return
        if "DAVolumeType" in disk: return disk["DAVolumeType"]
        if "DAVolumeKind" in disk: return disk["DAVolumeKind"].upper()

    def get_readable_type(self, disk = None, disk_dict = None):
        # Attempts to get the type of the passed disk.  First - it tries to get the
        # partition type, then it falls back on the volume type.
        disk = self.get_disk(disk,disk_dict=disk_dict)
        if not disk: return
        if disk.get("DAMediaWhole") and not disk.get("DAMediaLeaf"):
            # Check if we have a partition scheme and return that
            scheme = self.get_readable_partition_scheme(disk,disk_dict=disk_dict)
            if scheme: return scheme
        part = self.get_partition_type(disk,disk_dict=disk_dict)
        if part and not self.is_guid(part): # We got a valid partition type
            return part
        vol = self.get_volume_type(disk,disk_dict=disk_dict)
        # Return the volume type - if we got one - or the partition type, whatever
        # it may be.
        return vol or part

    def get_readable_size(self, disk = None, disk_dict = None):
        # Returns the readable, rounded (to one decimal point) size of the passed disk
        disk = self.get_disk(disk,disk_dict=disk_dict)
        if not disk or not "DAMediaSize" in disk: return "Unknown"
        return self.get_size(disk["DAMediaSize"])

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
                "volume_uuid": self.get_volume_uuid(i,disk_dict=disk_dict),
                "size_bytes": i.get("DAMediaSize",-1),
                "size": self.get_readable_size(i,disk_dict=disk_dict),
                "type": self.get_readable_type(i,disk_dict=disk_dict)
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
        #   "size": "X.Y GB",
        #   "size_bytes" 123456,
        #   "partitions" : [ 
        #    { 
        #      "identifier" : "disk0s1", 
        #      "name" : "EFI", 
        #      "mount_point" : "/Volumes/EFI",
        #      "size": "X.Y GB",
        #      "size_bytes" 123456,
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
            disks[parent]["size_bytes"] = d.get("DAMediaSize",-1)
            disks[parent]["size"] = self.get_readable_size(d,disk_dict=disk_dict)
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
                    "volume_uuid": self.get_volume_uuid(p,disk_dict=disk_dict),
                    "type": self.get_readable_type(p,disk_dict=disk_dict),
                    "size_bytes": p.get("DAMediaSize",-1),
                    "size": self.get_readable_size(p,disk_dict=disk_dict)
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
        return self._get_value(disk,"DAMediaContent",disk_dict=disk_dict)

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
        return self.compare_version(self.full_os_version,self.sudo_mount_version) in (True,None) and self.get_content(disk,disk_dict=disk_dict).upper() in self.efi_guids

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
