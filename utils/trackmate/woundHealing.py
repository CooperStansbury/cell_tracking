import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn import svm
from scipy.spatial.distance import cdist
from scipy import interpolate


def distance(x1,y1,x2,y2):
    """A function to compute distance between two points
    
    Parameters:
    -----------------------------
        : x1 (float): point in x
        : y1 (float): point in y
        : x2 (float): comparison point in x
        : y2 (float): comparison point in y
        
    Returns:
    -----------------------------
        : d (float): the distance between the points (in this case Euclidean)
    """
    d = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return d


def idw_npoint(x, y, z, xz, yz, n_point, p, r):
    """Inverse distance weighted function. The weight is a function of inverse distance. 
    The surface being interpolated should be that of a locationally dependent variable.
    
    Parameters:
    -----------------------------
        : x (iterable): vector x
        : y (iterable): vector y
        : z (iterable): vector z
        : xz (float): point in x
        : yz (float): point in y
        : n_point (int): number of points to consider
        : p (float): comparison point in y
        : r (int): block radius iteration distance
        
    Returns:  
    -----------------------------
        : z_idw (float): the functional value for z at the point p, weighted
        by the neighborhood
    """
    nf = 0
    while nf <= n_point: #will stop when np reaching at least n_point
        x_block = []
        y_block = []
        z_block = []
        r += 10 # add 10 unit each iteration
        xr_min = xz - r
        xr_max = xz + r
        yr_min = yz - r
        yr_max = yz + r
        for i in range(len(x)):
            # condition to test if a point is within the block
            if ((x[i] >= xr_min and x[i] <= xr_max) and (y[i] >= yr_min and y[i] <= yr_max)):
                x_block.append(x[i])
                y_block.append(y[i])
                z_block.append(z[i])
        nf = len(x_block) #calculate number of point in the block
    
    # calculate weight based on distance and p value
    w_list = []
    for j in range(len(x_block)):
        d = distance(xz,yz,x_block[j],y_block[j])
        if d > 0:
            w = 1 / (d**p)
            w_list.append(w)
            z0 = 0
        else:
            w_list.append(0) # if meet this condition, it means d<=0, weight is set to 0
    
    #check if there is 0 in weight list
    w_check = 0 in w_list
    if w_check == True:
        idx = w_list.index(0) # find index for weight=0
        z_idw = z_block[idx] # set the value to the current sample value
    else:
        wt = np.transpose(w_list)
        z_idw = np.dot(z_block,wt) / sum(w_list) # idw calculation using dot product
    return z_idw


def interpolate_3d(x, y, z, n=10, r=10):
    """A function to interpolate a 3d surface using the IDW function
    
    Parameters:
    -----------------------------
        : x (iterable): vector x
        : y (iterable): vector y
        : z (iterable): vector z
        : n (int): number of points in the neighborhood (both x and y)
        : r (int): block radius iteration distance
        
    Returns:  
    -----------------------------
        : x_idw_list (list): a list with rescale x points
        : y_idw_list (list): a list with rescale y points
        : z_head (list): interpolated z points
    """
    x_min = np.min(x)
    x_max = np.max(x)
    y_min = np.min(y)
    y_max = np.max(y)
    w = x_max - x_min #width
    h = y_max - y_min #length
    wn = w / n #x interval
    hn = h / n #y interval

    #list to store interpolation point and elevation
    y_init = y_min
    x_init = x_min
    x_idw_list = []
    y_idw_list = []
    z_head = []
    for i in range(n):
        xz = x_init + wn * i
        yz = y_init + hn * i
        y_idw_list.append(yz)
        x_idw_list.append(xz)
        z_idw_list = []
        for j in range(n):
            xz = x_init + wn * j
            z_idw = idw_npoint(x, y, z, xz, yz, 5, 1.5, r) #min. point=5, p=1.5
            z_idw_list.append(z_idw)
        z_head.append(z_idw_list)
        
    return x_idw_list, y_idw_list, z_head



def estimate_cut(df, kernel='poly', C=1, degree=3):
    """A function to estimate the center of the wound, from which 
    may be computed the leading cells
    
    
    Parameters:
    -----------------------------
        : df (pd.DataFrame): must have POSITION_X and POSITION_Y
        : kernel (str):  It must be one of ‘linear’, ‘poly’, ‘rbf’, 
        ‘sigmoid’, ‘precomputed’ or a callable. 
        : C (float): regularization param
        : degree (int): the degree of the svm poluynomial fit
        
    Returns:
    -----------------------------
        : cut_line (np.array): the x,y values of the center of the wound
        : init_frame (pd.DataFrame): first available timepoint with cluster ids
    """
    
    init_frame = df[df['FRAME'] == df['FRAME'].min()].reset_index()
    
    # compute Kmeans classes (always 2)
    kmeans = KMeans(n_clusters=2).fit(init_frame[['POSITION_Y']])
    init_frame.loc[:, 'CLUSTER'] = kmeans.labels_
    
    # compute maximal decision boundary
    clf = svm.SVC(C=C, kernel=kernel, degree=degree)
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
    

def leading_cells_top_bottom_dist(box):
    """A function to simplify the `box` representation from
    utils.trackmate.woundHealing.get_leading_cells() to just time points, x bins, 
    and the distance between the upper and lower cells. This is simply the distance between
    the y position of the cells on the edges of the cut.
    
    Parameters:
    -----------------------------
        : box (pd.DataFrame): output dataframe from 
        utils.trackmate.woundHealing.get_leading_cells()
        
    Returns:
    -----------------------------
        : top_bottom (pd.DataFrame): dataframe with the following columns: 
        ['FRAME', 'BOX', 'y_dist']
    """

    new_rows = []

    for t in range(box['FRAME'].max()):
        for b in range(box['BOX'].max()):

            up_mask = (box['FRAME'] == t) & (box['BOX'] == b+1) & (box['type'] == 'upper')
            lo_mask =  (box['FRAME'] == t) & (box['BOX'] == b+1) & (box['type'] == 'lower')

            y_dist = box[up_mask]['POSITION_Y'].values[0] - box[lo_mask]['POSITION_Y'].values[0]

            row = {
                'FRAME' : t,
                'BOX' : b+1,
                'y_dist' : y_dist
            }
            new_rows.append(row)

    top_bottom = pd.DataFrame(new_rows)
    return top_bottom
    

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
        : box (pd.DataFrame): leading cells in discretized x bin regions
    """
    # increase granularity of cut line
    interp = interpolate.interp1d(cut_line[:, 0], cut_line[:, 1])
    x_new = np.linspace(np.min(cut_line[:, 0]), np.max(cut_line[:, 0]), n_splits+1)
    cut_line = np.column_stack((x_new, interp(x_new)))
    
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
#         tmp['dist'] = tmp['dist'] * -1

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
    
    box = box.sort_values(by=['FRAME', 'BOX'])
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

