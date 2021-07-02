import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable


def shark_plot(boxes, cmap):
    """A function to plot the leading edge of the wound over time
          
    Parameters:
    -----------------------------
        : boxes (pd.DataFrame): dataframe returned from utils.trackmate.woundHealing.get_leading_cells()
        : cmap (matplotlib.colors.ListedColormap): a color map, NOTE the str
    """
    a_list = []
    for t in boxes['FRAME'].unique():

        upper = boxes[(boxes['FRAME'] == t) & (boxes['type'] == 'upper')]
        a = upper['FRAME_NORM'].unique()[0] 
        plt.plot(upper['POSITION_X'], 
                 upper['POSITION_Y'],
                 c=cmap(upper['FRAME_NORM'].unique()[0]))

        lower = boxes[(boxes['FRAME'] == t) & (boxes['type'] == 'lower')]
        a = lower['FRAME_NORM'].unique()[0] 
        plt.plot(lower['POSITION_X'],
                 lower['POSITION_Y'],
                 c=cmap(upper['FRAME_NORM'].unique()[0]))

        a_list.append(a)

    sm = plt.cm.ScalarMappable(cmap=cmap, 
                               norm=Normalize(vmin=0, 
                                              vmax=boxes['FRAME'].max()))
    cb = plt.colorbar(sm, aspect=20)
    cb.ax.get_yaxis().labelpad = 15
    cb.ax.set_ylabel('Frame', rotation=270)
    
    
    
def velocity_shark(boxes, cmap):
    """A function to plot a quiver plot 
          
    Parameters:
    -----------------------------
        : boxes (pd.DataFrame): dataframe returned from utils.trackmate.woundHealing.get_leading_cells()
        : cmap (matplotlib.colors.ListedColormap): a color map, NOTE the str
    """
    first_last = boxes[(boxes['FRAME'] == 0) | (boxes['FRAME'] == boxes['FRAME'].max())]

    X = []
    Y = []
    U = []
    V = []
    C = []

    for b in range(first_last['BOX'].max()):
        tmp = first_last[first_last['BOX'].astype(int) == b+1]

        # lower box
        init = (tmp['type'] == 'lower') &  (tmp['FRAME'] == 0)
        fin =  (tmp['type'] == 'lower') &  (tmp['FRAME'] == tmp['FRAME'].max() )

        X.append(tmp[init]['POSITION_X'].values[0] )
        Y.append(tmp[init]['POSITION_Y'].values[0] )

        y_dist =  tmp[fin]['POSITION_Y'].values[0]  - tmp[init]['POSITION_Y'].values[0] 

        U.append(0)
        V.append(y_dist)
        C.append(y_dist)

        # upper box
        init = (tmp['type'] == 'upper') &  (tmp['FRAME'] == 0)
        fin =  (tmp['type'] == 'upper') &  (tmp['FRAME'] == tmp['FRAME'].max() )

        X.append(tmp[init]['POSITION_X'].values[0] )
        Y.append(tmp[init]['POSITION_Y'].values[0] )

        y_dist =  tmp[fin]['POSITION_Y'].values[0]  - tmp[init]['POSITION_Y'].values[0] 

        U.append(0)
        V.append(y_dist)
        C.append(y_dist)

    v = np.abs(np.array(C))
    v_normed =  (v - v.min()) / (v.max() - v.min()) 

    q = plt.quiver(X, 
                   Y, 
                   U, 
                   V, 
                   scale_units='xy', 
                   angles='xy', 
                   color=cmap(v_normed),
                   scale=0.9,
                   width=0.005)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=Normalize(vmin=np.min(v), vmax=np.max(v)))
    cb = plt.colorbar(sm, aspect=20)
    cb.ax.get_yaxis().labelpad = 15
    cb.ax.set_ylabel('Distance Traveled (pixels)', rotation=270)