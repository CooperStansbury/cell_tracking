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
from pandas.io.json.normalize import nested_to_record   

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
        self.czi_list, self.spec_list = self._load_paths()


    def _resolve_paths(self):
        """A function to resolve the input path.
        
        Returns:
        -----------------------------
            : paths (list of str): file names in the 
            input directory with the specific extension
        """
        paths = []
        
        input_dir = self.params['input_directory']
        for f in os.listdir(input_dir):
            if f.endswith(self.params['input_type']):
                full_path = f"{input_dir}{f}"
                paths.append(os.path.abspath(full_path))
                
        if len(paths) > 1:
            msg = f"Current pipeline optimizzed for single image input. Found {len(paths)}."
            warnings.warn(msg)
        return paths
    
    
    def _load_paths(self):
        """A function to load the files
        
        Returns:
        -----------------------------
            : czi_list (list of aicsimageio.readers.czi_reader.CziReader): loaded images
            : spec_list (list of dict): metadata for each file
        """
        czi_list = []
        spec_list = []
        
        for _path in self.input_paths:
            _czi = CziReader(_path)
            czi_list.append(_czi)
            
            spec = self._get_spec(_czi)
            spec_list.append(spec)
            
        return czi_list, spec_list
    
    
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
        
        spec = {
            'file_shape' : czi.shape,
            'image_shape' : czi.shape[-2:],
            'n_tiles': czi.shape[3],
            'n_timepoints': czi.shape[1],
            'n_channels' : czi.shape[2],
            'channel_names': czi.get_channel_names(),
        }
        
        meta_dict = self.select_metadata(czi.metadata)
        return {**spec, **meta_dict}


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
        return self.czi_list[index], self.spec_list[index]
    
    
    def save_metadata(self, index, output_dir):
        """A function to save the metadata file for a given index
        
        Parameters:
        ----------------------------- 
            : index (int): zero indexed position of the file in self.paths
            : output_dir (str): output directory
                
        Returns:
        -----------------------------
            : NA: prints confirmation
        """
        metafile = self.spec_list[index]
        
        new_name = datetime.now().strftime(f'metadata_{index}_%d_%m_%Y.json')
        outpath = f"{output_dir}{new_name}"
            
        with open(outpath, 'w') as f:
            json.dump(metafile, f)
            
        print(f"Saved: `{outpath}`")
    