import pandas as pd
import numpy as np

# spatial analysis
from pointpats import centrography


def get_densities(points, frame_size, subregion_div):
    """A function to return density estimates for subregions of 
    size (x_subdiv, y_subdiv).
    
    Parameters:
    -----------------------------
        : points (pd.DataFrame): 2 column dataframe with POSITION_X and POSITION_Y
        : frame_size (tuple): the (x, y) size of the total area
        : subregion_div (tuple): the factor by which (x, y) of total area will be divided
        
    Returns:
    -----------------------------
        : density_matrix (2d np.array): a frame_size / subregion_div matrix of densities
        : dipersion (2d np.array): mean distance of points to center of tile
    """
    
    density_matrix = np.zeros(subregion_div)
    dipersion = np.zeros(subregion_div)
    
    subregion_area = int(frame_size[0] / subregion_div[0]) * int(frame_size[1] / subregion_div[1])
    
    x_iter = np.linspace(0, frame_size[0], subregion_div[0]+1, dtype=int)
    y_iter = np.linspace(0, frame_size[1], subregion_div[1]+1, dtype=int)
    
    total_hits = 0
    
    for i, x_coord in enumerate(x_iter[1:]):
        # note that 'i' is the 'x' index - 1
        prev_x_coord = x_iter[i]
        
        for j, y_coord in enumerate(y_iter[1:]):
            # note that 'j' is the 'y' index - 1
            prev_y_coord = y_iter[j]

            mask = (points['POSITION_X'] >= prev_x_coord) & (points['POSITION_X'] < x_coord) & \
                   (points['POSITION_Y'] >= prev_y_coord) & (points['POSITION_Y'] < y_coord)

            hits = points[mask]

            # cell densities
            n_hits = len(hits)
            total_hits += n_hits
            region_density = n_hits / subregion_area
            density_matrix[j, i] = region_density

            # dispersion stats
            disp = centrography.std_distance(hits[['POSITION_X', 'POSITION_Y']])
            disp = disp if not np.isnan(disp) else 0
            
            
            dipersion[j, i] = disp
    return density_matrix, dipersion