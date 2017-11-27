from PyQt5.QtWidgets import QApplication
from SliderApp.slider_fit_app import SliderFitApp, cPlotAndFit

import numpy as np
import sys, lmfit
from VSM.VSMFortran import models  as vsmmodel

class GuiApp(cPlotAndFit):
    def init_data(self):
        self.x = np.linspace(-1, 1, 1000)

        self.T = 300
        
        self.p = lmfit.Parameters()
        self.p.add("Ms", 200, min=0, max=500)
        self.p.add("mu", 20e3,min=1e3, max=100e3)
        self.p.add("sig_mu", 0.1,min=0, max=2)
        self.p.add("chi", 0,min=-10, max=10)
        self.ymodel = self.get_model(self.p, self.x)

    def get_model(self, p, B):
        return vsmmodel.magnetization_mu(B,\
            p["Ms"], p["mu"], self.T, p["sig_mu"]) + p["chi"]*B
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    aw = SliderFitApp(GuiApp)
    aw.show()
    app.exec_()
