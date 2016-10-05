import numpy as np
import sys, os, os.path, time
from vsm import VSMClass

class VSM_Extract(VSMClass):
    def __init__(self, filepath=None):
        super().__init__()
        
        if self.n_args < 1 and filepath is None:
            print("Give path to file containing parameters for VSM "+\
                  "data extraction as argument.")
            print("Usage of vsm_dataextract.py:")
            self.help()
            sys.exit()
        if filepath is not None:
            self.filepath = filepath
        
        self.B_units = {"Oe": 1E4, "mT": 1E3, "T": 1}
        self.M_units = {"Am2": 1E-6, "emu": 1E-3, "memu": 1, "Am-1": 1E-6,\
                        "kAm-1":1E-9}

        self.log_string = ""
        self.load_param_file()

    def help(self):
        print("python vsm_dataextract.py parameter_file [..]")
        print("Possible parameters:")
        print("\tNone")
        print("")

    def get_args(self):
        if self.n_args > 0:
            self.filepath = sys.argv[1]

    def load_param_file(self):
        self.pdict = {}
        self.samplelist = []
        #  Start Reading parameter file
        start_load_datapaths = False
        pfile = open(self.filepath, "r")
        self.log_string += "#Loaded parameter file: " + str(self.filepath) + "\n"
        for line in pfile:
            if line.startswith('#'):  # skip comment lines which start with #
                continue
            if '@start' in line:  # flag switches from parameter reading to datapaths reading
                start_load_datapaths = True
                continue
            if '@end' in line:  # flag switches from parameter reading to datapaths reading
                start_load_datapaths = False
                continue
            split_line = line.split('#')[0].strip().split(maxsplit=1)  # remove everything after # and split between first empty spaces/tabs
            if len(split_line) < 2:
                continue
            if not start_load_datapaths:  # First load parameters, structure Name Value, then load paths
                self.pdict[split_line[0]] = split_line[1]
            else:
                if not os.path.isfile(split_line[0]):  # does sample file exist?
                    sys.exit("Datapath does not exist. Entered path: " + split_line[0])
                self.samplelist.append((split_line[0], split_line[1]))
        pfile.close()

        #  End of reading parameter file
        def check_if_parameter_loaded(pdict, pname, pdescription):
            if not pname in pdict:
                sys.exit("Define parameter for " + pdescription +": " + pname)
        check_if_parameter_loaded(self.pdict, "B_column", "column name of B")
        check_if_parameter_loaded(self.pdict, "M_column", "column name of M")
        check_if_parameter_loaded(self.pdict, "B_unit", "unit of B")
        check_if_parameter_loaded(self.pdict, "M_unit", "unit of M")
        check_if_parameter_loaded(self.pdict, "noise_level", "noiselevel of magnetometer")

        if not self.pdict["B_unit"] in self.B_units:  # check if B units are known
            sys.exit("Define unit of B.")
        else:
            self.B_unit_factor = self.B_units[self.pdict["B_unit"]]
        
        if not self.pdict["M_unit"] in self.M_units:  # check if M units are known
            sys.exit("Define unit of M.")
        else:
            self.M_unit_factor = self.M_units[self.pdict["M_unit"]]
            if self.pdict["M_unit"] in {"Am-1", "kAm-1"}:  # check if volume is entered correctly for rescaling
                if not "V" in self.pdict:
                    sys.exit("You selected " + self.pdict["M_unit"] + " as unit. You need to define the volume of the magnetic sample as parameter V.")
                else:
                    try:
                        self.pdict["V"] = float(self.pdict["V"])
                    except ValueError:
                        sys.exit("The entered volume is not a number.")
                    self.M_unit_factor /= (self.pdict["V"]*1e-9)
        print("Desired unit of B: " +self.pdict["B_unit"])
        self.log_string += "#Desired unit of B: " + self.pdict["B_unit"] + "\n"
        print("Desired unit of M: " +self.pdict["M_unit"])
        self.log_string += "#Desired unit of M: " + self.pdict["M_unit"] + "\n"
        self.log_string += "#Reading column for B: " + self.pdict["B_column"] + "\n"
        self.log_string += "#Reading column for M: " + self.pdict["M_column"] + "\n"
        self.log_string += "#Estimate noise level: " + self.pdict["noise_level"] + " memu\n"
    
        for samplepair in self.samplelist:
            self.data_string = "#Loading data from file: " + samplepair[0] + "\n"
            self.data_string = "#Save data to file: " + samplepair[1] + "\n"
            self.data_string = "#Extraction performed at: " +  time.strftime("%c") + "\n"
            
            B, M, sM, M_raw, sM_raw, M_rawunit, B_imagecorr, imagecorr_factor =\
                        self.load_data(samplepair[0]) # Load Data
            
            #Save data 
            save_data = open(samplepair[1], "w")
            save_data.write("#Extracted data using VSM extraction tool v"+\
                    str(self.version)+" \n")
            save_data.write(self.log_string)
            save_data.write(self.data_string)
            
            save_data.write("\n#B / "+self.pdict["B_unit"]+"\tM / "+self.pdict["M_unit"] +\
                    "\tsM / "+self.pdict["M_unit"]+"\tMraw / "+M_rawunit +"\tsMraw / "+\
                    M_rawunit + "\n")
                    
            for i, bval in enumerate(B):
                save_data.write(str(bval) + "\t" + str(M[i]) + "\t" + str(sM[i]) +\
                    "\t" + str(M_raw[i]) + "\t" + str(sM_raw[i]) + "\n")
            save_data.close()
                
            print("Saved data from "+samplepair[0]+" to: " + samplepair[1])
            print("\n")
            
    def load_data(self, file_path):
        B_col, M_col, B_rawunit, M_rawunit =\
            self.load_columns(file_path, self.pdict["B_column"], self.pdict["M_column"])
        B_raw, M_raw, B_imagecorr, imagecorr_factor =\
            self.load_data_from_VHD_file(file_path, B_col, M_col)
        
        self.data_string += "#Unit of B in data: " + B_rawunit + "\n"
        self.data_string += "#Changing unit by multiplying with factor: " + str(self.B_unit_factor / self.B_units[B_rawunit]) + "\n"
        self.data_string += "#Unit of M in data: " + M_rawunit + "\n"
        m_change_factor = self.M_unit_factor / self.M_units[M_rawunit]
        if not np.allclose(m_change_factor, 1):
    ö        self.data_string += "#Changing unit by multiplying with factor: " + str(m_change_factor) + "\n"
        M = M_raw * self.M_unit_factor / self.M_units[M_rawunit]
        
        # image correct M_values
        if len(B_imagecorr) > 0:
            for i, B_value in enumerate(B_raw):
                B_value = abs(B_value)
                if B_value < B_imagecorr[0]:
                    continue
                
                if B_value >= B_imagecorr[-1]:
                    corr_fac = imagecorr_factor[-1]
                elif B_value == B_imagecorr[0]:
                    corr_fac = imagecorr_factor[0]
                else:
                    for ib, B_imagecorrs in enumerate(B_imagecorr):
                        if B_imagecorrs > B_value:
                            dB = B_imagecorr[ib] - B_imagecorr[ib-1]
                            corr_fac =\
                                imagecorr_factor[ib-1] *(B_imagecorr[ib] - B_value)/dB +\
                                imagecorr_factor[ib] *(B_value - B_imagecorr[ib-1])/dB
                            break
                M[i] *= corr_fac
                

            print("Applied image correction Factors to magnetization.")
            self.data_string += "#Applied image correction factors to M by "+\
                                "linear interpolation of following values\n"
            for i, bval in enumerate(B_imagecorr):
                self.data_string += "#"+str(bval) + "\t" + str(imagecorr_factor[i]) + "\n"
        else:
            print("Failed to load correction values.")
            self.data_string += "#Failed to perform image correction\n"
        
        B = B_raw * self.B_unit_factor / self.B_units[B_rawunit]
        
        #sM in raw units
        sM_raw = float(self.pdict["noise_level"]) * np.ones(len(M_raw)) * self.M_units[M_rawunit]/self.M_units["memu"]
        
        #sM in desired units
        sM = sM_raw * self.M_unit_factor / self.M_units[M_rawunit]
        print("Applied factor to change unit of magnetic field:", self.B_unit_factor / self.B_units[B_rawunit])
        print("Applied factor to change unit of magnetization:", self.M_unit_factor / self.M_units[M_rawunit])
        return B, M, sM, M_raw, sM_raw, M_rawunit, B_imagecorr, imagecorr_factor

    def load_data_from_VHD_file(self, filename, B_column, M_column):
        print("Loading", filename)
        datafile = open(filename, 'r')
        B = []
        M = []
        
        B_imagecorr = []
        imagecorr_factor = []
        read_flag = False
        read_image_correction_flag = False
        for line in datafile:
            if line.startswith("#"):
                continue
                
            if line.startswith('@@Data'):
                read_flag = True
                continue
                
            if line.startswith('Image Correction'):
                read_image_correction_flag = True
                continue
            if read_image_correction_flag:
                try:
                    split_line = line.split('#')[0].strip().split()
                    if len(split_line) < 2:
                        read_image_correction_flag = False
                        continue
                    b_val = float(split_line[0])
                    corr_val = float(split_line[1])
                    B_imagecorr.append(b_val)
                    imagecorr_factor.append(corr_val)
                except:
                    read_image_correction_flag = False
                    continue
                    
            if read_flag:
                if line.startswith('New Section: Section 0:'):
                    continue
                if line.startswith('@@END Data.'):
                    break
                split_line = line.split('#')[0].strip().split()
                B.append(float(split_line[B_column]))
                M.append(float(split_line[M_column]))
        datafile.close()
        
        return np.asarray(B), np.asarray(M),\
               np.array(B_imagecorr), np.array(imagecorr_factor)


    def load_columns(self, filename, search_string_B, search_string_M):
        print("Searching for columns in", filename)
        datafile = open(filename, 'r')
        read_columns=False
        list_of_columns = []
        for line in datafile:
            if "@Column Contents:" in line:
                read_columns=True
                continue
            elif "@@END Columns" in line:
                break

            if read_columns:
                if line.startswith("Column"):
                    list_of_columns.append(line)
        datafile.close()

        B_int = -1
        M_int = -1

        #print("Column structure of datafile:")
        for int_line, line in enumerate(list_of_columns):
            #print(line,)
            if search_string_B in line:
                B_int = int_line
            elif search_string_M in line:
                M_int = int_line
        # Found both?
        if B_int == -1:
            sys.exit(search_string_B + " not found in " + filename)
        if M_int == -1:
            sys.exit(search_string_M + " not found in " + filename)

        B_unit = list_of_columns[B_int].strip().split("[")[-1].split("]")[0]
        M_unit = list_of_columns[M_int].strip().split("[")[-1].split("]")[0]
        print("Selected column for B: " +str(list_of_columns[B_int].strip()))
        print("Recognized unit:", B_unit)
        print("Selected column for M: " +str(list_of_columns[M_int].strip()))
        print("Recognized unit:", M_unit)

        return B_int, M_int, B_unit, M_unit



if __name__ == "__main__":
    VSM_Extract()

