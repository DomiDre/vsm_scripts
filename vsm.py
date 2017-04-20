import sys
import numpy as np

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
    
    def get_data_from_file(self, filepath):
        datafile = open(filepath, "r")
        B = []
        M = []
        sM = []
        Mraw = []
        sMraw = []
        header = ""
        self.Bunit = ""
        self.Munit = ""
        last_line = ""
        loading_header = True
        for line in datafile:
            if loading_header:
                header += last_line
                last_line = line
            
            if line.startswith('#B') or line.startswith('# B'):
                loading_header = False
                split_line = line.strip().split("#")[1].split("\t")
                for element in split_line:
                    if "B /" in element or "B_sub /" in element or "B_res /" in element:
                        self.Bunit = element.split("/")[1].strip()
                    elif "M /" in element or "M_sub /" in element or "B_res /" in element:
                        self.Munit = element.split("/")[1].strip()
                    elif "B_raw /" in element:
                        self.Brawunit = element.split("/")[1].strip()
                    elif "M_raw /" in element:
                        self.Mrawunit = element.split("/")[1].strip()
                continue
            
            if line.startswith("#") or line.strip() == "":
                continue
            
            loading_header = False
            splitline = line.strip().split()
            B.append(float(splitline[0]))
            M.append(float(splitline[1]))
            sM.append(float(splitline[2]))
            Mraw.append(float(splitline[-2]))
            sMraw.append(float(splitline[-1]))
        return B, M, sM, Mraw, sMraw, header
    
    def load_xye_vsmfile(self, filepath):
        B, M, sM, Mraw, sMraw, header = self.get_data_from_file(filepath)
        self.B = np.asarray(B)
        self.M = np.asarray(M)
        self.sM = np.asarray(sM)
        self.Mraw = np.asarray(Mraw)
        self.sMraw = np.asarray(sMraw)
        self.header = header
