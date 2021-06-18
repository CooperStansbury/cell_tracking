import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# video stuff
from celluloid import Camera
from IPython.display import HTML
from moviepy.editor import ImageSequenceClip
from IPython.display import display, Image


def simple_giffer(scene, tile=0, channel=2, outpath=None, fps=20):
    """A function to create a .gif from a scene 
    
    args:
        : scene (np.array): the scene to use
        : tile (int): the index of the tile in mosiac to choose
        : channel (int): the index of the channel to plot. if None, all will be used
        : outpath (str): the location to save the file to
        : fps (int): frames per second
    """

    if outpath is None:
        raise ValueError("Must specify outpath.")

    if channel is None:
        frames = scene[:, tile, :, :]
    else:
        frames = scene[:, tile, :, :, channel]
        frames = np.expand_dims(frames, -1)

    clip = ImageSequenceClip(list(frames), fps=20)
    clip.write_gif(outpath, fps=fps)
    print(f"saved: {outpath}")
    
    
def whole_plate_giffer(blocked_scene, channel=2, outpath=None, fps=20):
    """A function to create a .gif from a scene 
    
    args:
        : blocked_scene (np.array): the blocked_scene to use
        : channel (int): the index of the channel to plot. if None, all will be used
        : outpath (str): the location to save the file to
        : fps (int): frames per second
    """
    
    if outpath is None:
        raise ValueError("Must specify outpath.")

    if channel is None:
        frames = blocked_scene[:, :, :]
    else:
        frames = blocked_scene[:, :, :, channel]
        frames = np.expand_dims(frames, -1)

    clip = ImageSequenceClip(list(frames), fps=20)
    clip.write_gif(outpath, fps=fps)
    print(f"saved: {outpath}")
    
    
def jupyterlab_video(scene, tile, channel=2):
    """"A function to create an HTML5 video. NOTE: this will
    note work inside VSCODE.
    
    args:
        : scene (np.array): the scene to use
        : tile (int): the index of the tile in mosiac to choose
        : channel (int): the index of the channel to plot. if None, all will be used
    """
    
    fig, ax = plt.subplots()
    camera = Camera(fig)

    for t in scene:
        img = t[tile, :, :, channel]
        ax.imshow(img)
        camera.snap()

    animation = camera.animate()
    animation.to_html5_video()

    

