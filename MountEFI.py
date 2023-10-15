#!/usr/bin/env python
# 0.0.0
from Scripts import *
import os, tempfile, datetime, shutil, time, plistlib, json, sys, argparse

class MountEFI:
    def __init__(self, **kwargs):
        self.r = run.Run()
        self.u = utils.Utils("MountEFI")
        if not kwargs.get("quiet"):
            # Give some feedback in case we have slow disks - particularly annoying
            # when waiting on an APFS volume formatted in a newer OS while we're booted
            # in an older OS.
            self.u.head("MountEFI")
            print("\nWaiting for disks...")
            print("\nIf you see this message for a long while, you may have a disk that is")
            print("slow or malfunctioning - causing \"diskdump\" to stall.")
            print("")
            print("Note: APFS volumes created on newer OS versions (10.14+) can cause stalls")
            print("when accessed on older macOS versions (10.13 and prior).  They will appear")
            print("eventually, but may take several minutes.")
        self.d = disk.Disk()
        self.boot_manager = bdmesg.get_bootloader_uuid()
        # Get the tools we need
        self.script_folder = "Scripts"        
        self.settings_file = kwargs.get("settings", None)
        cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if self.settings_file and os.path.exists(self.settings_file):
            self.settings = json.load(open(self.settings_file))
        else:
            self.settings = {
                # Default settings here
                "default_disk" : None,
                "after_mount"  : None,
                "full_layout"  : False,
                "skip_countdown" : False,
            }
        os.chdir(cwd)

    def flush_settings(self):
        if self.settings_file:
            cwd = os.getcwd()
            os.chdir(os.path.dirname(os.path.realpath(__file__)))
            json.dump(self.settings, open(self.settings_file, "w"), indent=2)
            os.chdir(cwd)

    def after_mount(self):
        if self.settings.get("resize_window",True): self.u.resize(80, 24)
        self.u.head("After Mount Action")
        print(" ")
        print("1. Return to Menu")
        print("2. Quit")
        print("3. Open EFI and Return to Menu")
        print("4. Open EFI and Quit")
        if not self.settings.get("skip_countdown", False):
            print("5. Skip After-Mount Countdown")
        else:
            print("5. Use After-Mount Countdown")
        print(" ")
        print("M. Main Menu")
        print("Q. Quit")
        print(" ")
        menu = self.u.grab("Please pick an option:  ")
        if not len(menu):
            self.after_mount()
            return
        menu = menu.lower()
        if menu in ["1","2","3","4"]:
            self.settings["after_mount"] = [
                "Return to Menu", 
                "Quit", 
                "Reveal and Return to Menu", 
                "Reveal and Quit"
                ][int(menu)-1]
            self.flush_settings()
            return
        elif menu == "5":
            cd = self.settings.get("skip_countdown", False)
            cd ^= True
            self.settings["skip_countdown"] = cd
            self.flush_settings()
            self.after_mount()
            return
        elif menu == "m":
            return
        elif menu == "q":
            self.u.custom_quit()
        self.after_mount()

    def default_disk(self):
        self.d.update()
        if self.settings.get("resize_window",True): self.u.resize(80, 24)
        self.u.head("Select Default Disk")
        print(" ")
        print("1. None")
        print("2. Boot Disk")
        if self.boot_manager:
            print("3. Booted EFI (Clover/OC)")
        print(" ")
        print("M. Main Menu")
        print("Q. Quit")
        print(" ")
        menu = self.u.grab("Please pick a default disk:  ")
        if not len(menu):
            self.default_disk()
        menu = menu.lower()
        if menu in ["1","2"]:
            self.settings["default_disk"] = [None, "boot"][int(menu)-1]
            self.flush_settings()
            return
        elif menu == "3" and self.boot_manager:
            self.settings["default_disk"] = "clover"
            self.flush_settings()
            return
        elif menu == "m":
            return
        elif menu == "q":
            self.u.custom_quit()
        self.default_disk()

    def get_efi(self):
        while True:
            self.d.update()
            pad = 4
            disk_string = "\n"
            if not self.settings.get("full_layout"):
                boot_disk = self.d.get_parent(self.boot_manager)
                mounts = self.d.get_mounted_volume_dicts()
                # Gather some formatting info
                name_pad = size_pad = type_pad = 0
                index_pad = len(str(len(mounts)))
                for x in mounts:
                    if len(str(x["name"])) > name_pad: name_pad = len(str(x["name"]))
                    if len(x["size"]) > size_pad: size_pad = len(x["size"])
                    if len(str(x["readable_type"])) > type_pad: type_pad = len(str(x["readable_type"]))
                for i,d in enumerate(mounts,start=1):
                    disk_string += "{}. {} | {} | {} | {}".format(
                        str(i).rjust(index_pad),
                        str(d["name"]).ljust(name_pad),
                        d["size"].rjust(size_pad),
                        str(d["readable_type"]).ljust(type_pad),
                        d["identifier"]
                    )
                    if self.d.get_parent(d["identifier"]) == boot_disk:
                        disk_string += " *"
                    disk_string += "\n"
            else:
                mounts = self.d.get_disks_and_partitions_dict()
                disks = list(mounts)
                index_pad = len(str(len(disks)))
                # Gather some formatting info
                name_pad = size_pad = type_pad = 0
                for d in disks:
                    for x in mounts[d]["partitions"]:
                        name = "Container for {}".format(x["container_for"]) if "container_for" in x else str(x["name"])
                        if len(name) > name_pad: name_pad = len(name)
                        if len(x["size"]) > size_pad: size_pad = len(x["size"])
                        if len(str(x["readable_type"])) > type_pad: type_pad = len(str(x["readable_type"]))
                for i,d in enumerate(disks,start=1):
                    disk_string+= "{}. {} ({}):\n".format(
                        str(i).rjust(index_pad),
                        d,
                        mounts[d]["size"]
                    )
                    if mounts[d].get("scheme"):
                        disk_string += "      {}\n".format(mounts[d]["scheme"])
                    if mounts[d].get("physical_stores"):
                        disk_string += "      Physical Store{} on {}\n".format(
                            "" if len(mounts[d]["physical_stores"])==1 else "s",
                            ", ".join(mounts[d]["physical_stores"])
                        )
                    parts = mounts[d]["partitions"]
                    part_list = []
                    for p in parts:
                        name = "Container for {}".format(p["container_for"]) if "container_for" in p else p["name"]
                        p_text = "        - {} | {} | {} | {}".format(
                            str(name).ljust(name_pad),
                            p["size"].rjust(size_pad),
                            str(p["readable_type"]).ljust(type_pad),
                            p["identifier"]
                        )
                        if p["disk_uuid"] == self.boot_manager:
                            # Got boot manager
                            p_text += " *"
                        part_list.append(p_text)
                    if len(part_list):
                        disk_string += "\n".join(part_list) + "\n"
            disk_string += "\nS. Switch to {} Output\n".format("Slim" if self.settings.get("full_layout") else "Full")
            disk_string += "B. Mount the Boot Drive's EFI\n"
            if self.boot_manager:
                disk_string += "C. Mount the Booted EFI (Clover/OC)\n"
            disk_string += "L. Show diskutil list Output\n"
            dd = self.settings.get("default_disk")
            dd = self.boot_manager if dd=="clover" else "/" if dd=="boot" else dd
            di = self.d.get_identifier(dd)
            disk_string += "\nD. Pick Default Disk ({})\n".format(
                "{} - {}".format(self.d.get_volume_name(di),di) if di else "None Set"
            )
            am = self.settings.get("after_mount","Return to Menu")
            disk_string += "M. After Mounting: {}\n".format(am)
            disk_string += "R. Toggle Window Resizing (Currently {})\nQ. Quit\n".format("Enabled" if self.settings.get("resize_window",True) else "Disabled")
            if self.boot_manager:
                disk_string += "\n(* denotes the booted EFI (Clover/OC))"
            height = max(len(disk_string.split("\n"))+pad,24)
            width  = max((len(x) for x in disk_string.split("\n")))
            if self.settings.get("resize_window",True): self.u.resize(max(80,width), height)
            self.u.head()
            print(disk_string)
            menu = self.u.grab("Pick the drive containing your EFI:  ")
            if not len(menu):
                if not di:
                    continue
                return self.d.get_efi(di)
            menu = menu.lower()
            if menu == "q":
                if self.settings.get("resize_window",True): self.u.resize(80,24)
                self.u.custom_quit()
            elif menu == "s":
                self.settings["full_layout"] = not self.settings.get("full_layout")
                self.flush_settings()
                continue
            elif menu == "b":
                disk = "/"
            elif menu == "c" and self.boot_manager:
                disk = self.boot_manager
            elif menu == "l":
                self.u.head("MountEFI")
                print("\nWaiting for disks...")
                print("\nIf you see this message for a long while, you may have a disk that is")
                print("slow or malfunctioning - causing \"diskutil\" to stall.")
                print("")
                print("Note: APFS volumes created on newer OS versions (10.14+) can cause stalls")
                print("when accessed on older macOS versions (10.13 and prior).  They will appear")
                print("eventually, but may take several minutes.")
                try: diskutil_list = self.r.run({"args":["diskutil","list"]})[0]
                except: diskutil_list = ""
                dl_message = "\n"+(diskutil_list or "diskutil list output was not found!").strip()+"\n"
                if self.settings.get("resize_window",True):
                    self.u.resize(80,max(len(dl_message.split("\n"))+pad,24))
                self.u.head("Diskutil List Output")
                print(dl_message)
                self.u.grab("Press [enter] to return...")
                continue
            elif menu == "m":
                self.after_mount()
                continue
            elif menu == "d":
                self.default_disk()
                continue
            elif menu == "r":
                self.settings["resize_window"] = not self.settings.get("resize_window",True)
                self.flush_settings()
                continue
            else:
                try: disk = mounts[int(menu)-1]["identifier"] if isinstance(mounts, list) else list(mounts)[int(menu)-1]
                except: disk = menu
            iden = self.d.get_identifier(disk)
            if not iden:
                self.u.head("Invalid Disk")
                print("")
                print("'{}' is not a valid disk!".format(disk))
                print("")
                self.u.grab("Returning in 5 seconds...", timeout=5)
                continue
            # Valid disk!
            efi = self.d.get_efi(iden)
            if not efi:
                self.u.head("No EFI Partition")
                print("")
                print("There is no EFI partition associated with {}!".format(iden))
                print("")
                self.u.grab("Returning in 5 seconds...", timeout=5)
                continue
            return efi

    def main(self):
        while True:
            efi = self.get_efi()
            if not efi:
                # Got nothing back
                continue
            # Resize and then mount the EFI partition
            if self.settings.get("resize_window",True): self.u.resize(80, 24)
            self.u.head("Mounting {}".format(efi))
            print(" ")
            out = self.d.mount_partition(efi)
            if out[2] == 0:
                print(out[0])
            else:
                print(out[1])
            # Check our settings
            am = self.settings.get("after_mount", None)
            if not am:
                continue
            if "reveal" in am.lower():
                # Reveal
                mp = self.d.get_mount_point(efi)
                if mp:
                    self.r.run({"args":["open", mp]})
            # Hang out for a couple seconds
            if not self.settings.get("skip_countdown", False):
                self.u.grab("", timeout=3)
            if "quit" in am.lower():
                # Quit
                self.u.custom_quit()

    def quiet_mount(self, disk_list, unmount=False):
        ret = 0
        for disk in disk_list:
            ident = self.d.get_identifier(disk)
            if not ident:
                continue
            efi = self.d.get_efi(ident)
            if not efi:
                continue
            if unmount:
                out = self.d.unmount_partition(efi)
            else:
                out = self.d.mount_partition(efi)
            if not out[2] == 0:
                ret = out[2]
        exit(ret)

if __name__ == '__main__':
    # Setup the cli args
    parser = argparse.ArgumentParser(prog="MountEFI.command", description="MountEFI - an EFI Mounting Utility by CorpNewt")
    parser.add_argument("-u", "--unmount", help="unmount instead of mount the passed EFIs", action="store_true")
    parser.add_argument("-p", "--print-efi", help="prints the disk#s# of the EFI attached to the passed var")
    parser.add_argument("disks",nargs="*")

    args = parser.parse_args()

    # Determine if we need to print the warning about disk stalls
    quiet = True if args.print_efi or args.disks else False
    m = MountEFI(settings="./Scripts/settings.json",quiet=quiet)
    # Gather defaults
    unmount = False
    if args.unmount:
        unmount = True
    if args.print_efi:
        print("{}".format(m.d.get_efi(args.print_efi)))
    # Check for args
    if args.disks:
        # We got command line args!
        m.quiet_mount(args.disks, unmount)
    elif not args.print_efi:
        m.main()
