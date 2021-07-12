import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable


def control_plot(box):
    """A function to create the control-style plot for different discrete 
    bins of the x coordinate
    
        Parameters:
    -----------------------------
        : boxes (pd.DataFrame): dataframe returned from utils.trackmate.woundHealing.get_leading_cells()
    
    """
    box['X'] = box['POSITION_X'].astype(int)
    box['Direction'] = np.where(box['type'] == 'upper', 'Above Wound', 'Below Wound')

    top_boxes = box[box['type'] == 'upper'].sort_values(by=['BOX', 'FRAME'])
    top_boxes['y_diff'] = top_boxes['POSITION_Y'].diff(1)
    top_boxes['y_diff'] = np.where(top_boxes['FRAME'] == 0, 0, top_boxes['y_diff'])
    top_boxes_grp = top_boxes.groupby(['X', 'Direction'], as_index=False)['y_diff'].mean()

    bot_boxes = box[box['type'] == 'lower'].sort_values(by=['BOX', 'FRAME'])
    bot_boxes['y_diff'] = bot_boxes['POSITION_Y'].diff(1)
    bot_boxes['y_diff'] = np.where(bot_boxes['FRAME'] == 0, 0, bot_boxes['y_diff'])
    bot_boxes_grp = bot_boxes.groupby(['X', 'Direction'], as_index=False)['y_diff'].mean()

    sns.barplot(data=top_boxes_grp,
                x='X',
                y='y_diff',
                hue='Direction',
                palette=['C1'])

    sns.barplot(data=bot_boxes_grp,
                x='X',
                y='y_diff',
                hue='Direction',
                palette=['C7'])

    mean_upper = top_boxes_grp['y_diff'].mean()
    mean_lower = bot_boxes_grp['y_diff'].mean()

    plt.axhline(y=mean_upper, ls=':', lw=3, c="C1")
    plt.axhline(y=mean_lower, ls=':', lw=3, c="C7")


def shark_plot(boxes, cmap):
    """A function to plot the leading edge of the wound over time
          
    Parameters:
    -----------------------------
        : boxes (pd.DataFrame): dataframe returned from utils.trackmate.woundHealing.get_leading_cells()
        : cmap (matplotlib.colors.ListedColormap): a color map, NOTE the str
    """
    a_list = []
    for t in range(boxes['FRAME'].max()):

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