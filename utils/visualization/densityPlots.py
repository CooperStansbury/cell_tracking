import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.axes_grid1 import make_axes_locatable


def density_compare(init_density, final_density):
    """A function to two density plots based on differnet frames
    
    Parameters:
    -----------------------------
        : init_density (numpy.ndarray): intial density, as returned by utils.trackmate.spatialAnalysis.get_densities()
        : final_density (numpy.ndarray): intial density, as returned by utils.trackmate.spatialAnalysis.get_densities()
    """

    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)

    im1=ax1.imshow(init_density, 
                   interpolation='nearest', 
                   cmap='viridis', 
                   origin='lower')
    ax1.set_title("Initial Density")
    ax1.set_ylabel("Y Coordinate Bin")
    ax1.set_xlabel("X Coordinate Bin")
    divider = make_axes_locatable(ax1)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    plt.colorbar(im1, cax=cax)


    im2=ax2.imshow(final_density, 
                   interpolation='nearest', 
                   cmap='viridis', 
                   origin='lower')
    ax2.set_title("Final Density")
    ax2.set_xlabel("X Coordinate Bin")
    divider = make_axes_locatable(ax2)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    plt.colorbar(im1, cax=cax)