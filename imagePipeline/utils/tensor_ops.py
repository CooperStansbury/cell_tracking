import numpy as np


class SceneBlocker():
    """A class to rebuild each tile into a single image """
    
    def __init__(self, scene):
        self.scene = scene
    
    def _stich(self, arr):
        """A function to stitch together tiles per
        channel per time point
        
        Parameters:
        -----------------------------
            : arr (np.array): single channel set of 9 images
            
        Returns:
        -----------------------------
            : blocked_img (np.array): a blocked image
        """
    
        row1 = np.concatenate(arr[0:3], axis=0)
        row2 = np.concatenate(arr[3:6], axis=0)
        row3 = np.concatenate(arr[6:9], axis=0)
        
        return np.concatenate([row1, row2, row3], axis=1)

    
    def block(self):
        """A function to block the tiles of the mosiac
        
        Returns:
        -----------------------------
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