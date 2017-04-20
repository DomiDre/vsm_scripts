import numpy as np
import sys, os.path
import matplotlib.pyplot as plt
from vsm import VSMClass

class VSM_Substract(VSMClass):
    def __init__(self):
        super().__init__()
        print("Loading " + self.sample_path)
        self.load_xye_vsmfile(self.sample_path)
        self.substract_nearest_neighbor = False
        if self.substract_pbp:
            self.load_bg()
            self.substract_ptbypt()
            self.save_to_file_ptbypt()
            self.plot_substraction_ptbypt()
            sys.exit("Working on that mode.")
        else:
            self.substract_linear()
            self.save_to_file_linear_substraction()
            self.plot_substraction_linear()
        
    def substract_linear(self):
        self.M_sub = self.M - self.sf*self.slope*self.B
        self.sM_sub = np.sqrt(self.sM**2 + (self.sf*self.sigma_slope*self.B)**2)

    def print_log(self, entry):
        self.header += '#' + entry + '\n'
        print(entry)

    def compare_B_values(self, B1, B2):
        """Check if B lists contain both the same B values"""
        #Same amount of data points?
        if not len(B1) == len(B2):
            self.print_log("WARNING: Different length in B values observed.")
            self.substract_nearest_neighbor = True

        # if not self.substract_nearest_neighbor:
        #     #Same values?
        #     for int_B, B_value in enumerate(B1):
        #         if not np.isclose(B_value, B2[int_B], rtol=0.001, atol=0.001):
        #             self.print_log("WARNING:",B_value, " is not equal to ", B2[int_B])
        #             self.print_log("WARNING: Check whether signal and background have been "+\
        #                   "measured with the same magnetic field steps.")
                              
    def load_bg(self):
        B, M, sM, Mraw, sMraw, header = self.get_data_from_file(self.bg_path)
        #load : self.bg_path
        self.B_bg = np.asarray(B)
        self.M_bg = np.asarray(M)
        self.sM_bg = np.asarray(sM)
        
    def substract_ptbypt(self):
        self.compare_B_values(self.B, self.B_bg)
        self.Binterpolated, self.Minterpolated, self.sMinterpolated,\
            self.M_sub, self.sM_sub = self.nearest_point_substraction(\
                              self.B, self.M, self.sM,\
                              self.B_bg, self.sf*self.M_bg, self.sf*self.sM_bg)

    def nearest_point_substraction(self, B1, M1, sM1,\
                                           B2, M2, sM2):
        Binterpolated = []
        Minterpolated = []
        sMinterpolated = []

        Msubstracted = []
        sMsubstracted = []

        NB2 = len(B2)
        for iB, Bval in enumerate(B1):
            # linear interpolation of B2 at Bval:
            nearest_idx = self.find_idx_nearest_val(B2, Bval)
            Bnear = B2[nearest_idx]
            if np.allclose(Bnear, Bval):
                M2_interpolated = M2[nearest_idx]
                sM2_interpolated = sM2[nearest_idx]

                Binterpolated.append(Bnear)
                Minterpolated.append(M2_interpolated)
                sMinterpolated.append(sM2_interpolated)

                Msub = M1[iB] - M2_interpolated
                Msubstracted.append(Msub)
                sMsubstracted.append(np.sqrt(sM1[iB]**2 +\
                                     sM2_interpolated**2))
            else:
                if nearest_idx == 0:
                    high_idx = 1
                    low_idx = 0
                elif nearest_idx == NB2-1:
                    high_idx = NB2-1
                    low_idx = NB2-2
                else:
                    if Bnear < Bval:
                        low_idx = nearest_idx
                        high_idx = nearest_idx + 1
                    else:
                        low_idx = nearest_idx - 1
                        high_idx = nearest_idx

                dB = (B2[high_idx] - B2[low_idx])
                slope = (M2[high_idx] - M2[low_idx])/dB
                sig_slope = np.sqrt(sM2[high_idx]**2 + sM2[low_idx]**2)/dB

                M2_interpolated = slope*(Bval - B2[low_idx]) + M2[low_idx]
                sM2_interpolated = np.sqrt(sM2[low_idx]**2 +\
                                           (sig_slope*(Bval - B2[low_idx]))**2)
                Binterpolated.append(Bval)
                Minterpolated.append(M2_interpolated)
                sMinterpolated.append(sM2_interpolated)

                Msub = M1[iB] - M2_interpolated
                Msubstracted.append(Msub)
                sMsubstracted.append(np.sqrt(sM1[iB]**2 +\
                                     sM2_interpolated**2))

        return np.asarray(Binterpolated),\
                np.asarray(Minterpolated), np.asarray(sMinterpolated),\
                np.asarray(Msubstracted), np.asarray(sMsubstracted)

    def save_to_file_ptbypt(self):
        save_data = open(self.save_to, "w")
        save_data.write(self.header)
        save_data.write("#Substracted file: " +self.sample_path+"\n")
        save_data.write("#Background file: " + str(self.bg_path) + "\n")
        save_data.write("#BG Scalefactor: " + str(self.sf) + "\n")
        save_data.write('\n\n\n#Raw Background data:\n')
        save_data.write("#B_bg / "+self.Bunit+\
                        "\tM_bg / "+self.Munit+\
                        "\tsM_bg / "+ self.Munit+"\n")
        for i, bval in enumerate(self.B_bg):
            save_data.write('#'+str(bval)+"\t"+\
                            str(self.M_bg[i])+"\t"+\
                            str(self.sM_bg[i])+"\n")
        save_data.write('\n\n')
        

        save_data.write("#B / "+self.Bunit+\
                        "\tM_sub / "+self.Munit+\
                        "\tsM_sub / "+ self.Munit+\
                        "\tM_sample / "+self.Munit+\
                        "\tsM_sample / "+ self.Munit+\
                        "\tM_bg / "+self.Munit+\
                        "\tsM_bg / "+ self.Munit+\
                        "\tM_raw / "+self.Mrawunit+\
                        "\tsM_raw / "+ self.Mrawunit+"\n")
        for i, bval in enumerate(self.B):
            save_data.write(str(bval)+"\t"+\
                            str(self.M_sub[i])+"\t"+\
                            str(self.sM_sub[i])+"\t"+\
                            str(self.M[i])+"\t"+\
                            str(self.sM[i])+"\t"+\
                            str(self.Minterpolated[i])+"\t"+\
                            str(self.sMinterpolated[i])+"\t"+\
                            str(self.Mraw[i])+"\t"+\
                            str(self.sMraw[i])+"\n")

        save_data.close()

    def plot_substraction_ptbypt(self):
        if self.Munit == "kAm-1":
            Munit = "kAm^{-1}"
        else:
            Munit = self.Munit
        fig, ax = plt.subplots()
        ax.axhline(0, color='black')
        ax.axvline(0, color='black')
        ax.errorbar(self.B, self.M, self.sM, label=self.pre+" + Bg")
        ax.errorbar(self.B_bg, self.sf*self.M_bg,\
                    self.sf*self.sM_bg,\
                    label='Background Data')
        ax.errorbar(self.B, self.sf*self.Minterpolated,\
                    self.sf*self.sMinterpolated,\
                    label='Interpolated Data')
        ax.errorbar(self.B, self.M_sub, self.sM_sub, label='Corrected Data')
        ax.set_xlabel("$\mathit{B} \, / \, "+self.Bunit+"$")
        ax.set_ylabel("$\mathit{M} \, / \, "+Munit+"$")

        ax.set_xlim([min(self.B), max(self.B)])
        ax.set_ylim([1.5*min(self.M), 1.5*max(self.M)])
        
        plt.legend(loc='best', fontsize=8).draw_frame(True)

        fig.savefig(self.plot_path)
        plt.show()
        
        
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

        self.save_to = head + "/" + self.pre + "_"+self.suffix+".xye"
        
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
