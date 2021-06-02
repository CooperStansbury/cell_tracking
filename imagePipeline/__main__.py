
import sys
import os
sys.path.append("./")

import json
from easydict import EasyDict
from datetime import datetime

import imagePipeline.data_io.loaders as _read
import imagePipeline.vision.prepare as _prep
import imagePipeline.vision.transform as _transform
    

if __name__ == '__main__':
    # load the user configs
    params = _read.load_params(params_path="imagePipeline/inputs/params.json")
    
    # load the image files
    loader = _read.cziLoader(params)  
    
    # store metadata
    loader.save_metadata(index=0, output_dir="imagePipeline/outputs/")  
    czi, _ = loader.get_item(index=0)
    
    print(type(czi))
    
    # store the parameters
    params = _read.save_params(params=params,
                               params_path="imagePipeline/inputs/params.json", 
                               output_dir="imagePipeline/outputs/")
    
    ## @TODO: by-tile preprocessing
    
    ## @TODO: stiching?
    
    ## @TODO: CZI output writer
    
    
    

    
    
    