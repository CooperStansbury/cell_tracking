import pandas as pd
import numpy as np

def get_leading_cells(df, cut_line, n_splits):
    """A function to collect the cells closest to the incision line
    
    
    Parameters:
    -----------------------------
        : df (pd.DataFrame): must have POSITION_X and POSITION_Y
        : cut_line (float): the y-axis value of the center of the wound
        : n_splits (float): number of slices in the x-zxis used to define supporting cells
        
    Returns:
    -----------------------------
        : df (pd.DataFrame): dataframe with column corrected in place
    """
    
    x_iter = np.linspace(0, df['POSITION_X'].max(), n_splits+1, dtype=int)
    
    boxes = []

    for i, x_coord in enumerate(x_iter[1:]):
        prev_x_coord = x_iter[i]

        # top box
        mask = ((df['POSITION_X'] > prev_x_coord) & (df['POSITION_X'] < x_coord) ) \
             & ((df['POSITION_Y'] > cut_line))

        tmp = df[mask].groupby(['FRAME'], as_index=False).agg({
            'POSITION_Y' : np.min
        })

        tmp['POSITION_X'] = (x_coord + prev_x_coord) / 2
        tmp['BOX'] = i + 1
        tmp['type'] = 'upper'

        boxes.append(tmp)

        # bottom box
        mask = ((df['POSITION_X'] > prev_x_coord) & (df['POSITION_X'] < x_coord) ) \
             & ((df['POSITION_Y'] < cut_line) )

        tmp = df[mask].groupby(['FRAME'], as_index=False).agg({
            'POSITION_Y' : np.max
        })

        tmp['POSITION_X'] = (x_coord + prev_x_coord) / 2
        tmp['BOX'] = i + 1
        tmp['type'] = 'lower'

        boxes.append(tmp)

    box = pd.concat(boxes, ignore_index=True)

    box['FRAME_NORM'] = (box['FRAME'] /  box['FRAME'].max())
    
    return box