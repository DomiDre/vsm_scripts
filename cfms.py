import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import inspect
import sys

class CFMS():
    def __init__(self):
        self.data_loaded = False
        self.data_averaged = False
        self.log = ""
        self.__version__ = 0.1
        self.__author__ ="Dominique Dresen"
        
    def print_help(self):
        print("CFMS DataExtractor version " + str(self.__version__))
        print("Usage: cfms.py PATH_TO_DAT [..]")
        
        print("Possible parameters:")
        print("--")
        
        print("\nFor more professional usage: generate class and use "+\
              "provided class members to load/manipulate CFMS data:")
        print(inspect.getmembers(CFMS, predicate=inspect.ismethod))
        
    def load(self, datfile):
        self.data_loaded = True
        self.datfile = datfile
        datafile = open(datfile, "r")
        self.print_and_log("Loading data from " + str(datfile))
        self.header = datafile.readline().rstrip().split()
        
        self.data = {}
        self.print_and_log("")
        self.print_and_log("Found columns:")
        for datahead in self.header:
            self.print_and_log(str(datahead))
            self.data[datahead] = []
            
        for line in datafile:
            linestrip = line.strip()
            if linestrip.startswith("#") or linestrip == "":
                continue
            split_line = linestrip.split()
            for i, val in enumerate(split_line):
                self.data[self.header[i]].append(float(val))
        datafile.close()
        
        self.print_and_log("")
        
        for datahead in self.data:
            self.data[datahead] = np.asarray(self.data[datahead])

        if "moment_(emu)" in self.data:
            self.data["moment_(emu)"] *= 1e3
            self.print_and_log("Transformed data from column 'moment_(emu)' "+\
                               "from emu to memu by multiplication with 1000.")

        self.data_loaded = True
        self.N_pts = len(self.data[self.header[0]])
        self.print_and_log("Loaded "+ str(self.N_pts) + " datapoints.")

    def print_and_log(self, print_string):
        self.log += "#" + print_string + "\n"
        print(print_string)
        
    def reduce_averages(self, n_averages):
        self.n_averages = n_averages
        self.print_and_log("Averaging data, combining every " + str(n_averages) +\
                           " points.")
        self.B_avg = []
        self.sB_avg = []

        self.M_avg = []
        self.sM_avg = []

        self.T_avg = []
        self.sT_avg = []
        
        B = self.get_B()
        M = self.get_M()
        T = self.get_T()
        for i in range(0, self.N_pts, self.n_averages):
            cur_b_avg = B[i:i+self.n_averages]
            cur_m_avg = M[i:i+self.n_averages]
            cur_t_avg = T[i:i+self.n_averages]
            if len(cur_b_avg) != self.n_averages or \
                    len(cur_m_avg) != self.n_averages or \
                    len(cur_t_avg) != self.n_averages:
                self.print_and_log("Skipped line "+ str(i)+\
                            ": Does not commensurate.")
                continue
            self.B_avg.append(np.mean(cur_b_avg))
            self.sB_avg.append(np.std(cur_b_avg,ddof=1))
            self.M_avg.append(np.mean(cur_m_avg))
            self.sM_avg.append(np.std(cur_m_avg,ddof=1))
            self.T_avg.append(np.mean(cur_t_avg))
            self.sT_avg.append(np.std(cur_t_avg,ddof=1))
            
        self.data_averaged = True
        self.B_avg = np.asarray(self.B_avg)
        self.sB_avg = np.asarray(self.sB_avg)

        self.M_avg = np.asarray(self.M_avg)
        self.sM_avg = np.asarray(self.sM_avg)

        self.T_avg = np.asarray(self.T_avg)
        self.sT_avg = np.asarray(self.sT_avg)
        self.N_pts_avg = len(self.B_avg)
        self.print_and_log("Average data contains " + str(self.N_pts_avg) +\
                           " data points.")

    def get_B(self):
        if not self.data_loaded:
            sys.exit("ERROR: Load data before calling get_B")
        data_string = "B_analog_(T)"
        if not data_string in self.data:
            sys.exit("ERROR: Unable to find " + data_string + " in data.")
        return self.data[data_string]

    def get_M(self):
        if not self.data_loaded:
            sys.exit("ERROR: Load data before calling get_M")
        data_string = "moment_(emu)"
        if not data_string in self.data:
            sys.exit("ERROR: Unable to find " + data_string + " in data.")
        return self.data[data_string]

    def get_T(self):
        if not self.data_loaded:
            sys.exit("ERROR: Load data before calling get_T")
        data_string = "sensor_B_(K)"
        return self.data[data_string]

    def get_Bavg(self):
        if not self.data_averaged:
            sys.exit("ERROR: Average data before calling get_Bavg")
        return self.B_avg, self.sB_avg

    def get_Mavg(self):
        if not self.data_averaged:
            sys.exit("ERROR: Average data before calling get_Mavg")
        return self.M_avg, self.sM_avg

    def get_Tavg(self):
        if not self.data_averaged:
            sys.exit("ERROR: Average data before calling get_Tavg")
        return self.T_avg, self.sT_avg

    def plot_B_M(self):
        fig, ax = plt.subplots()
        ax.plot(self.get_B(), self.get_M())
        
        ax.set_xlabel("$ \mathit{B} \, / \, T$")
        ax.set_ylabel("$ \mathit{M} \, / \, memu$")
        fig.tight_layout()
        saveplot = self.datfile.rsplit(".",1)[0] + "_BM.png"
        fig.savefig(saveplot)
        print("Saved plot to " + saveplot)

    def plot_B_M_avg(self):
        fig, ax = plt.subplots()
        B, sB = self.get_Bavg()
        M, sM = self.get_Mavg()
        valid_points = sM/M < 1e-1
        B = B[valid_points]
        sB = sB[valid_points]
        M = M[valid_points]
        sM = sM[valid_points]
        ax.errorbar(B, M, xerr=sB, yerr=sM)
        
        ax.set_xlabel("$ \mathit{B} \, / \, T$")
        ax.set_ylabel("$ \mathit{M} \, / \, memu$")
        fig.tight_layout()
        saveplot = self.datfile.rsplit(".",1)[0] + "_BMavg.png"
        fig.savefig(saveplot)
        print("Saved plot to " + saveplot)
        
    def plot_T_M(self):
        fig, ax = plt.subplots()
        ax.plot(self.get_T(), self.get_M())
        
        ax.set_xlabel("$ \mathit{T} \, / \, K$")
        ax.set_ylabel("$ \mathit{M} \, / \, memu$")
        fig.tight_layout()
        saveplot = self.datfile.rsplit(".",1)[0] + "_TM.png"
        fig.savefig(saveplot)
        print("Saved plot to " + saveplot)
    
    def export_avg(self, export_file=None):
        if export_file is None:
            export_file = self.datfile.rsplit(".",1)[0]+"_extracted.xye"
        
        B, sB = self.get_Bavg()
        M, sM = self.get_Mavg()
        T, sT = self.get_Tavg()

        self.print_and_log("Export averaged data to " + export_file)
        savefile = open(export_file, "w")
        
        savefile.write(self.log)
        savefile.write("#\n#B / T\tsB / T\tM / memu\tsM / memu\tT / K\tsT / K\n")
        for i in range(self.N_pts_avg):
            savefile.write(str(B[i]) + "\t" +\
                       str(sB[i]) + "\t" +\
                       str(M[i]) + "\t" +\
                       str(sM[i]) + "\t" +\
                       str(T[i]) + "\t" +\
                       str(sT[i]) + "\n")
        savefile.close()
    
    def show(self): 
        plt.show()

if __name__ == "__main__":
    n_args = len(sys.argv) - 1
    cfms_data = CFMS()
    if n_args > 0:
        cfms_data.load(sys.argv[1])
        
        cfms_data.reduce_averages(10)
        cfms_data.export_avg()
    #    cfms_data.plot_B_M_avg()
    #    cfms_data.plot_T_M()
    #    cfms_data.plot_B_M()
        plt.show()
    else:
        cfms_data.print_help()
