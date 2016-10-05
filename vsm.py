import sys

class VSMClass():
    def __init__(self):
        self.version = 1.1
        self.n_args = len(sys.argv) - 1
        self.get_args()
        if "-help" in sys.argv or "-h" in sys.argv:
            self.help()
            sys.exit()
            
    def get_args(self):
        self.arg_dict = {}
        for ip, param in enumerate(sys.argv):
            if param.startswith("-"):
                jp = ip + 1
                param_list = []
                while jp <= self.n_args and not sys.argv[jp].startswith("-"):
                    param_list.append(sys.argv[jp])
                    jp += 1
                if len(param_list) == 1:
                    param_list = param_list[0]
                self.arg_dict[param[1:]] = param_list
            else:
                continue
                
    def help(self):
        print("Help is not defined.")
