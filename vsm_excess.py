import numpy as np
import sys, os.path, lmfit
import matplotlib.pyplot as plt
from vsm import VSMClass

class VSM_Excess(VSMClass):
    def __init__(self):
        super().__init__()
        print("Loading " + self.sample_path)
        self.load_xye_vsmfile(self.sample_path)
        
        self.determine_excess()
        self.save_to_file_excess()
        self.plot_excess()
    
    def linear(self, p, x):
        return p['m'].value*x + p['n'].value

    def residuum(self, p, x, y, sy):
        return (self.linear(p, x) - y)/sy

    def determine_excess(self):
        B_up_slice = np.logical_and(self.min_B<self.B, self.B<self.max_B)
        B_down_slice = np.logical_and(-self.max_B<self.B, self.B<-self.min_B)
        B_up = self.B[B_up_slice]
        M_up = self.M[B_up_slice]
        sM_up = self.sM[B_up_slice]
          
        p_upper_fit = lmfit.Parameters()
        m_up_estimate = (M_up[-1] - M_up[0]) / (B_up[-1] - B_up[0])
        p_upper_fit.add("m", m_up_estimate)
        p_upper_fit.add("n", B_up[0])

        B_down = self.B[B_down_slice]
        M_down = self.M[B_down_slice]
        sM_down = self.sM[B_down_slice]
        m_down_estimate = (M_down[-1] - M_down[0]) / (B_down[-1] - B_down[0])
        p_lower_fit = lmfit.Parameters()
        p_lower_fit.add("m", m_down_estimate)
        p_lower_fit.add("n", B_down[0])

        res_up = lmfit.minimize(self.residuum, p_upper_fit, args=(B_up, M_up, sM_up), method='leastsq')
        print(lmfit.fit_report(res_up))
        res_down = lmfit.minimize(self.residuum, p_lower_fit, args=(B_down, M_down, sM_down), method='leastsq')
        print(lmfit.fit_report(res_down))

        p_upper_fit = res_up.params
        p_lower_fit = res_down.params

        self.mup = p_upper_fit["m"].value
        self.nup = p_upper_fit["n"].value
        self.mlow = p_lower_fit["m"].value
        self.nlow = p_lower_fit["n"].value
        
        self.smup = p_upper_fit["m"].stderr
        self.snup = p_upper_fit["n"].stderr
        self.smlow = p_lower_fit["m"].stderr
        self.snlow = p_lower_fit["n"].stderr

        self.sm = 1./self.smup**2 + 1./self.smlow**2
        self.m = (self.mup/self.smup**2 + self.mlow/self.smlow**2) / self.sm
        self.sm = np.sqrt(1./self.sm)
        
        self.sn = 1./self.snup**2 + 1./self.snlow**2
        self.n = (self.nup/self.snup**2 - self.nlow/self.snlow**2) / self.sn
        self.sn = np.sqrt(1./self.sn)

        self.M_corr = self.M - self.m*self.B
        self.sM_corr = self.sM

    def print_log(self, entry):
        self.header += '#' + entry + '\n'
        print(entry)

    def save_to_file_excess(self):
        save_data = open(self.save_to, "w")
        save_data.write(self.header)
        save_data.write("#Excess corrected file: " +self.sample_path + "\n")
        save_data.write("#Fitted slope: " + str(self.m) + ' +\- ' + str(self.sm) + "\n")
        save_data.write("#Fitted shift: " + str(self.n) + ' +\- ' + str(self.sn) + "\n")
        
        save_data.write("#B / "+self.Bunit+\
                        "\tM_corr / "+self.Munit+\
                        "\tsM_corr / "+ self.Munit+\
                        "\tM_loaded / "+self.Munit+\
                        "\tsM_loaded / "+ self.Munit+\
                        "\tM_raw / "+self.Mrawunit+\
                        "\tsM_raw / "+ self.Mrawunit+"\n")
        for i, bval in enumerate(self.B):
            save_data.write(str(bval)+"\t"+\
                            str(self.M_corr[i])+"\t"+\
                            str(self.sM_corr[i])+"\t"+\
                            str(self.M[i])+"\t"+\
                            str(self.sM[i])+"\t"+\
                            str(self.Mraw[i])+"\t"+\
                            str(self.sMraw[i])+"\n")
        save_data.close()

    def plot_excess(self):
        if self.Munit == "kAm-1":
            Munit = "kAm^{-1}"
        else:
            Munit = self.Munit
        fig, ax = plt.subplots()
        ax.axhline(0, color='black')
        ax.axvline(0, color='black')
        ax.errorbar(self.B, self.M, self.sM, label=self.pre)
        ax.errorbar(self.B, self.M_corr, self.sM_corr,label=self.pre+" corrected")
        ax.plot(self.B, self.m*self.B + self.nup, color='black', marker='None')
        ax.plot(self.B, self.m*self.B + self.nlow, color='black', marker='None')

        ax.set_xlabel("$\mathit{B} \, / \, "+self.Bunit+"$")
        ax.set_ylabel("$\mathit{M} \, / \, "+Munit+"$")

        ax.set_xlim([min(self.B), max(self.B)])
        ax.set_ylim([1.5*min(self.M), 1.5*max(self.M)])
        
        plt.legend(loc='best', fontsize=8).draw_frame(True)

        fig.savefig(self.plot_path)
        plt.show()
        
    def help(self):
        print("python vsm_excess.py samplefile Min_B Max_B [saveto]")
        print("\nFit data between Min_B, Max_B linearly and substract mean slope from data. ")
        print("Possible Parameters:")
        print("-saveto SAVEPATH\t -- \t Save data to SAVEPATH.")

        
    def get_args(self):
        # Initialization:
        if self.n_args <= 2:
            print("Error: Usage of excess fit script:")
            self.help() 
            sys.exit()
        
        self.sample_path = sys.argv[1]
        try:
            self.min_B = float(sys.argv[2])
            self.max_B = float(sys.argv[3])
            assert(np.sign(self.min_B) == np.sign(self.max_B))
            self.min_B = abs(float(sys.argv[2]))
            self.max_B = abs(float(sys.argv[3]))
            

        except (TypeError, ValueError):
            print("ERROR: Second & Third argument must be a number.")
            sys.exit()
            
                
        head, tail = os.path.split(self.sample_path)
        self.pre, ext = os.path.splitext(tail)
        self.suffix = "ExcessSubstracted"
        self.plot_path = head + "/" + self.pre + "_"+self.suffix+".png"
        if self.plot_path.startswith("/"):
            self.plot_path = "." + self.plot_path
        self.save_to = head + "/" + self.pre + "_"+self.suffix+".xye"
        
        if self.save_to.startswith("/"):
            self.save_to = "." + self.save_to
        if "-saveto" in sys.argv:
            self.save_to = sys.argv[sys.argv.index("-saveto") + 1]

if __name__ == "__main__":
    VSM_Excess()
