import numpy as np
import skimage
from skimage.feature import blob_log
import matplotlib.pyplot as plt
import matplotlib


class CellDetector():
    """A class to wrap individual cell detection """

    def __init__(self, image):
        self.image = image
        self.cells = None


    def get_cells_LoG(self, set_attr=True):
        """A function to return a list of cells 

        args:
            : set_attr (bool): if true, sets self.cells and DOES NOT RETURN
        
        returns:
            : cells (np.array): first two columns are center coords, 3rd is radius 
        """
        cells = blob_log(self.image, 
                         min_sigma=9, 
                         max_sigma=12,
                         num_sigma=1, 
                         threshold=1000)
        # compute the radii
        cells[:, 2] = cells[:, 2] * np.sqrt(2)
        
        if set_attr:
            self.cells = cells 
        else:
            return cells


    def plot_contour(self):
        """A function to plot the contour of an image"""
        fig, ax = plt.subplots(figsize=(5, 5))
        qcs = ax.contour(self.image, origin='image')
        

    def plot_cells(self):
        """A function to plot cells and an image in the same window """

        if self.cells is None:
            raise ValueError("Set cells with self.get_cells(set_attr=True)")

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        ax.imshow(self.image, cmap='plasma')

        for cell in self.cells:
            y, x, r = cell
            c = plt.Circle((x, y), r, color='yellow', linewidth=2, fill=False)
            ax.add_patch(c)
        plt.axis(False)