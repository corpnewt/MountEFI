import sys, os, time, re, json, datetime

if os.name == "nt":
    # Windows
    import msvcrt
else:
    # Not Windows \o/
    import select

class Utils:

    def __init__(self, name = "Python Script"):
        self.name = name
        # Init our colors before we need to print anything
        cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if os.path.exists("colors.json"):
            self.colors_dict = json.load(open("colors.json"))
        else:
            self.colors_dict = {}
        os.chdir(cwd)

    def compare_versions(self, vers1, vers2, pad = -1):
        # Helper method to compare ##.## strings
        #
        # vers1 < vers2 = True
        # vers1 = vers2 = None
        # vers1 > vers2 = False
        #
        # Must be separated with a period
        
        # Sanitize the pads
        pad = -1 if not type(pad) is int else pad
        
        # Cast as strings
        vers1 = str(vers1)
        vers2 = str(vers2)
        
        # Split to lists
        v1_parts = vers1.split(".")
        v2_parts = vers2.split(".")
        
        # Equalize lengths
        if len(v1_parts) < len(v2_parts):
            v1_parts.extend([str(pad) for x in range(len(v2_parts) - len(v1_parts))])
        elif len(v2_parts) < len(v1_parts):
            v2_parts.extend([str(pad) for x in range(len(v1_parts) - len(v2_parts))])
        
        # Iterate and compare
        for i in range(len(v1_parts)):
            # Remove non-numeric
            v1 = ''.join(c for c in v1_parts[i] if c.isdigit())
            v2 = ''.join(c for c in v2_parts[i] if c.isdigit())
            # If empty - make it a pad var
            v1 = pad if not len(v1) else v1
            v2 = pad if not len(v2) else v2
            # Compare
            if int(v1) < int(v2):
                return True
            elif int(v1) > int(v2):
                return False
        # Never differed - return None, must be equal
        return None
        
    def check_path(self, path):
        # Loop until we either get a working path - or no changes
        count = 0
        while count < 100:
            count += 1
            if not len(path):
                # We uh.. stripped out everything - bail
                return None
            if os.path.exists(path):
                # Exists!
                return os.path.abspath(path)
            # Check quotes first
            if (path[0] == '"' and path[-1] == '"') or (path[0] == "'" and path[-1] == "'"):
                path = path[1:-1]
                continue
            # Check for tilde
            if path[0] == "~":
                test_path = os.path.expanduser(path)
                if test_path != path:
                    # We got a change
                    path = test_path
                    continue
            # If we have no spaces to trim - bail
            if not (path[0] == " " or path[0] == "  ") and not(path[-1] == " " or path[-1] == " "):
                return None
            # Here we try stripping spaces/tabs
            test_path = path
            t_count = 0
            while t_count < 100:
                t_count += 1
                t_path = test_path
                while len(t_path):
                    if os.path.exists(t_path):
                        return os.path.abspath(t_path)
                    if t_path[-1] == " " or t_path[-1] == "    ":
                        t_path = t_path[:-1]
                        continue
                    break
                if test_path[0] == " " or test_path[0] == " ":
                    test_path = test_path[1:]
                    continue
                break
            # Escapes!
            test_path = "\\".join([x.replace("\\", "") for x in path.split("\\\\")])
            if test_path != path and not (path[0] == " " or path[0] == "  "):
                path = test_path
                continue
            if path[0] == " " or path[0] == "  ":
                path = path[1:]
        return None

    def grab(self, prompt, **kwargs):
        # Takes a prompt, a default, and a timeout and shows it with that timeout
        # returning the result
        timeout = kwargs.get("timeout", 0)
        default = kwargs.get("default", None)
        # If we don't have a timeout - then skip the timed sections
        if timeout <= 0:
            if sys.version_info >= (3, 0):
                return input(prompt)
            else:
                return str(raw_input(prompt))
        # Write our prompt
        sys.stdout.write(prompt)
        sys.stdout.flush()
        if os.name == "nt":
            start_time = time.time()
            i = ''
            while True:
                if msvcrt.kbhit():
                    c = msvcrt.getche()
                    if ord(c) == 13: # enter_key
                        break
                    elif ord(c) >= 32: #space_char
                        i += c
                if len(i) == 0 and (time.time() - start_time) > timeout:
                    break
        else:
            i, o, e = select.select( [sys.stdin], [], [], timeout )
            if i:
                i = sys.stdin.readline().strip()
        print('')  # needed to move to next line
        if len(i) > 0:
            return i
        else:
            return default

    def cls(self):
    	os.system('cls' if os.name=='nt' else 'clear')

    def cprint(self, message, **kwargs):
        strip_colors = kwargs.get("strip_colors", False)
        if os.name == "nt":
            strip_colors = True
        reset = u"\u001b[0m"
        # Requires sys import
        for c in self.colors:
            if strip_colors:
                message = message.replace(c["find"], "")
            else:
                message = message.replace(c["find"], c["replace"])
        if strip_colors:
            return message
        sys.stdout.write(message)
        print(reset)

    # Needs work to resize the string if color chars exist
    '''# Header drawing method
    def head(self, text = None, width = 55):
        if text == None:
            text = self.name
        self.cls()
        print("  {}".format("#"*width))
        len_text = self.cprint(text, strip_colors=True)
        mid_len = int(round(width/2-len(len_text)/2)-2)
        middle = " #{}{}{}#".format(" "*mid_len, len_text, " "*((width - mid_len - len(len_text))-2))
        if len(middle) > width+1:
            # Get the difference
            di = len(middle) - width
            # Add the padding for the ...#
            di += 3
            # Trim the string
            middle = middle[:-di]
            newlen = len(middle)
            middle += "...#"
            find_list = [ c["find"] for c in self.colors ]

            # Translate colored string to len
        middle = middle.replace(len_text, text + self.rt_color) # always reset just in case
        self.cprint(middle)
        print("#"*width)'''

    # Header drawing method
    def head(self, text = None, width = 55):
        if text == None:
            text = self.name
        self.cls()
        print("  {}".format("#"*width))
        mid_len = int(round(width/2-len(text)/2)-2)
        middle = " #{}{}{}#".format(" "*mid_len, text, " "*((width - mid_len - len(text))-2))
        if len(middle) > width+1:
            # Get the difference
            di = len(middle) - width
            # Add the padding for the ...#
            di += 3
            # Trim the string
            middle = middle[:-di] + "...#"
        print(middle)
        print("#"*width)

    def resize(self, width, height):
        print('\033[8;{};{}t'.format(height, width))

    def custom_quit(self):
        self.head()
        print("by CorpNewt\n")
        print("Thanks for testing it out, for bugs/comments/complaints")
        print("send me a message on Reddit, or check out my GitHub:\n")
        print("www.reddit.com/u/corpnewt")
        print("www.github.com/corpnewt\n")
        # Get the time and wish them a good morning, afternoon, evening, and night
        hr = datetime.datetime.now().time().hour
        if hr > 3 and hr < 12:
            print("Have a nice morning!\n\n")
        elif hr >= 12 and hr < 17:
            print("Have a nice afternoon!\n\n")
        elif hr >= 17 and hr < 21:
            print("Have a nice evening!\n\n")
        else:
            print("Have a nice night!\n\n")
        exit(0)
