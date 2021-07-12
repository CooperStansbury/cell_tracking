import pandas as pd
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable

import plotly
import plotly.offline as go_offline
import plotly.graph_objects as go
import plotly.express as px


def plot_surface(x, y, z, outpath, cmap='Inferno'):
    """A Function to save an HTML interactive 3d surface plot from x, y, z
    
    Parameters:
    -----------------------------
        : x (iterable): x dimension data 
        : y (iterable): y dimension data
        : z (iterable): z dimension data
        : outpath (str): for saving the plot
        : cmap (str): a valid plotly surface plot color string
    """
    x_min = np.min(x)
    x_max = np.max(x)
    y_min = np.min(y)
    y_max = np.max(y)
    
    fig = go.Figure()
    fig.add_trace(go.Surface(z = z, 
                             x = x, 
                             y = y,
                             colorscale = 'Inferno'))

    fig.update_layout(scene = dict(aspectratio=dict(x = 2, y = 2, z = 0.5),
                                 xaxis = dict(range=[x_min, x_max],),
                                 yaxis = dict(range=[y_min, y_max])))
    
    go_offline.plot(fig, 
                    filename=outpath,
                    validate=True, 
                    auto_open=False)
    
    print(f"done. saved: `{outpath}`")
    

    
def plot_interactive_contour(x, y, z,  outpath, cmap):
    """A Function to save an HTML interactive countour plot (2D)
    
    Parameters:
    -----------------------------
        : x (iterable): x dimension data 
        : y (iterable): y dimension data
        : z (iterable): z dimension data
        : outpath (str): for saving the plot
        : cmap (str): a valid plotly contour plot color string
    """

    fig = go.Figure(data =
        go.Contour(   
            z=z,
            x=x, # horizontal axis
            y=y, # vertical axis
            colorscale=cmap
        ))

    fig.update_layout(showlegend=True)

    html_out = f'{outpath}.html'
    go_offline.plot(fig, 
                    filename=html_out,
                    validate=True, 
                    auto_open=False)
    
    print(f"done. saved: `{html_out}`")
    
    png_out = f'{outpath}.png'
    fig.write_image(png_out)
    print(f"done. saved: `{png_out}`")