
import sys
import os
sys.path.append("./")

import json
from easydict import EasyDict
from datetime import datetime

import imagePipeline.data_utils.image_reader as _read
import imagePipeline.data_utils.tensor_ops as _ops
import imagePipeline.vision.prepare as _prep
import imagePipeline.vision.transform as _transform


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
    return params


def save_params(params, params_path, output_dir):
    """A function to store the parameter file withthe datetime appended.
    
    
        Parameters:
        ----------------------------- 
           : params (EasyDict): dictionary of parameters to store
           : input_path (str): input path to the parameter configuration
           : output_dir (str): output directory
            
        Returns:
        -----------------------------
            : NA: prints confirmation
    """
    base = os.path.basename(params_path)
    base_name = os.path.splitext(base)[0]
    
    new_name = datetime.now().strftime(f'{base_name}_%d_%m_%Y.json')
    outpath = f"{output_dir}{new_name}"
    
    with open(outpath, 'w') as f:
        json.dump(params, f)
        
    print(f"Saved: `{outpath}`")
    
    

if __name__ == '__main__':
    # load the user configs
    params = load_params(params_path="imagePipeline/inputs/params.json")
    
    # load the image files
    loader = _read.cziLoader(params)  
    
    # store metadata
    loader.save_metadata(index=0, output_dir="imagePipeline/outputs/")  
    czi, _ = loader.get_item(index=0)
    
    print(type(czi))
    
    # store the parameters
    params = save_params(params=params,
                         params_path="imagePipeline/inputs/params.json", 
                         output_dir="imagePipeline/outputs/")
    
    ## @TODO: by-tile preprocessing
    
    ## @TODO: stiching?
    
    ## @TODO: CZI output writer
    
    
    

    
    
    