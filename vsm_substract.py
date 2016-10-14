import numpy as np
import sys, os.path
import matplotlib.pyplot as plt
from vsm import VSMClass

class VSM_Substract(VSMClass):
    def __init__(self):
        super().__init__()
        print("Loading " + self.sample_path)
        self.load_xye_vsmfile(self.sample_path)
        
        if self.substract_pbp:
            self.substract_data()
            self.
        else:
            self.substract_linear()
            self.save_to_file_linear_substraction()
            self.plot_substraction_linear()
        
    def substract_linear(self):
        self.M_sub = self.M - self.sf*self.slope*self.B
        self.sM_sub = np.sqrt(self.sM**2 + (self.sf*self.sigma_slope*self.B)**2)

    def compare_B_values(self, B1, B2):
        """Check if B lists contain both the same B values"""
        #Same amount of data points?
        if not len(B1) == len(B2):
            print("WARNING: Different length in B values observed.")

        #Same values?
        for int_B, B_value in enumerate(B1):
            if not np.isclose(B_value, B2[int_B], rtol=0.001, atol=0.001):
                print("WARNING:",B_value, " is not equal to ", B2[int_B])
                print("WARNING: Check whether signal and background have been "+\
                      "measured with the same magnetic field steps.")
                      
    def substract_data(self, B1, M1, sM1, B2, M2, sM2, sf):
        self.compare_B_values(B1, B2)
        B = B1
        M = M1 - sf*M2
        sM = np.sqrt(sM1**2 + sf**2*sM2**2)
        return B, M, sM
        
    def save_to_file_linear_substraction(self):
        save_data = open(self.save_to, "w")
        save_data.write(self.header)
        save_data.write("#Substracted file: " +self.sample_path+"\n")
        save_data.write("#Using Slope: " + str(self.slope) + "\n")
        save_data.write("#BG Scalefactor: " + str(self.sf) + "\n")
        save_data.write("#BG Sigma Slope: " + str(self.sigma_slope) + "\n")
        
        save_data.write("#B / "+self.Bunit+\
                        "\tM_sub / "+self.Munit+\
                        "\tsM_sub / "+ self.Munit+\
                        "\tM_extracted / "+self.Munit+\
                        "\tsM_extracted / "+ self.Munit+\
                        "\tM_raw / "+self.Mrawunit+\
                        "\tsM_raw / "+ self.Mrawunit+"\n")
        for i, bval in enumerate(self.B):
            save_data.write(str(bval)+"\t"+\
                            str(self.M_sub[i])+"\t"+\
                            str(self.sM_sub[i])+"\t"+\
                            str(self.M[i])+"\t"+\
                            str(self.sM[i])+"\t"+\
                            str(self.Mraw[i])+"\t"+\
                            str(self.sMraw[i])+"\n")
        save_data.close()

    def plot_substraction_linear(self):
        if self.Munit == "kAm-1":
            Munit = "kAm^{-1}"
        else:
            Munit = self.Munit
        fig, ax = plt.subplots()
        ax.axhline(0, color='black')
        ax.axvline(0, color='black')
        ax.errorbar(self.B, self.Mraw, self.sMraw, label=self.pre+" + Bg")
        bg_label = "Bg: "+str(self.slope)+" "+Munit+"/"+self.Bunit+" * B"
        if not self.sf == 1.:
            bg_label = str(self.sf) +"*"+ bg_label
        ax.errorbar(self.B, self.sf*self.slope*self.B,\
                    self.sigma_slope*np.ones(len(self.B)),\
                    label=bg_label)
        ax.errorbar(self.B, self.M_sub, self.sM_sub, label=self.pre)
        ax.set_xlabel("$\mathit{B} \, / \, "+self.Bunit+"$")
        ax.set_ylabel("$\mathit{M} \, / \, "+Munit+"$")

        ax.set_xlim([min(self.B), max(self.B)])
        ax.set_ylim([1.5*min(self.M), 1.5*max(self.M)])
        
        plt.legend(loc='best', fontsize=8).draw_frame(True)

        fig.savefig(self.plot_path)
        plt.show()
        
    def help(self):
        print("python vsm_substract.py samplefile [SLOPE/SUBSTRACTFILE] [saveto] [..]")
        print("\nIf second number is a number, this slope will be substracted linearly "+\
              "(m_bg=slope*B). Otherwise if it is an existing .xye file, substracting takes place "+\
              "point by point with nearest neighbor approximation.")
        print("Possible Parameters:")
        print("-sf \t -- \t Apply scale factor at substraction m = m_s - sf*m_bg")
        print("-sig SIGMASLOPE\t -- \t Increase error by systematic error.")
        print("-saveto SAVEPATH\t -- \t Save data to SAVEPATH.")

        
    def get_args(self):
        # Initialization:
        if self.n_args <= 1:
            print("Error: Usage of substract linear script:")
            self.help() 
            sys.exit()
        
        self.sample_path = sys.argv[1]
        
        try:
            self.slope = float(sys.argv[2])
            self.substract_pbp = False
        except (TypeError, ValueError):
            if os.path.isfile(sys.argv[2]):
                self.bg_path = sys.argv[2]
                self.substract_pbp = True
            else:
                print("ERROR: Second argument must either be a number or a filepath.")
                sys.exit()
                
                
        head, tail = os.path.split(self.sample_path)
        self.pre, ext = os.path.splitext(tail)
        if self.substract_pbp:
            self.suffix = "BGPtByPtSub"
        else:
            self.suffix = "BGLinSub"
        self.plot_path = head + "/" + self.pre + "_"+self.suffix+".png"
        if self.plot_path.startswith("/"):
            self.plot_path = "." + self.plot_path

        self.save_to = head + "/" + self.pre + "_"+self.suffix+".xy"
        
        if self.save_to.startswith("/"):
            self.save_to = "." + self.save_to
        if "-saveto" in sys.argv:
            self.save_to = sys.argv[sys.argv.index("-saveto") + 1]
        
        if "-sf" in sys.argv:
            self.sf = float(sys.argv[sys.argv.index("-sf") + 1])
        else:
            self.sf = 1

        if "-sig" in sys.argv:
            self.sigma_slope = float(sys.argv[sys.argv.index("-sig") + 1])
        else:
            self.sigma_slope = 0.

if __name__ == "__main__":
    VSM_Substract()
