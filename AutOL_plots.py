
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# read the file into a list of lines and print to separate files for different outputs
for d in [40,41]:
    with open("/home/bcelik/Results_AutOL/Grace/results_ensemble_"+str(d)+".txt",'r') as f:
        lines = f.read().split("\n")
    output_file_perf = open("/home/bcelik/Results_AutOL/Grace/Performance_Output_"+ str(d)+".txt", "w")
    output_file_retrainings = open("/home/bcelik/Results_AutOL/Grace/Retrainings_Output_"+ str(d)+".txt", "w")
    output_file_update = open("/home/bcelik/Results_AutOL/Grace/Update_Output_"+ str(d)+".txt", "w")


    word_perf = 'Test batch'
    word_drift = 'Change detected'
    word_nondrift = 'No drift but'
    word_update = 'Online model is updated'

    # iterate over lines, and print out line numbers which contain the word of interest.
    for j,line in enumerate(lines):
        if word_perf in line: # or word in line.split() to search for full word
            print("{}".format(line), file=output_file_perf)
        if word_drift in line:
            print("{}".format(line), file=output_file_retrainings)
        if word_update in line:
            print("{}".format(line), file=output_file_update)
        if word_nondrift in line:
            print("{}".format(line), file=output_file_retrainings)


    output_file_perf.close()
    output_file_retrainings.close()
    output_file_update.close()

#Read data from the output files
# Get test scores and batch numbers
results={}
retrainings={}
for d in [40, 41]:  # data streams
    #Get performance
    read_perf = pd.read_table("/home/bcelik/Results_AutOL/Grace/Performance_Output_" + str(d) + ".txt", header=None, sep=' ')
    results["AutOL_Ensemble_Data_" + str(d)] = (read_perf.iloc[:, [3, 6]])
    results["AutOL_Ensemble_Data_" + str(d)].columns = ['Batch number', 'Test score']
    results["AutOL_Ensemble_Data_" + str(d)]['Test score'] = results["AutOL_Ensemble_Data_" + str(d)]['Test score'].str.rstrip('%').astype('float') / 100.0

    #Get retraining points and types - No : no drift training point, Change: drift training point
    if os.path.getsize("/home/bcelik/Results_AutOL/Grace/Retrainings_Output_" + str(d) + ".txt") > 0:
        read_retraining = pd.read_table("/home/bcelik/Results_AutOL/Grace/Retrainings_Output_" + str(d) + ".txt", header=None, sep=' ')
        retrainings["AutOL_Ensemble_Data_" + str(d)] = read_retraining.iloc[:, [5,0]]
        retrainings["AutOL_Ensemble_Data_" + str(d)].columns = ['Batch number', 'Type']

    #Get model switch to ensemble or AutOL output
    if os.path.getsize("/home/bcelik/Results_AutOL/Grace/Retrainings_Output_" + str(d) + ".txt") > 0:
        read_update = pd.read_table("/home/bcelik/Results_AutOL/Grace/Update_Output_" + str(d) + ".txt", header=None, sep=' ')
        retrainings["AutOL_Ensemble_Data_" + str(d)]['Model update'] = read_update.iloc[:, [6]]

#Plot-1 Performance

figs = {}

SMALL_SIZE = 20
MEDIUM_SIZE = 25
BIGGER_SIZE = 35

data_names = ["Electricity", "Airlines",  "IMDB", "Vehicle", "SEA - High Abrupt Drift", "HYPERPLANE - High Gradual Drift",
              "SEA - High Mixed Drift"]

for d in [40]:

    plt.rcParams["figure.figsize"] = (25, 20)
    plt.rcParams["axes.labelsize"] = ('x-large')
    figs[d] = plt.figure()
    figs[d], ax = plt.subplots(1, 1, sharex='col', sharey='row', constrained_layout=True)

    ax.set(xlabel="Batch #", ylabel="Accuracy")
    ax.grid(linestyle='--', linewidth=1)

    ax.set_title('AutOL Prequential Performance - Data '+data_names[int(d/10)])

    l3 = ax.plot(results["AutOL_Ensemble_Data_" + str(d)]['Batch number'],
                    results["AutOL_Ensemble_Data_" + str(d)]['Test score'],
                    label='AutOL_Without_Extra_Training', lw=4, color='b')
    l2 = ax.plot(results["AutOL_Ensemble_Data_" + str(d+1)]['Batch number'],
                    results["AutOL_Ensemble_Data_" + str(d+1)]['Test score'],
                    label='AutOL_With_Extra_Training', lw=4, color='r')
    # l1 = ax[i].plot(results["Auto_"+str(i+1)]["Option_1"]["Data_"+str(d)]['Batch number'],results["Auto_"+str(i+1)]["Option_1"]["Data_"+str(d)]['Test score'],label = '1. Best model adaptation after drift', lw=3, color='g')

    if os.path.getsize("/home/bcelik/Results_AutOL/Grace/Retrainings_Output_"+ str(d)+".txt") > 0:
        i=0
        for xc in retrainings["AutOL_Ensemble_Data_" + str(d)]['Batch number']:
            if retrainings["AutOL_Ensemble_Data_" + str(d)]['Type'].iloc[i] == "Change":
                ax.axvline(x=xc, linestyle=':', color='b')
            else:
                ax.axvline(x=xc, linestyle='solid', color='b')
            i=i+1

    if os.path.getsize("/home/bcelik/Results_AutOL/Grace/Retrainings_Output_"+ str(d+1)+".txt") > 0:
        i=0
        for xc in retrainings["AutOL_Ensemble_Data_" + str(d+1)]['Batch number']:
            if retrainings["AutOL_Ensemble_Data_" + str(d+1)]['Type'].iloc[i] == "Change":
                ax.axvline(x=xc, linestyle=':', color='r')
            else:
                ax.axvline(x=xc, linestyle='solid', color='r')
            i=i+1

    handles, labels = ax.get_legend_handles_labels()
    plt.legend(handles, labels,
               loc='upper center',
               bbox_to_anchor=(0.5, -0.2),
               ncol=1,
               borderaxespad=0.1,
               title="Options",
               prop={'size': 30})
    #plt.yticks(np.arange(results["AutOL_Ensemble_Data_" + str(d)]['Test score'], results["AutOL_Ensemble_Data_" + str(d)]['Test score']+0.1, 0.1))

    plt.plot()
    figs[d].show()
    figs[d].savefig("/home/bcelik/Results_AutOL/Performance_Data"+str(d)+".png")