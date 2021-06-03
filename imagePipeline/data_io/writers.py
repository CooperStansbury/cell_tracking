import os
import sys
import json
from easydict import EasyDict
from datetime import datetime
import numpy as np
import warnings
import aicsimageio
from aicsimageio.writers import OmeTiffWriter


#############################################################
# CLASSES
############################################################

class OutputWriter():
    """A class to write OME tiff files from numpy arrays and
    final metadata and parameters used """
    
    def __init__(self, params, metadata):
        """
        Parameters:
        ----------------------------- 
            : params (dict): dictionary of parameters specified for the run
            : metadata (dict): the czi_metadata
            : output_dir (str): output file directory for all results
        """
        self.params = params
        self.metadata = metadata
        self.output_dir = self._get_output_path()
        self.base_name = self._get_basename()
    
    
    #############################################
    # path resolution operations
    #############################################
    def _get_output_path(self):
        """A function to return the basename of the file 
                
        Returns:
        ----------------------------- 
            : out_dir (str): file name of the input
        """
        out_dir = os.path.abspath(self.params['output_directory'])
        out_dir = f"{out_dir}/"
        return out_dir
    

    def _get_basename(self):
        """A function to return the basename of the file 
                
        Returns:
        ----------------------------- 
            : base_name (str): file name of the input
        """
        base = os.path.basename(self.metadata['czi_path'])
        base_name = os.path.splitext(base)[0]
        return base_name
        
        
    #############################################
    # writers
    #############################################
    def write_ome(self, czi_data):
        """A function to save an OME .tiff 
        
        Parameters:
        ----------------------------- 
            : czi_data (np.array): 6d image array
        """
        scene = czi_data[0]
        output_file_name = f"OME_{self.base_name}.tiff"
        outpath = f"{self.output_dir}{output_file_name}"
        outpath = os.path.abspath(outpath)

        _writer = OmeTiffWriter(outpath, overwrite_file=True)
        _writer.save(data=scene)
        print(f"saved: {outpath}")
        
        
    def save_params(self):
        """A function to store the parameter file withthe datetime appended.

        Returns:
        -----------------------------
            : NA: prints confirmation
        """
        output_file_name = f"PARAMETERS_{self.base_name}.json"
        outpath = f"{self.output_dir}{output_file_name}"
        outpath = os.path.abspath(outpath)

        with open(outpath, 'w') as f:
            json.dump(self.params, f)

        print(f"Saved: `{outpath}`")
    
    
    def save_metadata(self):
        """A function to store the select czi metadata

        Returns:
        -----------------------------
            : NA: prints confirmation
        """
        output_file_name = f"METADATA_{self.base_name}.json"
        outpath = f"{self.output_dir}{output_file_name}"
        outpath = os.path.abspath(outpath)

        with open(outpath, 'w') as f:
            json.dump(self.metadata, f)

        print(f"Saved: `{outpath}`")

               