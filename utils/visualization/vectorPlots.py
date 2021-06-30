# plotting
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable



def plot_quiver(df, group, colorcolumn, cmap='jet'):
    """A function to plot a quiver plot 
          
    Parameters:
    -----------------------------
        : df (pd.DataFrame): is assumed to have columns POSITION_X and POSITION_Y
        : group (str): valid column name to group start and end points 
        : colorcolumn (str): valid column containning color values
        : cmap (str): a color map name
    """
    colormap = matplotlib.cm.get_cmap('jet')

    # create a normalized mapping between the track length and track ID
    colors = df.groupby(group, as_index=False)[colorcolumn].first()
    colors[colorcolumn] /= colors[colorcolumn].max()
    colors = dict(zip(colors[group], colors[colorcolumn]))

    X = []
    Y = []
    U = []
    V = []
    C = []

    for track in df[group].unique():
        tmp = df[df[group] == track]
        x = tmp['POSITION_X'].to_numpy()
        y = tmp['POSITION_Y'].to_numpy()

        X.append(x[0])
        Y.append(y[0])
        U.append(x[-1]-x[0])
        V.append(y[-1]-y[0])
        C.append(colormap(colors[track]))
    
    
    q = plt.quiver(X, 
                   Y, 
                   U, 
                   V, 
                   scale_units='xy', 
                   color=C,
                   angles='xy', 
                   scale=0.9,
                   width=0.005,
                   cmap=cmap)
    
    return q