import os, sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__))))
import run, utils

class Rebuild:
    def __init__(self):
        self.r = run.Run()
        return

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

    def rebuild(self, stream = True):
        # Get os version
        os_vers = self.r.run({"args":["sw_vers", "-productVersion"]})[0]
        if self._compare_versions(os_vers, "10.11.0") == True:
            # We're on an OS version prior to 10.11
            return self.r.run({"args":"sudo touch /System/Library/Extensions && sudo kextcache -u /", "stream" : stream, "shell" : True})
        else:
            # 10.11 or above
            return self.r.run({"args":"sudo kextcache -i / && sudo kextcache -u /", "stream" : stream, "shell" : True})