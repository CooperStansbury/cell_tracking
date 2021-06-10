import pandas as pd
import numpy as np
import os
import sys
import xml.etree.ElementTree as ET


class TrackMerger():
    
    
    def __init__(self, spots_path, tracks_path=None):
        """Initialiation.
        
                
        Parameters:
        ----------------------------- 
            : spots_path (str): path to spots file
            : tracks_path (str): path to tracks file
        """
        self.spots_path = spots_path
        self.tracks_path = tracks_path
        
        self.spots = pd.read_csv(self.spots_path) 
        
        if not self.tracks_path is None:
            self.tracks = self.load_tracks()
        else:
            self.tracks = None

        
    def _track_parser(self, root):
        """A function to parse the spots file
        
                       
        Parameters:
        ----------------------------- 
            : root (xml.etree.ElementTree.Element): root of xml tree
            
        Returns:
        ----------------------------- 
            : tracks_df (pd.DataFrame) of tracks
        """
        new_rows = []
        
        for spot in root.iter('particle'):
            row = spot.attrib
            
            for detection in spot.iter('detection'):
                row = {**row, **detection.attrib}
                new_rows.append(row)
        
        return pd.DataFrame(new_rows)
    
    
    def load_tracks(self):
        """A function to load the tracks file to a dataframe
                        
        Returns:
        ----------------------------- 
            : tracks_df (pd.DataFrame): track information in a dataframe
        """
        tree = ET.parse(self.tracks_path)
        tracks_df = self._track_parser(tree.getroot())
        
        new_names = {
            't': 'FRAME', 
            'x': 'POSITION_X', 
            'y':'POSITION_Y', 
            'z':'POSITION_Z'
        }
        
        tracks_df = tracks_df.rename(columns=new_names)
        return tracks_df
        
        
        
        
