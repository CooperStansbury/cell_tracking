
import sys
sys.path.append("./")

import json
from easydict import EasyDict

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


if __name__ == '__main__':
    
    # load the user configs
    params = load_params(params_path="imagePipeline/params.json")
    
    loader = _read.cziLoader(params)    
    czi, metadata = loader.get_item(0)
    
    ## @TODO: by-tile preprocessing
    
    ## @TODO: stiching?
    
    ## @TODO: CZI output writer
    
    
    

    
    
    