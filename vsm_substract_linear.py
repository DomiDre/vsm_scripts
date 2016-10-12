import numpy as np
import sys, os.path
import matplotlib.pyplot as plt
import vsm_methods as vsmm
from vsm import VSMClass

class VSM_SubstractLinear(VSMClass):
    def __init__(self):
        super().__init__()
        print("Loading " + self.sample_path)
        self.load_xye_vsmfile(self.sample_path)

        self.substract_linear()
        self.save_to_file()
        self.plot_substraction()
        
    def substract_linear(self):
        self.M_sub = self.M - self.sf*self.slope*self.B
        self.sM_sub = np.sqrt(self.sM**2 + (self.sf*self.sigma_slope*self.B)**2)

    def save_to_file(self):
        save_data = open(self.save_to, "w")
        save_data.write(self.header)
        save_data.write("#Substracted file: " +self.sample_path+"\n")
        save_data.write("#Using Slope: " + str(self.slope) + "\n")
        save_data.write("#Scale Factor: " + str(self.sf) + "\n")
        save_data.write("#Sigma Slope: " + str(self.sigma_slope) + "\n")
        
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

    def plot_substraction(self):
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
        print("python vsm_substract_linear.py samplefile self.slope [saveto] [..]")
        print("Possible Parameters:")
        print("-sf \t -- \t Apply scale factor at substraction m = m_s - sf*self.slope*B")
        print("-sig SIGMAself.slope\t -- \t Increase error by systematic error.")

        
    def get_args(self):
        # Initialization:
        if self.n_args < 2:
            print("Error: Usage of substract linear script:")
            self.help() 
            sys.exit()

        self.sample_path = sys.argv[1]
        self.slope = float(sys.argv[2])
        
        head, tail = os.path.split(self.sample_path)
        self.pre, ext = os.path.splitext(tail)
        self.plot_path = head + "/" + self.pre + "_BGLinSub.png"
        if self.plot_path.startswith("/"):
            self.plot_path = "." + self.plot_path

        self.save_to = head + "/" + self.pre + "_BGLinSub.xy"
        if self.save_to.startswith("/"):
            self.save_to = "." + self.save_to
        if self.n_args > 2 and not sys.argv[3].startswith("-"):
            self.save_to = sys.argv[3]
        
        if "-sf" in sys.argv:
            self.sf = float(sys.argv[sys.argv.index("-sf") + 1])
        else:
            self.sf = 1

        if "-sig" in sys.argv:
            self.sigma_slope = float(sys.argv[sys.argv.index("-sig") + 1])
        else:
            self.sigma_slope = 0.

if __name__ == "__main__":
    VSM_SubstractLinear()
