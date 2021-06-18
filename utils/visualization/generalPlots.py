# plotting
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns



def joint_plot(df, frame_size=None):
    """A function to produce a rather ugly joint plot 
    
      
    Parameters:
    -----------------------------
        : df (pd.DataFrame): is assumed to have columns POSITION_X and POSITION_Y
        : frame_size (tuple): the axis limits
        
    Returns:
    -----------------------------
        : joint_plot (seaborn.axisgrid.JointGrid)
    """
    g = sns.jointplot(data=df,
                  x='POSITION_X',
                  y='POSITION_Y',
                  s=10,
                  alpha=0.7,
                  xlim=(0, frame_size[0]),
                  ylim=(0, frame_size[1]),
                  marginal_kws=dict(bins=100),
                  color='black')

    g.plot_joint(sns.kdeplot, 
                 color="r", 
                 zorder=0, 
                 levels=10, 
                 alpha=0.6)
    
    g.ax_joint.set_xlabel('X Coordinate')
    g.ax_joint.set_ylabel('Y Coordinate')
