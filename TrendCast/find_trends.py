# find_trends.py (ver 1.1 delta)
# Insane script to make composite charts, combining individual plots into grids according to pattern etc
# $$$$ TRANSFORM YOUR BIGDATA INTO IMPACTFUL TRENDS $$$$
# Created, debugged and tested by Gleb Novikov
# The Visual Hub - All rights reserved - 2025 (c)
#
# !!! README !!!
#
# Organized in several functions, this script operates with any number of imput graphs (xvg, csv, whatever ..)
# to group them according to data patterns (defined in $data_types) and plot as summary charts to analyse the trends
# The current version emplements two different strategies for data visualization using Matplotlib (for images) or Plotly (for html):
#
# (i) - Matplotlib, when saving to PNG, offers the advantages of producing lightweight, universally viewable static images 
# suitable for reports and publications without requiring any special software, 
# BUT lacking interactivity such as zoom, pan, and hover information.
# (ii) - Plotly, on the other hand, saves interactive HTML files that allow users to explore data in detail through zooming, panning, and hover tools, and supports a wider range of advanced chart types with extensive customization options, making them highly portable and accessible via web browsers, though the file sizes can be larger for complex plots, and the interactive nature might not always be necessary for static presentations.

import plotly.graph_objects as go  # 25/05/2025 added Plotly
from plotly.offline import plot  # 25/05/2025 added Plotly
import matplotlib.pyplot as plt # plotting static images library
import numpy as np # operating with multi-dimensional arrays and matrices
import glob # # finds all the pathnames matching a specified pattern
import os # file and directory operations process management
import shutil # file and directory operations (practical to remove old dir with all subdirs)

# LINK YOUR DATA ACCORDING TO THE DATA TYPES to the GLOBAL VARIABLES:
data_directory = '!bigDATA' # the folder contained all input data, contained the following patterns:
# example 1: two pattern data (as provided in the example):
data_types = ['Income.Whole','Matrix.MarketCycle']
# example 1: eight pattern data which could be organized in 2x4 grid etc:
#data_types = ['Income.Whole','Matrix.MarketCycle', 'Volatility.Index', 'Distribution.Consumer', 'Volatility.MarketCycle', 'Spread.MarketCycle', 'TrendShift.XA', 'TrendShift.YA']
output_directory = '!NewTrends/' # the output folder that will contain all charts including composite matplotlib graph

# ADVANCED OPTIONS:
# Number of rows / columns defining the grid geometry of the generated summary chart
rows = 2
cols = 4
# Chart format: matplotlib produces static images, while plotlib save charts in dynamic html (similar to R) 
USE_MATPLOTLIB = True  # Toggle to switch between plotting libraries
SCALE_DATA = False # Secret option
#
# Chart quality (better DPI - more impactful trends)
DPI = 500  # super dpi for individual plots
STACKED_DPI = 800  # a bit higher DPI for summary chart to make it impactful

######## CUTTING-EDGE DATA PIPELINE ########

# thi function check all activated booleans and print them in the begining
# so that you could know what's happening !!
def get_boolean_status(debug=True):
    if debug:
        print(f"Welcome back, Master !")
        print(f"The following options are provided:")
        # Get all global variables that are booleans
        bool_vars = {k: v for k, v in globals().items() if isinstance(v, bool)}
        for name, value in bool_vars.items():
            print(f"{name} = {value}")
    else:
        print(f"Welcome back, Master !")


# this function check the format of input XY graphs and convert it to the numpy array
# (..as you could notice I put everything in numpy arrays in all of my scripts..)
def read_multicolumn_data(file_path):
    """
    Reads multicolumn data from a file, skips the first line (assumed header), and returns it as a numpy array.
    """
    try:
        data = np.genfromtxt(file_path, delimiter=None, skip_header=1, usecols=(0, 1))
        if SCALE_DATA:
            # modify the data, e.g.
            data[:, 1] *= 22  # Multiply Y-values by 100
            data[:, 0] /= 14  # Divide X-values by 10
        return data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# older version of the samy function (not used)
def OLDread_multicolumn_data(file_path):
    """
    Reads multicolumn data from a file, skips the first line (assumed header), and returns it as a numpy array.
    """
    try:
        # Read the data, skipping the first line (header)
        data = np.genfromtxt(file_path, delimiter=None, skip_header=1, usecols=(0, 1))  # Adjust usecols as needed
        return data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# added 25/05/2025
# !! switch between TWO different strategies to visualize your data !! 
# either using matplotlib (producing png images that can be combined into grid)
# or using plotly (producing html charts)
def plot_data_type(data_files, data_type, output_file, dpi):
    """Plots overlapping 2D graphs for a data type."""

    if USE_MATPLOTLIB:
        _plot_data_type_matplotlib(data_files, data_type, output_file, dpi)
    else:
        _plot_data_type_plotly(data_files, data_type, output_file)

# 1st strategy - using matplotlib
def _plot_data_type_matplotlib(data_files, data_type, output_file, dpi):
    """
    Plots overlapping 2D graphs from multiple data files of a specific data type and saves the plot to a file with specified DPI.
    """
    fig, ax = plt.subplots()
    #fig.patch.set_facecolor('lightskyblue')  # Figure background
    #ax.set_facecolor('lightskyblue') 
    has_label = False

    for file_path in data_files:
        # Check if the data_type is part of the filename
        if data_type in os.path.basename(file_path):
            data = read_multicolumn_data(file_path)
            if data is None:
                continue

            x = data[:, 0]
            y = data[:, 1]

            # Get the filename without extension and path
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            
            legend_label = file_name.replace(data_type, '').replace('_eco_trendPO', '').replace('_500val', '').replace('_', '', 1).rstrip('_')
            #legend_label = file_name.replace(data_type, '').replace('eco_trendPO', '').replace('_', '', 1).rstrip('_')
            #legend_label = file_name.replace(data_type, '').replace('eco_trendPO', '').replace('_500val', '').replace('_', '', 1).rstrip('_')


            plt.plot(x, y, label=legend_label)
            has_label = True
            
    # Set custom X and Y axis labels
    if 'Distribution' in data_type:
        plt.xlabel('Operational Cycle')
        plt.ylabel('Trend Magnitude')
    elif 'dada' in data_type:
        plt.xlabel('Days')
        plt.ylabel('Trend Magnitude')
    else:
        plt.xlabel('Quarters')
        plt.ylabel('Trend Magnitude')
        

    #plt.xlabel('Simulation Time (ns)')
    #plt.ylabel('A')
    plt.title(f'{data_type}', fontsize=18, color='orangered')
    
    # Place legend in the upper right corner
    if has_label:
    	plt.legend(loc='upper right')
    
    # Set grid style to dashed lines
    plt.grid(True, linestyle='--')
    
    # Save the plot with specified DPI (dots per inch)
    plt.savefig(output_file, dpi=dpi)
    print(f"Plot saved as {output_file} with DPI={dpi}")
    plt.close()

# 2nd strategy - using plotly
def _plot_data_type_plotly(data_files, data_type, output_file):
    """Plots using Plotly."""

    fig = go.Figure()
    has_label = False

    for file_path in data_files:
        if data_type in os.path.basename(file_path):
            data = read_multicolumn_data(file_path)
            if data is None:
                continue

            x = data[:, 0]
            y = data[:, 1]

            file_name = os.path.splitext(os.path.basename(file_path))[0]

            legend_label = file_name.replace(data_type, '').replace(
                '_eco_trendPO', '').replace('_500val', '').replace('_', '', 1).rstrip('_')

            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=legend_label))
            has_label = True

    # Set custom X and Y axis labels
    if 'Distribution' in data_type:
        fig.update_layout(xaxis_title='Operational Cycle', yaxis_title='Trend Magnitude')
    elif 'dada' in data_type:
        fig.update_layout(xaxis_title='Days', yaxis_title='Trend Magnitude')
    else:
        fig.update_layout(xaxis_title='Quarters', yaxis_title='Trend Magnitude')

    fig.update_layout(title_text=f'{data_type}', title_font_size=18, title_font_color='orangered')

    if has_label:
        fig.update_layout(legend=dict(x=1, y=1, xanchor='right', yanchor='top'))  # Upper right

    fig.update_layout(
        plot_bgcolor='white',
        xaxis=dict(gridcolor='lightgray', zerolinecolor='lightgray'),
        yaxis=dict(gridcolor='lightgray', zerolinecolor='lightgray')
    )

    # Remove any potential ".png" from the filename as it will be saved as HTML
    output_file = output_file.replace(".png", "")
    plot(fig, filename=output_file, auto_open=False)  # Save as HTML
    print(f"Plot saved as {output_file} with Plotly")
        
def stack_plots_in_grid(output_files, output_directory, rows, cols, dpi):
    """
    Stacks all generated PNG files in a grid layout using Matplotlib subplots.
    """
    num_plots = len(output_files)
    
    # Create a figure with subplots arranged in a grid
    fig, axes = plt.subplots(rows, cols, figsize=(6*cols, 6*rows))  # Adjust figsize as needed
    
    for i, output_file in enumerate(output_files):
        row = i // cols
        col = i % cols
        
        # Load the image and display it on the subplot
        img = plt.imread(output_file)
        axes[row, col].imshow(img)
        axes[row, col].axis('off')
        
    # Adjust spacing and layout
    fig.tight_layout()
    
    # Save the stacked plot
    stacked_output_file = os.path.join(output_directory, 'FinalTrends.png')
    plt.savefig(stacked_output_file, dpi=dpi)
    print(f"Stacked plots saved as {stacked_output_file} with DPI={dpi}")
    
def remove_old_trends(path):
    """
    Removes a directory and its contents if it exists.
    Creates the directory afterwards.
    """
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            print(f"Removed existing directory: {path}")
        except OSError as e:
            print(f"Error removing directory {path}: {e}")
    else:
        print(f"Directory does not exist, creating new one: {path}")

    os.makedirs(path)

# the main workflow
def find_trends():
#def find_trends(use_matplotlib=False): # for internal control only
    """!!Principal workflow of the script which generate powerfull trends!!"""
    # switch from global trigger to the local parameter if required
    #global USE_MATPLOTLIB  # Indicate you're modifying the global
    #USE_MATPLOTLIB = use_matplotlib
    #
    get_boolean_status()
    # remove old trends
    remove_old_trends(output_directory)
   

    # Get list of all input data files
    data_files = sorted(glob.glob(os.path.join(data_directory, '*')))  # Ensure files are sorted
    
    # Create a list to store output files for stacking
    output_files = []

    # main workflow
    for data_type in data_types:
        output_file = os.path.join(output_directory, f'{data_type}_plot.png')
        
        # Plot the overlapping graphs for the current data type and save the plot
        plot_data_type(data_files, data_type, output_file, DPI)
        
        # Append the output file to the list
        output_files.append(output_file)
    
    # Stack all generated PNG files in a grid layout
    if USE_MATPLOTLIB:
        stack_plots_in_grid(output_files, output_directory, rows, cols, STACKED_DPI)
    else:
        print("Skipping grid stacking - not implemented for Plotly output.")

# activate the main workflow
if __name__ == "__main__":
    find_trends()
else:
    print(f"Hidden post-processing functions are being imported from external modules!!")