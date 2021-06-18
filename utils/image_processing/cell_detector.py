import numpy as np
import skimage
from scipy import ndimage as ndi
from skimage.feature import blob_log
import matplotlib.pyplot as plt
import matplotlib
from skimage import (
    color, feature, filters, measure, morphology, segmentation, util, exposure
)


def get_cells_LoG(image):
        """A function to return an array of cells 

        args:
            : image (np.array): the input image
        
        returns:
            : cells (np.array): first two columns are center coords, 3rd is radius 
        """
        cells = blob_log(image, 
                         min_sigma=9, 
                         max_sigma=12,
                         num_sigma=1, 
                         threshold=1000)
        # compute the radii
        cells[:, 2] = cells[:, 2] * np.sqrt(2)
        return cells


def get_cells_mutli_otsu(image):
    """A function to return a list of cells 
    
    args:
        : image (np.array): the input image
        
    returns:
        : cells (np.array): first two columns are center coords, 3rd is radius 
    """
    thresholds = filters.threshold_multiotsu(image , classes=2)
    cells = image > thresholds[0]
    distance = ndi.distance_transform_edt(cells)
    local_max_coords = feature.peak_local_max(distance, min_distance=7)
    local_max_mask = np.zeros(distance.shape, dtype=bool)
    local_max_mask[tuple(local_max_coords.T)] = True
    markers = measure.label(local_max_mask)
    segmented_cells = segmentation.watershed(-distance, markers, mask=cells)
    return segmented_cells

        
def plot_cells_LoG(image, cells):
    """A function to plot cells and an image in the same window 
    
    args:
        : image (np.array): the input image
        : cells (np.array): detected cells (assume 3D array with y, x, r)
    """
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.imshow(image, cmap='plasma')
    for cell in cells:
        y, x, r = cell
        c = plt.Circle((x, y), r, color='yellow', linewidth=2, fill=False)
        ax.add_patch(c)
    plt.axis(False)