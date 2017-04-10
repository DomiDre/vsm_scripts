import sys
import matplotlib.pyplot as plt
import numpy as np

#  Read input files:

def load_xyemfile(filepath):
    datafile = open(filepath, "r")
    x = []
    y = []
    sy = []
    ymodel = []
    if "-u" in sys.argv:
        uidx = sys.argv.index("-u")
        colx = int(sys.argv[uidx+1])
        coly = int(sys.argv[uidx+2])
        colsy = int(sys.argv[uidx+3])
        colymodel = int(sys.argv[uidx+4])
    else:
        colx = 0
        coly = 1
        colsy = 2
        colymodel = 3
        
    if "-skipheader" in sys.argv:
        n = int(sys.argv[sys.argv.index("-skipheader") + 1])
    else:
        n = 0

    for ifile, line in enumerate(datafile):
        if ifile < n:
            continue

        if line.startswith('#'):
            continue

        splitline = line.strip().split()
        if len(splitline) == 0:
            continue
        x.append(float(splitline[colx]))
        y.append(float(splitline[coly]))
        sy.append(float(splitline[colsy]))
        ymodel.append(float(splitline[colymodel]))
    return np.asarray(x), np.asarray(y), np.asarray(sy), np.asarray(ymodel)
    
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
    if "-skipheader" in sys.argv:
        n = int(sys.argv[sys.argv.index("-skipheader") + 1])
    else:
        n = 0
    for ifile, line in enumerate(datafile):
        if ifile < n:
            continue
        if line.startswith('#'):
            continue
        splitline = line.strip().split()
        if len(splitline) == 0:
            continue
        x.append(float(splitline[colx]))
        y.append(float(splitline[coly]))
        sy.append(float(splitline[colsy]))
    return np.asarray(x), np.asarray(y), np.asarray(sy)

def load_xymfile(filepath):
    datafile = open(filepath, "r")
    x = []
    y = []
    ymodel = []
    if "-u" in sys.argv:
        uidx = sys.argv.index("-u")
        colx = int(sys.argv[uidx+1])
        coly = int(sys.argv[uidx+2])
        colymodel = int(sys.argv[uidx+3])
    else:
        colx = 0
        coly = 1
        colymodel = 2
    if "-skipheader" in sys.argv:
        n = int(sys.argv[sys.argv.index("-skipheader") + 1])
    else:
        n = 0
    for ifile, line in enumerate(datafile):
        if ifile < n:
            continue
        if line.startswith('#'):
            continue
        splitline = line.strip().split()
        x.append(float(splitline[colx]))
        y.append(float(splitline[coly]))
        ymodel.append(float(splitline[colymodel]))
    return np.asarray(x), np.asarray(y), np.asarray(ymodel)
    
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
        
    if "-skipheader" in sys.argv:
        n = int(sys.argv[sys.argv.index("-skipheader") + 1])
    else:
        n = 0
    for ifile, line in enumerate(datafile):
        if ifile < n:
            continue
        if line.startswith('#'):
            continue
        splitline = line.strip().split()
        x.append(float(splitline[colx]))
        y.append(float(splitline[coly]))
    return np.asarray(x), np.asarray(y)

def get_slice(array, left, right):
    return -((array < left) -  (right < array))

def plot_xye(x, y, sy, ymodel, plot_slice, ax, linecolor=None, linestyle="None",\
                marker='.', labelname=None, modelname = None, modelcolor='red'):
    x_plot = x[plot_slice]
    y_plot = y[plot_slice]
    x_exc = x[-plot_slice]
    y_exc = y[-plot_slice]
    if sy is not None:
        sy_plot = sy[plot_slice]
        sy_exc = sy[-plot_slice]
    if ymodel is not None:
        ymodel_plot = ymodel[plot_slice]
        ymodel_exc = ymodel[-plot_slice]
        
    if "-linestyle" in sys.argv:
        linestyle = sys.argv[sys.argv.index("-linestyle")+1]
    elif "-ls" in sys.argv:
        linestyle = sys.argv[sys.argv.index("-ls")+1]

    if "-marker" in sys.argv:
        marker = sys.argv[sys.argv.index("-marker")+1]
    
    if "-linecolor" in sys.argv:
        linecolor = sys.argv[sys.argv.index("-linecolor")+1]
    elif "-lc" in sys.argv:
        linecolor = sys.argv[sys.argv.index("-lc")+1]
    
    if "-nv" in sys.argv:
        #Assuming all symmetric measurements find virgin curve and remove it
        virgin = round(len(x_plot)/5 , 0) 
        virgin = int(virgin)
        x_plot = x_plot[virgin:-1]
        y_plot = y_plot[virgin:-1]
        sy_plot = sy_plot[virgin:-1]

    if len(x_exc) > 0:
        if sy is None:
            ax.plot(x_exc, y_exc, linestyle='None', color='gray')
        else:
            ax.errorbar(x_exc, y_exc, sy_exc, linestyle='None', color='gray')
        
    if sy is None:
        ax.errorbar(x_plot, y_plot, marker=marker, linestyle=linestyle,\
                color=linecolor, label=labelname)
    else:
        ax.errorbar(x_plot, y_plot, sy_plot, marker=marker, linestyle=linestyle,\
                color=linecolor, label=labelname)
    
    if ymodel is not None:
        ax.plot(x_plot, ymodel_plot, marker='None', ls='-',\
                color=modelcolor, label=modelname)
    
    if labelname is not None or modelname is not None:
        plt.legend(loc='upper left', fontsize=10)

    


if __name__ == "__main__":
    num_args = len(sys.argv) - 1
    if num_args < 1 or "-help" in sys.argv:
        print("ERROR: Usage of plot_xy.py:")
        print("python fit_vsm.py params [..]")
        print("Possible parameters:")
        print("-plot_lim minx maxx \t -- \t Set x plot limits")
        print("-label labelname \t -- \t Make a legend with given labelname")
        print("-vars xvar yvar \t -- \t Set variable names in plot to xvar yvar")
        print("-units xunit yunit  \t -- \t Set unit names in plot to xunit yunit")
        print("-logy \t -- \t Log y scale")
        print("-logx \t -- \t Log x scale")
        print("-loglog \t -- \t Log x and y scale")
        print("-linestyle style \t -- \t Linestyle: default None")
        print("-linecolor color \t -- \t Linestyle: default None")
        print("-add xyfile \t -- \t Plot additional xyfile")
        print("-skipheader n \t -- \t Skip first n rows of file")
        print("-xy \t -- \t Plot xy")
        print("-u \t -- \t Set columns which should be read from file.")
        print("-model \t -- \t Plot model.")
        print("-save savename \t -- \t Save to savename")
        print("-vsm \t -- Plot VSM Data")
        print("-nv \t -- No Virgin curve")
        sys.exit()
        
    # Initialization:
    pfile_path = sys.argv[1]
    fig, ax = plt.subplots()
    
    xvar = "\mathit{x}"
    yvar = "\mathit{y}"
    xunit = ""
    yunit = ""
    plot_path = None
    labelname = None
    modelmode = "-model" in sys.argv
    xymode = "-xy" in sys.argv
    nolabel_mode = False
    if "-vsm" in sys.argv:
        xvar = "\mathit{B}"
        xunit = " \, / \, T"
        yvar = "\mathit{M}"
        yunit = " \, / \, memu"
        nolabel_mode=True
        plot_path = pfile_path.rsplit(".", 1)[0] + ".png"
        
    if xymode:
        if modelmode:
            x, y, ymodel = load_xymfile(pfile_path)
        else:
            x, y = load_xyfile(pfile_path)
            ymodel = None
        sy = None
    else:
        if modelmode:
            x, y, sy, ymodel = load_xyemfile(pfile_path)
        else:
            x, y, sy = load_xyefile(pfile_path)
            ymodel = None
        
    if "-plot_lim" in sys.argv:
        minx = float(sys.argv[sys.argv.index("-plot_lim") + 1])
        maxx = float(sys.argv[sys.argv.index("-plot_lim") + 2])
    else:
        minx = -np.inf
        maxx = np.inf
        
    if "-label" in sys.argv:
        labelname = sys.argv[sys.argv.index("-label") +1]
        
    plot_slice = get_slice(x, minx, maxx)
    print("Loaded Data.")
    if labelname is None:
        labelname=pfile_path.rsplit(".",1)[0]
        
    plot_xye(x, y, sy, ymodel, plot_slice, ax, labelname=labelname)
    if "-plot_lim" in sys.argv:
        minx = float(sys.argv[sys.argv.index("-plot_lim")+1])
        maxx = float(sys.argv[sys.argv.index("-plot_lim")+2])
        ax.set_xlim([minx, maxx])
    else:
        ax.set_xlim([min(x), max(x)])
    miny = min(y)
    maxy = max(y)  
    minfacy = 1.1 if miny < 0 else 0.9
    maxfacy = 1.1 if maxy > 0 else 0.9
    ax.set_ylim([minfacy*miny, maxfacy*maxy])


    while "-add" in sys.argv:
        idxadd =sys.argv.index("-add")
        filename = sys.argv[idxadd+1]
        if "-xy" in sys.argv:
            x, y = load_xyfile(filename)
            sy = None
        else:
            x, y, sy = load_xyefile(filename)
        plot_slice = get_slice(x, minx, maxx)
        plot_xye(x, y, sy, None, plot_slice, ax,\
                labelname=filename.rsplit(".",1)[0])
        
        del sys.argv[idxadd + 1]
        del sys.argv[idxadd]
        miny = min(miny, min(y))
        maxy = max(maxy, max(y))
        minfacy = 1.1 if miny < 0 else 0.9
        maxfacy = 1.1 if maxy > 0 else 0.9
        ax.set_ylim([minfacy*miny, maxfacy*maxy])
        
    if "-logy" in sys.argv:
        ax.set_yscale('log')
    if "-logx" in sys.argv:
        ax.set_xscale('log')
    
    if "-loglog" in sys.argv:
        ax.set_xscale('log')
        ax.set_yscale('log')
    
    if "-vars" in sys.argv:
        xvar = "\mathit{"+sys.argv[sys.argv.index("-vars")+1]+"}"
        yvar = "\mathit{"+sys.argv[sys.argv.index("-vars")+2]+"}"
    
    if "-units" in sys.argv:
        xunit = " \, / \, " + sys.argv[sys.argv.index("-units")+1]
        yunit = " \, / \, " + sys.argv[sys.argv.index("-units")+2]
        
    ax.set_xlabel("$"+xvar+xunit+"$")
    ax.set_ylabel("$"+yvar+yunit+"$")
    if "-save" in sys.argv:
        plot_path = sys.argv[sys.argv.index("-save")+1]
    
    if plot_path is not None:
        fig.savefig(plot_path)
        print("Saved plot to", plot_path)
    plt.show()
