import os
import sys
import re
import datetime
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

#General post processing functions
#get the time data first
#first, open up every castep file 

#cell_file_directory holds the name of the directory for the cell files
def write_to_log(text):
    os.system("echo '{}' >> /home/riesel/Tsach/tsach276/more_organized/log_file.txt".format(text))
    
def read(filename): 
    file = open(filename, "r")
    file_read = file.read()
    file.close()
    return file_read

def readlines(filename):
    file = open(filename,"r")
    file_lines = file.readlines()
    file.close()
    return file_lines

def collectdata(data, storage_directory, cutoff_energy, kpoint_spacing, pressure, new_directory_name):
    
    #ex: storage_directory ="/pool001/riesel/convergence_testing_redone"
    #ex result direcotry = LaRu4Bi12-600.0-0.4-1.0
    new_directory_name = storage_directory + "/" + "LaRu4Bi12" + "-" + cutoff_energy + "-" + kpoint_spacing + "-" + pressure+"/"
    file_names = os.listdir(new_directory_name)

    #for every file in that folder
    for file_name in file_names:
        #if that file is a castep file
        if file_name[-6:] == "castep":
            sublist = []
            sublist.append(float(cutoff_energy))
            sublist.append(float(kpoint_spacing))
            sublist.append(float(pressure))
            
            sublist.append(file_name[:-7])
            #if the n extra bands error is in the castep file
            castep_file_lines = readlines(new_directory_name + file_name)
            for line in castep_file_lines:
                if "Total time" in line:
                    sublist.append(float(line[-9:-3]))

                
                elif " BFGS: Final Enthalpy" in line:
                    pattern = r'[-+]?\d*\.\d+|[-+]?\d+.\d*'
                    match = re.findall(pattern, line)
                    number = float(match[0])*10**float(match[1])
                    sublist.append(float(f'{number:.8f}'))
                    
            data.append(sublist)

    return data 


def calc_aggregate_data(df, type, cutoff_energies, kpoint_spacings, pressures):
    
    if type  == 'cutoff_energies':
        aggregate_data = []
        for cutoff_energy in cutoff_energies:
            sublist = []
            sublist.append(float(cutoff_energy))
            sublist.append(df[df["Cutoff Energy"]==float(cutoff_energy)]["Time"].mean())
            aggregate_data.append(sublist) 
            
        return aggregate_data
    
    elif type  == 'kpoint_spacings':
        aggregate_data = []
        for kpoint_spacing in kpoint_spacings:
            sublist = []
            sublist.append(float(kpoint_spacing))
            sublist.append(df[df["kpoint_spacing"]==float(kpoint_spacing)]["Time"].mean())
            aggregate_data.append(sublist)
            
        return aggregate_data
    
    elif type  == 'pressures':
        aggregate_data = []
        for pressure in pressures:
            sublist = []   
            sublist.append(float(pressure))
            sublist.append(df[df["pressure"]==float(pressure)]["Time"].mean())
            aggregate_data.append(sublist)

        return aggregate_data 

def plotter_assistant(name, axs, row_idx, col_idx, x, y, time):
    # Plot the line for Free Energy
    axs[row_idx][col_idx].plot(x, y, label='Free Energy')
    axs[row_idx][col_idx].set_ylabel('Free Energy')
    
    # Create a secondary y-axis for Time
    axs_time = axs[row_idx][col_idx].twinx()
    axs_time.plot(x, time, color='red', label='Time')
    axs_time.set_ylabel('Time')
    
    # Customize the subplot
    axs[row_idx][col_idx].set_title(f' {name}')
    axs[row_idx][col_idx].legend(loc='upper left')
    axs_time.legend(loc='upper right')
    
    # Format the y-axis labels to three decimal places
    axs[row_idx][col_idx].yaxis.set_major_formatter(ticker.FormatStrFormatter('%.3f'))
    axs_time.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.3f'))

def plotter(df, type, cutoff_energy, kpoint_spacing, pressure):
    #Essentially, we want to view the results for changing the cutoff energy at a particular kpoint mesh and pressure

    # Initialize a dictionary to store lines for each name
    # Get unique names
    names = df['Name'].unique()

    # Calculate the number of rows and columns for subplots
    num_plots = len(names)
    num_rows = (num_plots + 2) // 3  # Adjusting for uneven number of plots
    num_cols = min(num_plots, 3)

    # Create the grid of subplots
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(12, 3 * num_rows), sharex=True)

    # Flatten the axs array if needed
    if num_plots == 1:
        axs = [axs]

    if type == 'cutoff energy':
        # Iterate over each subplot
        for i, name in enumerate(names):
            # Calculate the row and column indices for the current subplot
            row_idx = i // num_cols
            col_idx = i % num_cols
            
            # Filter DataFrame by name
            subset = df[df['Name'] == name]
            subset = subset[subset['kpoint_spacing'] == float(kpoint_spacing)]
            subset = subset[subset['pressure'] == float(pressure)]
             
            # Get x and y values for the name
            x = subset['Cutoff Energy']
            y = subset['Free Energy']
            time = subset['Time']
            
            plotter_assistant(name, axs, row_idx, col_idx, x, y, time)

        # Remove any empty subplots
        if num_plots < num_rows * num_cols:
            for i in range(num_plots, num_rows * num_cols):
                fig.delaxes(axs[i // num_cols][i % num_cols])

        # Customize the overall plot
        plt.xlabel('Cutoff Energy')

        # Adjust spacing between subplots
        plt.tight_layout()

        # Display the plot
        plt.show()
        #### 
        plt.savefig("Images/cutoff_energy.png")
        plt.close()

    elif type == 'kpoint spacing':
        # Iterate over each subplot
        for i, name in enumerate(names):
            # Calculate the row and column indices for the current subplot
            row_idx = i // num_cols
            col_idx = i % num_cols
            
            # Filter DataFrame by name
            subset = df[df['Name'] == name]
            subset = subset[subset['Cutoff Energy'] == float(cutoff_energy)]
            subset = subset[subset['pressure'] == float(pressure)]
             
            # Get x and y values for the name
            x = subset['kpoint_spacing']
            y = subset['Free Energy']
            time = subset['Time']
            
            plotter_assistant(name, axs, row_idx, col_idx, x, y, time)

        # Remove any empty subplots
        if num_plots < num_rows * num_cols:
            for i in range(num_plots, num_rows * num_cols):
                fig.delaxes(axs[i // num_cols][i % num_cols])

        # Customize the overall plot
        plt.xlabel('Kpoint Spacing')

        # Adjust spacing between subplots
        plt.tight_layout()

        # Display the plot
        plt.show()
        ####
        plt.savefig("Images/kpoint_spacing.png")
        plt.close()

    elif type == 'pressure':
        # Iterate over each subplot
        for i, name in enumerate(names):
            # Calculate the row and column indices for the current subplot
            row_idx = i // num_cols
            col_idx = i % num_cols
            
            # Filter DataFrame by name
            subset = df[df['Name'] == name]
            subset = subset[subset['Cutoff Energy'] == float(cutoff_energy)]
            subset = subset[subset['kpoint_spacing'] == float(kpoint_spacing)]
             
            # Get x and y values for the name
            x = subset['pressure']
            y = subset['Free Energy']
            time = subset['Time']
            
            plotter_assistant(name, axs, row_idx, col_idx, x, y, time)

        # Remove any empty subplots
        if num_plots < num_rows * num_cols:
            for i in range(num_plots, num_rows * num_cols):
                fig.delaxes(axs[i // num_cols][i % num_cols])

        # Customize the overall plot
        plt.xlabel('Pressure')

        # Adjust spacing between subplots
        plt.tight_layout()

        # Display the plot
        plt.show()
        ####
        plt.savefig("Images/pressure.png")
        plt.close()