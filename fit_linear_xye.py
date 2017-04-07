import sys, os.path
import matplotlib.pyplot as plt
import numpy as np
import common_math
import lmfit

#  Read input files:
def load_xyfile(filepath):
    datafile = open(filepath, "r")
    x = []
    y = []
    if "-u" in sys.argv:
        uidx = sys.argv.index("-u")
        colx = int(sys.argv[uidx+1])
        coly = int(sys.argv[uidx+2])
    else:
        colx = 0
        coly = 1

    for line in datafile:
        stripline = line.strip()
        if stripline.startswith('#') or stripline == "":
            continue
        splitline = stripline.split()
        
        try:
            xval = float(splitline[colx])
            yval = float(splitline[coly])
            x.append(xval)
            y.append(yval)
        except (ValueError, TypeError):
            continue
            
    datafile.close()
    print("Loaded data from " + filepath)
    return np.asarray(x), np.asarray(y)

def load_xyefile(filepath):
    datafile = open(filepath, "r")
    x = []
    y = []
    sy = []
    if "-u" in sys.argv:
        uidx = sys.argv.index("-u")
        colx = int(sys.argv[uidx+1])
        coly = int(sys.argv[uidx+2])
        colsy = int(sys.argv[uidx+3])
    else:
        colx = 0
        coly = 1
        colsy = 2

    for line in datafile:
        stripline = line.strip()
        if stripline.startswith('#') or stripline == "":
            continue
        splitline = stripline.split()
        
        try:
            xval = float(splitline[colx])
            yval = float(splitline[coly])
            syval = float(splitline[colsy])
            x.append(xval)
            y.append(yval)
            sy.append(syval)
        except (ValueError, TypeError):
            continue
    datafile.close()
    print("Loaded data from " + filepath)
    return np.asarray(x), np.asarray(y), np.asarray(sy)


def get_slice(array, left, right):
    return -((array < left) -  (right < array))

def residuum(p, x, y, sy):
    return (common_math.linear(x, p["m"].value, p["b"].value) - y)/sy

def residuum_no_err(p, x, y):
    return (common_math.linear(x, p["m"].value, p["b"].value) - y)

def plotfit_xye(pfile_path):
    
    if "-xy" in sys.argv:
        load_xy = True
    else:
        load_xy = False
    
    if load_xy:
        x, y = load_xyfile(pfile_path)
    else:
        x, y, sy = load_xyefile(pfile_path)
        
    #Initialize variables
    xvar = "\mathit{x}"
    yvar = "\mathit{y}"
    xunit = ""
    yunit = ""
    plot_path = ""
    plotminx = min(x)
    plotmaxx = max(x)

    miny = min(y)
    maxy = max(y)  
    minfacy = 1.1 if miny < 0 else 0.9
    maxfacy = 1.1 if maxy > 0 else 0.9
    
    plotminy = miny*minfacy
    plotmaxy = maxy*maxfacy
    
    labelname = ""
    
    if "-vsm" in sys.argv:
        xvar = "\mathit{B}"
        yvar = "\mathit{M}"
        xunit = " \, / \, T"
        yunit = " \, / \, memu"
        head, tail = os.path.split(pfile_path)
        pre, ext = os.path.splitext(tail)
        plot_path = head + "/" + pre + ".png"
        if plot_path.startswith("/"):
            plot_path = "." + plot_path
        labelname = pre

    if "-vars" in sys.argv:
        xvar = "\mathit{"+sys.argv[sys.argv.index("-vars") + 1] + "}"
        yvar = "\mathit{"+sys.argv[sys.argv.index("-vars") + 2] + "}"
    
    if "-units" in sys.argv:
        xunit = " \, / \, " + sys.argv[sys.argv.index("-units") + 1]
        yunit = " \, / \, " + sys.argv[sys.argv.index("-units") + 2]
    
    if "-plot_lim" in sys.argv:
        minx = float(sys.argv[sys.argv.index("-plot_lim") + 1])
        maxx = float(sys.argv[sys.argv.index("-plot_lim") + 2])

    if "-label" in sys.argv:
        labelname = sys.argv[sys.argv.index("-label") + 1]

    if "-save" in sys.argv:
        plot_path = sys.argv[sys.argv.index("-save") + 1]
        
            
    fig, ax = plt.subplots() #Initialize plot canvas
    # Restricted fit area defined?
    if "-fit_lim" in sys.argv:
        fit_idx = sys.argv.index("-fit_lim")
        fitminx = float(sys.argv[fit_idx + 1])
        fitmaxx = float(sys.argv[fit_idx + 2])
        fit_slice = get_slice(x, fitminx, fitmaxx)

        x_plot = x[fit_slice]
        y_plot = y[fit_slice]
        #Excluded data
        x_exc = x[-fit_slice]
        y_exc = y[-fit_slice]

        if not load_xy:
            sy_plot = sy[fit_slice]
            sy_exc = sy[-fit_slice]
        
    
        if len(x_exc) > 0:
            if load_xy:
                ax.plot(x_exc, y_exc, linestyle='None', color='gray')
            else:
                ax.errorbar(x_exc, y_exc, sy_exc, linestyle='None', color='gray')
    else:
        x_plot = x
        y_plot = y
        if not load_xy:
            sy_plot = sy

    # Initialize fit variables
    p = lmfit.Parameters()
    minit = sys.argv[sys.argv.index("-m")+1] if "-m" in sys.argv else 1
    binit = sys.argv[sys.argv.index("-b")+1] if "-b" in sys.argv else 0
    
    if "-fixb" in sys.argv:
        varyb = False
    else:
        varyb = True
        
    p.add("m", minit)
    p.add("b", binit, vary=varyb)
    
    if load_xy:
        fit_result = lmfit.minimize(residuum_no_err, p, args=(x, y))
    else:
        fit_result = lmfit.minimize(residuum, p, args=(x, y, sy))
    print(lmfit.fit_report(fit_result))
    
    m = fit_result.params["m"].value
    sm = fit_result.params["m"].stderr
    b = fit_result.params["b"].value
    sb = fit_result.params["b"].stderr
    
    prec = "{:.3e}"
    fitresultstr = r"$\mathit{m} \, = \, $" + prec.format(m) + " +/- " + prec.format(sm) + "\n"+\
            "$\mathit{b} \, = \, $" + prec.format(b) + " +/-" + prec.format(sb)
    
    chi2 = fit_result.redchi
    if load_xy:
        ax.plot(x_plot, y_plot, linestyle='None', color='#2b8cbe', label=labelname)
    else:
        ax.errorbar(x_plot, y_plot, sy_plot, linestyle='None', color='#2b8cbe', label=labelname)
    ax.plot(x, common_math.linear(x, m, b), color='#e34a33', marker='None', label=fitresultstr)
    
    if chi2 < 1e-3:
        chi2str = "{:.3e}".format(chi2)
    else:
        chi2str = "{:.4f}".format(chi2)
    ax.plot([],[],ls='None', marker='None',label="$\chi^2/dof \, = \, " + chi2str+"$")
    
    ax.set_xlabel("$"+xvar+xunit+"$")
    ax.set_ylabel("$"+yvar+yunit+"$")
    ax.set_xlim([plotminx, plotmaxx])
    ax.set_ylim([plotminy, plotmaxy])
    plt.legend(loc='best', fontsize=10)
    
    if plot_path != "":
        fig.savefig(plot_path)
        print("Saved plot to", plot_path)

    plt.show()


if __name__ == "__main__":
    num_args = len(sys.argv) - 1
    if num_args < 1 or "-help" in sys.argv or "-h" in sys.argv:
        print("ERROR: Usage of plot_xy.py:")
        print("python fit_linear_xye.py xyefile [..]")
        print("Possible parameters:")
        print("-fit_lim MINX MAXX \t -- \t Define region on x axis where to perform linear fit.")
        print("-plot_lim MINX MAXX \t -- \t Define region on x axis which to plot.")
        print("-label LABEL DATA \t -- \t Create label in legend for data.")
        print("-vars XVAR YVAR \t -- \t What is the variable of x and y-axis?")
        print("-units XUNIT YUNIT \t -- \t What are the units of the x and y axis?")
        print("-save FILENAME \t -- \t Save image to file.")
        print("-m MINIT \t -- \t Initial slope for fit [Default: 1]")
        print("-b BINIT \t -- \t Initial interception for ift [Default: 0]")
        print("-xy \t -- \t Work without errors on y")
        print("-u x y [sy]\t -- \t Use columns for loading.")
        print("-fixb \t -- \t Dont vary the interception value")
        print("")
        print("-vsm \t -- \t VSM mode")
        sys.exit()
        
    # Initialization:
    pfile_path = sys.argv[1]
    plotfit_xye(pfile_path)
