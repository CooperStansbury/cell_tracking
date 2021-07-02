import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn import svm
from scipy.spatial.distance import cdist




def estimate_cut(df):
    """A function to estimate the center of the wound, from which 
    may be computed the leading cells
    
    
    Parameters:
    -----------------------------
        : df (pd.DataFrame): must have POSITION_X and POSITION_Y
        
    Returns:
    -----------------------------
        : cut_line (np.array): the x,y values of the center of the wound
        : init_frame (pd.DataFrame): first available timepoint with cluster ids
    """
    
    init_frame = df[df['FRAME'] == df['FRAME'].min()].reset_index()
    
    # compute Kmeans classes (always 2)
    kmeans = KMeans(n_clusters=2).fit(init_frame[['POSITION_X', 'POSITION_Y']])
    init_frame.loc[:, 'CLUSTER'] = kmeans.labels_
    
    # compute maximal decision boundary
    clf = svm.SVC(kernel='poly', degree=3)
    clf.fit(init_frame[['POSITION_X', 'POSITION_Y']], init_frame['CLUSTER'])
    
    # set up meshgrid
    xx = np.linspace(init_frame['POSITION_X'].min(), init_frame['POSITION_X'].max())
    yy = np.linspace(init_frame['POSITION_Y'].min(), init_frame['POSITION_Y'].max())
    YY, XX = np.meshgrid(yy, xx)
    xy = np.vstack([XX.ravel(), YY.ravel()]).T
    Z = clf.decision_function(xy).reshape(XX.shape)
    
    cs = plt.contour(XX, YY, Z, levels=[-1, 0, 1])
    
    plt.close()
    cut_line = cs.collections[1].get_paths()[0].vertices 
    return cut_line, init_frame
    
    

def get_leading_cells(df, cut_line, n_splits):
    """A function to collect the cells closest to the incision line.
    
    NOTE: this assumes that the cut is essentially parallel to the x-axis
    
    
    Parameters:
    -----------------------------
        : df (pd.DataFrame): must have POSITION_X and POSITION_Y
        : cut_line (n.array): the x,y values of the center of the wound
        : n_splits (float): number of slices in the x-zxis used to define supporting cells
        
    Returns:
    -----------------------------
        : df (pd.DataFrame): dataframe with column corrected in place
    """
    # structure the cut points along the line
    _line_iter = np.array_split(cut_line, n_splits+1)
    _line_iter = np.asarray([x[0] for x in _line_iter])    
    _line_iter = _line_iter[_line_iter[:, 0].argsort()]
    boxes = []
    
    for i, coord in enumerate(_line_iter[1:]):
        prev_coord = _line_iter[i]
        pt = np.array(coord).reshape(1,2)

        # top box
        mask = ((df['POSITION_X'] > prev_coord[0]) & (df['POSITION_X'] < coord[0]) ) \
             & ((df['POSITION_Y'] > coord[1]))

        # get set of points in region
        tmp = df[mask].reset_index()
        
        # compute euclidean distance to cut line
        _xy = tmp[['POSITION_X', 'POSITION_Y']].to_numpy()
        dists = cdist(_xy, pt)
        tmp['dist'] = dists
        
        # get cell with minimum distance to cut
        tmp['min_dist'] = tmp['dist'].groupby(tmp['FRAME']).transform(np.min)
        tmp = tmp[tmp['dist'] == tmp['min_dist']]
        
        tmp = tmp.drop_duplicates(subset=['FRAME', 'dist'])

        tmp['POSITION_X'] = (coord[0] + prev_coord[0]) / 2
        tmp['BOX'] = i + 1
        tmp['type'] = 'upper'

        boxes.append(tmp)
    
        # bottom box
        mask = ((df['POSITION_X'] > prev_coord[0]) & (df['POSITION_X'] < coord[0]) ) \
             & ((df['POSITION_Y'] < coord[1]) )

        # get set of points in region
        tmp = df[mask].reset_index()
        
        # compute euclidean distance to cut line
        _xy = tmp[['POSITION_X', 'POSITION_Y']].to_numpy()
        dists = cdist(_xy, pt)
        tmp['dist'] = dists
        
        # 
        tmp['min_dist'] = tmp['dist'].groupby(tmp['FRAME']).transform(np.min)
        tmp = tmp[tmp['dist'] == tmp['min_dist']]
        
        tmp = tmp.drop_duplicates(subset=['FRAME', 'dist'])

        tmp['POSITION_X'] = (coord[0] + prev_coord[0]) / 2
        tmp['BOX'] = i + 1
        tmp['type'] = 'lower'

        boxes.append(tmp)

    box = pd.concat(boxes, ignore_index=True)
    box['FRAME_NORM'] = (box['FRAME'] /  box['FRAME'].max())
    return box
    

def get_leading_cells_simple(df, cut_line, n_splits):
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

