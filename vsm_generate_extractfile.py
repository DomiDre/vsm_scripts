import numpy as np
import os, os.path, sys

class VSM_GenExtract():
    def __init__(self):
        self.version = 1.1
        self.n_args = len(sys.argv) - 1
        
        self.save_list = []
        self.vhd_list = []
        
        if "-help" in sys.argv or "-h" in sys.argv:
            self.help()
            sys.exit()
            
        if self.n_args < 1:
            print("ERROR: Usage of vsm_generate_extractfile.py:")
            self.help()
            sys.exit()
        self.get_args()
        self.generate_extract_file()
    def help(self):
        print("python vsm_generate_extractfile.py extractfile [..]")
        print("Possible parameters:")
        print("\t-vhd VHDFILE [VHDFILE2 VHDFILE3 ...]")
        print("\t-save SAVETOFILE [SAVETOFILE2 SAVETOFILE3 ...]")
        print("\t-V V \t --\t volume to set ")
        print("\t-extract \t -- \t Directly perform extraction after generating file.")
        print("")

    def get_multiple_args(self, arg):
        jp = sys.argv.index(arg) + 1
        arg_list = []
        while jp <= self.n_args and not sys.argv[jp].startswith("-"):
            next_arg = sys.argv[jp]
            arg_list.append(next_arg)
            jp += 1
        return arg_list

    def check_filelist(self, filelist, suffix="VHD"):
        for ifile, datafile in enumerate(filelist):
            if not os.path.isfile(datafile):

                if os.path.isfile(datafile+"."+suffix):
                    filelist[ifile] = datafile+"."+suffix
                elif os.path.isfile(datafile+suffix):
                    filelist[ifile] = datafile+suffix
                else:
                    print("Could not find file: " + datafile)
        return filelist
        
    def get_args(self):
        if not sys.argv[1].startswith("-"):
            self.extractname = sys.argv[1]
            if not "." in extractname:
                self.extractname += ".dat"
        else:
            self.extractname = "extractVSM.dat"
        
        
        vhd_file_pairlist = []
        if "-vhd" in sys.argv:
            self.vhd_list = self.get_multiple_args("-vhd")
            self.vhd_list = self.check_filelist(self.vhd_list, "VHD")
            
        if "-save" in sys.argv:
            self.save_list = self.get_multiple_args("-save")
            if not len(self.save_list) == len(self.vhd_list):
                print("Not given the same amount of save paths as datafile paths.")
                print("Given VHD Files:")
                for datafile in self.vhd_list:
                    print(datafile)
                print("Given Save Paths:")
                for datafile in self.save_list:
                    print(datafile)
            else:
                for ifile, datafile in enumerate(self.save_list):
                    suffix = datafile.rsplit(".",1)[-1]
                    if suffix == "":
                        self.save_list[ifile] += "xye"
                    elif suffix == datafile:
                        self.save_list[ifile] += ".xye"
        
        if len(self.vhd_list) > 0 and len(self.vhd_list) != len(self.save_list):
            print("Creating own savefile name proposals.")
            self.save_list = []
            for datafile in self.vhd_list:
                if datafile.endswith("-Hys-00.VHD"):
                    savename = datafile.replace("-Hys-00.VHD", ".xye")
                else:
                    savename = datafile.rsplit(".",1)[0]+".xye"
                self.save_list.append(savename)
                
        if "-V" in sys.argv:
            self.V = sys.argv[sys.argv.index("-V")+1]
            self.munit= "kAm-1"
        else:
            self.V = "Not set"
            self.munit ="memu"

    def generate_extract_file(self):
        extract_file = open(self.extractname, "w")
        extract_file.write(\
"# Use this file to give parameters to vsm_dataextract.py\n\
#\n\
# Author: Dominique Dresen\n\
# Contact: Dominique.Dresen@uni-koeln.de\n\
# Version: " + str(self.version) +"\n\
# \n\
# Abbreviations used:\n\
# B -- applied magnetic field\n\
# M -- magnetization of sample\n\
# V -- volume of magnetic sample\n\
\n\
# Parameters for VSM sample evaluation\n\
B_column	Applied Field		#  which column shall be loaded for B\n\
M_column	Raw Signal Mx   	#  which column shall be loaded for M\n\
B_unit		T			#  convert to which magnetic field unit, can choose between: T, mT, Oe\n\
M_unit		"+self.munit+"			#  convert to which magnetization unit, can choose between: Am2, memu, emu, Am-1, kAm-1\n\
noise_level	5e-3			#  noise level of VSM in memu\n\
V		"+self.V+"			#  in mm3 (µL), needed if M_unit is A/m, kA/m, volume of measured magnetic material\n\
\n\
# tell where to load data from and where to save the xy columns to\n\
# if multiple pairs are given, multiple files are created\n\n\
# data_path \t\t\t\t saveto\n\
@start data list\n")
        for ifile, vhdfile in enumerate(self.vhd_list):
            extract_file.write(vhdfile+"\t\t"+self.save_list[ifile]+"\n")
        extract_file.write("@end data list\n\n")
        extract_file.close()
        
if __name__ == "__main__":
    VSM_GenExtract()
