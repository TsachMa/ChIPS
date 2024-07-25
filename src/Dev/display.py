import csv
import matplotlib.pyplot as plt
import numpy as np
import sys

def read_csv(csv_filename):
    """
    Read the data from the CSV file.
    """
    data = []
    with open(csv_filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def display_aggregate_data(data):
    """
    Display the aggregate data as a table and plot a graph.
    """
    nbands_rounds = []
    nbands_errors = []
    completion_data = []
    completed_jobs = []

    for row in data:
        nbands_rounds.append(int(row['n-bands round']))
        nbands_errors.append(int(row['n-bands error']))
        completion_data.append(int(row['completed']))
        completed_jobs.append(int(row['Completed Jobs']))

    # Display aggregate data as a table
    table_data = list(zip(nbands_rounds, nbands_errors, completion_data, completed_jobs))
    headers = ['n-bands round', 'n-bands error', 'Completion Status', 'Completed Jobs']
    print("Aggregate Data:")
    print("{:<15}{:<15}{:<20}{:<15}".format(*headers))
    print("-" * 65)
    for row in table_data:
        print("{:<15}{:<15}{:<20}{:<15}".format(*row))
    print()

    # Plot a graph of nbands rounds, nbands errors, and completed jobs
    x = np.arange(len(nbands_rounds))
    width = 0.2
    fig, ax = plt.subplots()
    ax.bar(x - width, nbands_rounds, width, label='n-bands round')
    ax.bar(x, nbands_errors, width, label='n-bands error')
    ax.bar(x + width, completed_jobs, width, label='Completed Jobs')
    ax.set_xlabel('Data Entry')
    ax.set_ylabel('Count')
    ax.set_title('Aggregate Data')
    ax.set_xticks(x)
    ax.set_xticklabels([str(round_num) for round_num in nbands_rounds])
    ax.legend()
    plt.show()

def display_individual_data(data):
    """
    Display the individual data as overlayed histograms.
    """
    suggested_extra_bands = []
    for row in data:
        suggested_extra_bands.append(int(row['suggested extra bands']))

    # Plot overlayed histograms of suggested extra bands
    plt.hist(suggested_extra_bands, bins=10, alpha=0.5, label='Individual Data')
    plt.xlabel('Suggested Extra Bands')
    plt.ylabel('Count')
    plt.title('Individual Data')
    plt.legend()
    plt.show()

def main(directory_path):
    csv_filename = directory_path + "/log.csv"
    data = read_csv(csv_filename)

    display_aggregate_data(data)
    display_individual_data(data)

if __name__ == "__main__":
    directory_path = sys.argv[1]
    main(directory_path)
