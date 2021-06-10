
import sys
import os
sys.path.append("./")

import json
from easydict import EasyDict
from datetime import datetime

import imagePipeline.data_io.loaders as _read
import imagePipeline.data_io.writers as _write
import imagePipeline.preprocess_funcs.transform as _prep
    

if __name__ == '__main__':
    # load the user configs
    params = _read.load_params(params_path="inputs/params.json")
    
    print(params)
    
    
    

    
    
    