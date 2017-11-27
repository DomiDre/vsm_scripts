#Date: 2017-11-27 12:54:28.416956
#Author(s)/Contact:
#Dominique Dresen	 Dominique.Dresen@uni-koeln.de

import matplotlib.pyplot as plt
import numpy as np
from VSM.VSMFortran import models  as vsmmodel

Ms = 1
mu = 20e3
T = 300
sig_mu = 0.1
B = np.linspace(-5, 5, 1000)
M = vsmmodel.magnetization_mu(B, Ms, mu, T, sig_mu)

fig, ax = plt.subplots()
ax.axhline(0, color='lightgray', marker='None', zorder=0)
ax.axvline(0, color='lightgray', marker='None', zorder=0)
ax.plot(B, M, linestyle='None', marker='.', zorder=1,)
ax.set_xlabel("$\mathit{\mu_0 H} \, / \, T$")
ax.set_ylabel("$\mathit{M} \, / \, kAm^{-1}$")

ax.set_xlim(-5.1, 5.1)
ax.set_ylim(-1.1, 1.1)
fig.tight_layout()
plt.show()
