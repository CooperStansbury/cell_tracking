"""
wrapper around czi loading to coerse into standard structure
"""

import os
import sys
import json
from easydict import EasyDict
from datetime import datetime
import numpy as np
import warnings
from aicsimageio.readers import CziReader
from xml.etree import ElementTree
import xmltodict
from pandas.io.json._normalize import nested_to_record   


############################################################
# FUNCTIONS
############################################################
    
    
def load_params(params_path):
    """A function to load the configuration params
    
    Parameters:
    -----------------------------
        : params_path (str): path to the config file to use
        
    Returns:
    -----------------------------
        : params (EasyDict): a dictionary with parameters
    """
    with open(params_path) as f:
        params = EasyDict(json.load(f))
        
    params['parameter_input_path'] = params_path
    return params
    

############################################################
# CLASSES
############################################################

class cziLoader():
    """A class to load a .czi image into a simple, 
    common image processing format """

    def __init__(self, params):
        """
        Parameters:
        -----------------------------
            : params (dict): user configs
        """
        self.params = params
        self.input_paths = self._resolve_paths()

        
    #############################################
    # path resolution operations
    #############################################
    def _resolve_paths(self):
        """A function to resolve the input path.
        
        Returns:
        -----------------------------
            : paths (list of str): file names in the 
            input directory with the specific extension
        """
        paths = []
        
        data_dir = os.path.abspath(self.params['data_directory'])
        
        for f in self.params['files']:
            full_path = f"{data_dir}/{f}"
            paths.append(os.path.abspath(full_path))
            
        if len(paths) > 1:
            msg = f"Current pipeline optimized for single image input. Found {len(paths)}."
            warnings.warn(msg)
            
        return paths
    
    
    #############################################
    # metadata operations 
    #############################################
    def select_metadata(self, metadata):
        """A function to parse the czi metadata. Note - 
        this is a gross way to do this.
        
        Parameters:
        ----------------------------- 
           : metadata (lxml.etree._Element): czi.metadata
            
        Returns:
        -----------------------------
            : select_metadata (dict): with selected metadata
        """
        
        select_metadata = {}
        xml_str = ElementTree.tostring(metadata, encoding='unicode')
        root_dict = xmltodict.parse(xml_str)
        
        meta_dict = root_dict['ImageDocument']['Metadata']
        
        # get application information
        select_metadata['ImagePixelSize'] = meta_dict['ImageScaling']['ImagePixelSize']
        select_metadata['Application_Name'] = meta_dict['Information']['Application']['Name']
        select_metadata['Application_Version'] = meta_dict['Information']['Application']['Version']
        select_metadata['Application_Build'] = meta_dict['Information']['Application']['BuildId']
        
        # get scaling details
        for k, v in meta_dict['Scaling']['AutoScaling'].items():
            new_key = f"Scaling_{k}"
            select_metadata[new_key] = v
            
        for k in meta_dict['Scaling']['Items']['Distance']:
            new_key = f"Scaling_Dimension_{k['@Id']}"
            new_value = f"{k['Value']}{k['DefaultUnitFormat']}"
            select_metadata[new_key] = new_value
              
        # get channel acquisition details
        for k,v in meta_dict['Information']['Image'].items():
            if isinstance(v, str):
                select_metadata[k] = v
                
            if k == 'Dimensions':
                chan = v['Channels']['Channel']
                for c in chan:
                    channel_name = c['@Name']
                    for i, j in c.items():
                        new_key = channel_name + "_" + i
                        if '@' in i:
                            continue
                        if isinstance(j, str):
                            select_metadata[new_key] = j
                        elif j is not None:
                            new_j = ".....".join([f"{l}={p}" for l,p in nested_to_record(dict(j)).items()])
                            select_metadata[new_key] = new_j
        return select_metadata
    
    
    def _get_spec(self, czi):
        """A function to report all metadata for a loaded file.
        
        Parameters:
        ----------------------------- 
            : czi (aicsimageio.readers.czi_reader.CziReader)
                
        Returns:
        -----------------------------
            : spec (dict): different parameters that may be useful later on
        """
        _names = czi.get_channel_names()
        spec = {
            'file_shape' : czi.shape,
            'image_shape' : czi.shape[-2:],
            'n_tiles': czi.shape[3],
            'n_timepoints': czi.shape[1],
            'n_channels' : czi.shape[2],
            'channel_names': _names
        }
        
        spec['channel_map'] = dict(zip( _names, range(len(_names))))
        
        meta_dict = self.select_metadata(czi.metadata)
        return {**spec, **meta_dict}

    
    #############################################
    # item selection
    #############################################
    def get_item(self, index):
        """A function to return the image and metadata for a single file
        
        Parameters:
        ----------------------------- 
            : index (int): zero indexed position of the file in self.paths
                
        Returns:
        -----------------------------
            : czi (image array): the images
            : metadata (dict): metadata for the images
        """
        path = self.input_paths[index]
        
        # load czi 
        czi = CziReader(path)
        
        # load metadata
        metadata = self._get_spec(czi)
        metadata['czi_path'] = path        
        
        return czi, metadata