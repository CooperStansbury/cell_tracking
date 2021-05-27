import os
import sys
from aicsimageio import AICSImage
from aicsimageio.readers import CziReader
from aicsimageio.writers import OmeTiffWriter
from matplotlib.pyplot import sca, xscale
import numpy as np
import pandas as pd


class OME_writer():
    """A class to write OME tiff files from numpy arrays """
    
    def __init__(self, scene):
        self.scene = scene
        
    def restructure_scene(self):
        """A function to coerse a tensor into a format that
        may be written as an OME file

        returns:
            : sc (np.array) with same shape as input `.czi` but
            single dimension along the tile dimension
        """
        sc = self.scene[:, :, :, :]
        sc = np.moveaxis(sc, -1, 1)
        self.scene = sc
        
    
    def _convert(self):
        """A function to convert the scene into an image
        object"""
        return AICSImage(self.scene)
    
    def write(self, outpath=None):
        """A function to save an OME .tiff 
        
        args:
            : outpath (str): output file path
        """
        if outpath is None:
            raise ValueError("outpath cannot be None.")
        sc = self.scene
        _writer = OmeTiffWriter(outpath, overwrite_file=True)
        _writer.save(data=sc)
        print(f"saved: {outpath}")

               

