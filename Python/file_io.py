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
        # sc = np.expand_dims(sc, 2)
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
        
        # sc = self._convert()
        sc = self.scene
        _writer = OmeTiffWriter(outpath, overwrite_file=True)
        _writer.save(data=sc)
        print(f"saved: {outpath}")


class SceneBlocker():
    """A class to rebuild each tile into a single image """
    
    
    def __init__(self, scene):
        self.scene = scene
    
    def _stich(self, arr):
        """A function to stitch together tiles per
        channel per time point
        
        args:
            : arr (np.array): single channel set of 9 images
            
        returns:
            : blocked_img (np.array): a blocked image
        """
    
        row1 = np.concatenate(arr[0:3], axis=0)
        row2 = np.concatenate(arr[3:6], axis=0)
        row3 = np.concatenate(arr[6:9], axis=0)
        
        return np.concatenate([row1, row2, row3], axis=1)

    
    def block(self):
        """A function to block the tiles of the mosiac
        
        returns:
            : blocked_scene (np.array) where the `tiles`
            channel has been eliminated
        """
        blocked_scene = np.zeros(shape=(self.scene.shape[0],
                                        1416, 1920,
                                        self.scene.shape[-1]))
        
        for t in range(self.scene.shape[0]):
            for c in range(self.scene.shape[-1]):
                mosaic = self.scene[t, :, :, :, c]
                blocked_img = self._stich(mosaic)
                
                blocked_scene[t, :, :, c] = blocked_img
        return blocked_scene
               

class CZILoader():
    """A class to load a .czi image into a simple, 
    common image processing format """

    def __init__(self, filepath):
        self.path = filepath
        # self.img = AICSImage(filepath) 
        self.reader = CziReader(self.path)
        self.channel_names = self.reader.get_channel_names()
        self.scene = None 

    def restructure_scene(self, scene):
        """A function to coerse the .czi file
        into a welll-behaved numpy tensor

        args:
            : scene (int): the index of the scene (starting from 0)

        returns:
            : sc (np.array) with shape (T, C, M, Y, X)

            T: time index
            C: Channel index
            M: mosiac tile index 
            Y: Y dim
            X: X dim
        """
        sc = self.reader.data[scene]

        # # move some stuff arround
        sc = np.moveaxis(sc, 1, -1)
        self.scene = sc 

