"""
runs tiles and exports a .tiff with Z=n_tiles slices.

It is expected that all specific parameters are specified in
the .json parameter file being run.

EXAMPLE job run from: home/cstansbu

sbatch --job-name=TEST job_tools/script_runner.sh git_repositories/cell_tracking/imagePipeline/run_tiles_individually.py --params git_repositories/cell_tracking/imagePipeline/inputs/test.json 
"""

import argparse
import sys
import os
import time
from time import gmtime, strftime
import json
from easydict import EasyDict

# make local modules discoverable
sys.path.append("/home/cstansbu/git_repositories/cell_tracking/")
import imagePipeline.data_io.loaders as _read
import imagePipeline.data_io.writers as _write
import imagePipeline.preprocess_funcs.transform as _prep
    
    
def resolve_path(path):
    """A function to resolve the input path 

    Parameters:
    -----------------------------
        : path (str): path to the config file to use
        
    Returns:
    -----------------------------
        : path (str): full system path to the parameter file
    """
    return os.path.abspath(path)
    

if __name__ == '__main__':
    _datetime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print(f"script submitted: {_datetime}")
    full_start = time.time()
    
    """
    ARGUMENTS
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--params")
    args, unknown = parser.parse_known_args()
    PARAM_PATH = resolve_path(args.params)
    params = _read.load_params(params_path=PARAM_PATH)
    
    """
    FILE LOADING
    """
    start = time.time()
    loader = _read.cziLoader(params)  
    czi, metadata = loader.get_item(index=0)
    time_elapsed = (time.time() - start) / 60
    print(f"scene loading time: {time_elapsed:.4f}mins")
    
    """
    PREPROCESSING
    """
    start = time.time()
    transformer = _prep.ParallelTransformer(params, metadata)
    processed_czi = transformer.process_tiles(czi_data=czi.data)
    del czi
    time_elapsed = (time.time() - start) / 60
    print(f"scene processing time: {time_elapsed:.4f}mins")
    
    
    """
    OUTPUT WRITING
    """
    start = time.time()
    writer = _write.OutputWriter(params, metadata)
    writer.save_params()
    writer.save_metadata()
    writer.write_ome(processed_czi)
    time_elapsed = (time.time() - start) / 60
    print(f"scene writing time: {time_elapsed:.4f}mins")
    
    _datetime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print(f"script finished: {_datetime}")
    
    time_elapsed = (time.time() - full_start) / 60
    print(f"TOTAL TIME: {time_elapsed:.4f}mins")
    
    
    
    