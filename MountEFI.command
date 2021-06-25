#!/usr/bin/env python
# 0.0.0
from Scripts import *
import os, tempfile, datetime, shutil, time, plistlib, json, sys, argparse

class MountEFI:
    def __init__(self, **kwargs):
        self.r  = run.Run()
        self.d  = disk.Disk()
        self.dl = downloader.Downloader()
        self.u  = utils.Utils("MountEFI")
        self.re = reveal.Reveal()
        # Get the tools we need
        self.script_folder = "Scripts"
        self.update_url = "https://raw.githubusercontent.com/corpnewt/MountEFIv2/master/MountEFI.command"
        
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
        self.full = self.settings.get("full_layout", False)

    def check_update(self):
        # Checks against https://raw.githubusercontent.com/corpnewt/MountEFIv2/master/MountEFI.command to see if we need to update
        self.u.head("Checking for Updates")
        print(" ")
        with open(os.path.realpath(__file__), "r") as f:
            # Our version should always be the second line
            version = get_version(f.read())
        print(version)
        try:
            new_text = _get_string(url)
            new_version = get_version(new_text)
        except:
            # Not valid json data
            print("Error checking for updates (network issue)")
            return

        if version == new_version:
            # The same - return
            print("v{} is already current.".format(version))
            return
        # Split the version number
        try:
            v = version.split(".")
            cv = new_version.split(".")
        except:
            # not formatted right - bail
            print("Error checking for updates (version string malformed)")
            return

        if not need_update(cv, v):
            print("v{} is already current.".format(version))
            return

        # Update
        with open(os.path.realpath(__file__), "w") as f:
            f.write(new_text)

        # chmod +x, then restart
        run_command(["chmod", "+x", __file__])
        os.execv(__file__, sys.argv)

    def flush_settings(self):
        if self.settings_file:
            cwd = os.getcwd()
            os.chdir(os.path.dirname(os.path.realpath(__file__)))
            json.dump(self.settings, open(self.settings_file, "w"))
            os.chdir(cwd)

    def after_mount(self):
        if self.settings.get("resize_window"): self.u.resize(80, 24)
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
        clover = bdmesg.get_bootloader_uuid()
        if self.settings.get("resize_window"): self.u.resize(80, 24)
        self.u.head("Select Default Disk")
        print(" ")
        print("1. None")
        print("2. Boot Disk")
        if clover:
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
        elif menu == "3" and clover:
            self.settings["default_disk"] = "clover"
            self.flush_settings()
            return
        elif menu == "m":
            return
        elif menu == "q":
            self.u.custom_quit()
        self.default_disk()

    def get_efi(self):
        self.d.update()
        clover = bdmesg.get_bootloader_uuid()
        i = 0
        disk_string = ""
        if not self.full:
            clover_disk = self.d.get_parent(clover)
            mounts = self.d.get_mounted_volume_dicts()
            for d in mounts:
                i += 1
                disk_string += "{}. {} ({})".format(i, d["name"], d["identifier"])
                if self.d.get_parent(d["identifier"]) == clover_disk:
                # if d["disk_uuid"] == clover:
                    disk_string += " *"
                disk_string += "\n"
        else:
            mounts = self.d.get_disks_and_partitions_dict()
            disks = list(mounts)
            for d in disks:
                i += 1
                disk_string+= "{}. {}:\n".format(i, d)
                parts = mounts[d]["partitions"]
                part_list = []
                for p in parts:
                    p_text = "        - {} ({})".format(p["name"], p["identifier"])
                    if p["disk_uuid"] == clover:
                        # Got Clover
                        p_text += " *"
                    part_list.append(p_text)
                if len(part_list):
                    disk_string += "\n".join(part_list) + "\n"
        height = len(disk_string.split("\n"))+16
        if height < 24:
            height = 24
        if self.settings.get("resize_window"): self.u.resize(80, height)
        self.u.head()
        print(" ")
        print(disk_string)
        if not self.full:
            print("S. Switch to Full Output")
        else:
            print("S. Switch to Slim Output")
        lay = self.settings.get("full_layout", False)
        l_str = "Slim"
        if lay:
            l_str = "Full"
        print("L. Set As Default Layout (Current: {})".format(l_str))
        print("B. Mount the Boot Drive's EFI")
        if clover:
            print("C. Mount the Booted EFI (Clover/OC)")
        print("")

        dd = self.settings.get("default_disk", None)
        if dd == "clover":
            dd = clover
        elif dd == "boot":
            dd = "/"
        di = self.d.get_identifier(dd)
        if di:
            print("D. Pick Default Disk ({} - {})".format(self.d.get_volume_name(di), di))
        else:
            print("D. Pick Default Disk (None Set)")
        
        am = self.settings.get("after_mount", None)
        if not am:
            am = "Return to Menu"
        print("M. After Mounting: "+am)
        print("R. Toggle Window Resizing (Currently {})".format("Enabled" if self.settings.get("resize_window",True) else "Disabled"))
        print("Q. Quit")
        print(" ")
        print("(* denotes the booted EFI (Clover/OC))")

        menu = self.u.grab("Pick the drive containing your EFI:  ")
        if not len(menu):
            if not di:
                return self.get_efi()
            return self.d.get_efi(di)
        menu = menu.lower()
        if menu == "q":
            if self.settings.get("resize_window"): self.u.resize(80,24)
            self.u.custom_quit()
        elif menu == "s":
            self.full ^= True
            return self.get_efi()
        elif menu == "b":
            return self.d.get_efi("/")
        elif menu == "c" and clover:
            return self.d.get_efi(clover)
        elif menu == "m":
            self.after_mount()
            return
        elif menu == "d":
            self.default_disk()
            return
        elif menu == "l":
            self.settings["full_layout"] = self.full
            self.flush_settings()
            return
        elif menu == "r":
            self.settings["resize_window"] = not self.settings.get("resize_window",True)
            self.flush_settings()
            return
        try: disk = mounts[int(menu)-1]["identifier"] if isinstance(mounts, list) else list(mounts)[int(menu)-1]
        except: disk = menu
        iden = self.d.get_identifier(disk)
        name = self.d.get_volume_name(disk)
        if not iden:
            self.u.grab("Invalid disk!", timeout=3)
            return self.get_efi()
        # Valid disk!
        efi = self.d.get_efi(iden)
        if not efi:
            self.u.head("No EFI Partition")
            print("")
            print("There is no EFI partition associated with {}!".format(iden))
            print("")
            self.u.grab("Press returning in 3 seconds...", timeout=3)
            return self.get_efi()
        return efi

    def main(self):
        while True:
            efi = self.get_efi()
            if not efi:
                # Got nothing back
                continue
            # Resize and then mount the EFI partition
            if self.settings.get("resize_window"): self.u.resize(80, 24)
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

    m = MountEFI(settings="./Scripts/settings.json")
    # Gather defaults
    unmount = False
    if args.unmount:
        unmount = True
    if args.print_efi:
        print("{}".format(m.d.get_efi(args.print_efi)))
    # Check for args
    if len(args.disks):
        # We got command line args!
        m.quiet_mount(args.disks, unmount)
    elif not args.print_efi:
        m.main()
