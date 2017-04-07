import numpy as np
import sys, os.path
import matplotlib.pyplot as plt
from vsm import VSMClass

class VSM_Rescale(VSMClass):
    def __init__(self):
        super().__init__()
        print("Loading " + self.sample_path)
        self.load_xye_vsmfile(self.sample_path)
        
        self.rescale()
        self.save_to_file_rescale()
        self.plot_rescaling()
        
    def rescale(self):
        self.M_res = self.M/self.scalefactor
        self.sM_res = self.sM/self.scalefactor
        self.sM_res = self.M_res*np.sqrt((self.sM_res/self.M_res)**2 +\
                       (self.sigma_scale/self.scalefactor)**2)
                       
    def save_to_file_rescale(self):
        save_data = open(self.save_to, "w")
        save_data.write(self.header)
        save_data.write("#Rescaled file: " +self.sample_path+"\n")
        save_data.write("#Rescale Factor: " + str(self.scalefactor) + "\n")
        save_data.write("#Sigma Scalefactor: " + str(self.sigma_scale) + "\n")
        
        save_data.write("#B / "+self.Bunit+\
                        "\tM_scaled / "+self.Mnewunit+\
                        "\tsM_scaled / "+ self.Mnewunit+\
                        "\tM_prescaling / "+self.Munit+\
                        "\tsM_prescaling / "+ self.Munit+\
                        "\tM_raw / "+self.Mrawunit+\
                        "\tsM_raw / "+ self.Mrawunit+"\n")
        for i, bval in enumerate(self.B):
            save_data.write(str(bval)+"\t"+\
                            str(self.M_res[i])+"\t"+\
                            str(self.sM_res[i])+"\t"+\
                            str(self.M[i])+"\t"+\
                            str(self.sM[i])+"\t"+\
                            str(self.Mraw[i])+"\t"+\
                            str(self.sMraw[i])+"\n")
        save_data.close()

    def plot_rescaling(self):
        if self.Mnewunit == "kAm-1":
            Munit = "kAm^{-1}"
        elif self.Mnewunit == "emug-1":
            Munit = "emu \, g^{-1}"
        else:
            Munit = self.Mnewunit
            
        fig, ax = plt.subplots()
        ax.axhline(0, color='black')
        ax.axvline(0, color='black')
        ax.errorbar(self.B, self.M, self.sM, label=self.pre+" (before rescaling)")
        ax.errorbar(self.B, self.M_res, self.sM_res, label=self.pre)
        ax.plot([], [], marker='None', ls='None', \
                label="Scalefactor: " + str(self.scalefactor))
        ax.set_xlabel("$\mathit{B} \, / \, "+self.Bunit+"$")
        ax.set_ylabel("$\mathit{M} \, / \, "+Munit+"$")

        ax.set_xlim([min(self.B), max(self.B)])
        ax.set_ylim([1.5*min(self.M_res), 1.5*max(self.M_res)])
        
        plt.legend(loc='best', fontsize=8).draw_frame(True)

        fig.savefig(self.plot_path)
        plt.show()
        
    def help(self):
        print("python vsm_rescale.py samplefile SCALEFACTOR NEWUNIT [..]")
        print("Possible Parameters:")
        print("-sig SIGMA\t -- \t Increase error by systematic error.")
        print("-saveto SAVEPATH\t -- \t Save data to SAVEPATH.")
        print("-help \t -- \t Print help")
        
    def get_args(self):
        # Initialization:
        if self.n_args <= 2:
            print("Error: Usage of rescale script:")
            self.help() 
            sys.exit()
        
        self.sample_path = sys.argv[1]
        try:
            self.scalefactor = float(sys.argv[2])
        except (TypeError, ValueError):
            print("ERROR: Second argument must either be a number.")
            sys.exit()
        
        self.Mnewunit = sys.argv[3]
        
        head, tail = os.path.split(self.sample_path)
        self.pre, ext = os.path.splitext(tail)
        self.suffix = "rescale"
        self.plot_path = head + "/" + self.pre + "_"+self.suffix+".png"
        if self.plot_path.startswith("/"):
            self.plot_path = "." + self.plot_path
        self.save_to = head + "/" + self.pre + "_"+self.suffix+".xye"
        
        if self.save_to.startswith("/"):
            self.save_to = "." + self.save_to
        if "-saveto" in sys.argv:
            self.save_to = sys.argv[sys.argv.index("-saveto") + 1]
            self.plot_path = self.save_to.rsplit(".",1)[0] + ".png"
        
        if "-sig" in sys.argv:
            self.sigma_scale = float(sys.argv[sys.argv.index("-sig") + 1])
        else:
            self.sigma_scale = 0.

if __name__ == "__main__":
    VSM_Rescale()
