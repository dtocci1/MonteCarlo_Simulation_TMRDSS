'''
File: mcSim.py
Author: Dylan Tocci
Version: 1.0
Description:
    This program will run a Monte Carlo (MC) Simulation to simulate system reliability for a fault-tolerant storage system. 
    There will be two designs simulated, a TMR design, as well as a Dynamic Standby Sparing design. 
    The program will output:
        - failure frequency
        - average failure downtime
        - average uptime

    Each timestep of the simulation will represent a quarter day due to hard drive failure rate (very resilient), and speed of repair

System Components:
    - Storage system (failure rate for entire system, not individual drives)
    - Buses
    - Server
    - Spare if DSS

Failure Rates are based off of the following sources/assumptions:
    - Storage system is a HGST HMS5C4040ALE640 drives
        - Fail rate each is about .65% yearly or 0.00178082192 a day
            - Source: https://www.backblaze.com/blog/backblaze-hard-drive-stats-q1-2021/
    
    - Bus failure rate:
        
    - Server end failure rate:
        5% a year = 0.000136986301 / day
        https://www.statista.com/statistics/430769/annual-failure-rates-of-servers/

Recovery Rates are based off the following sources/assumptions: 


TO DO:
   - Make probabilities realistic
   - Add cold or warm sparing

'''

import numpy as np
#import pandas as pd
#import openpyxl
from datetime import datetime
from mcFunctions import * # See mcFunctions.py for specific functions definitions
    # from math import exp
    # import os
    # import random

# ADJUST SIMULATION PARAMETERS
stories = 100 # iterations run of simulation
steps = 10**4
saveOutput = True # Saves output (ONLY DO IF STORIES IS SMALL*******)

def main():
    # Simulation variables
    total_downtime_dss = 0
    total_downtime_tmr = 0
    storage_downtime_dss = 0
    storage_downtime_tmr = 0

    # Excel data
    failures_over_story_tmr = []
    failures_over_story_dss = []
    repairs_over_story_tmr = []
    repairs_over_story_dss = []
    system_state_over_story_tmr = []
    system_state_over_story_dss = []
    storage_state_over_story_tmr = []
    storage_state_over_story_dss = []

    system_downtime_story_tmr = []
    storage_downtime_story_tmr = []
    system_downtime_story_dss = []
    storage_downtime_story_dss = []

    prog = 0 # Timekeep variable for progress bar

    # Component Mapping
    # 1st index: 1=UP, 2=DOWN
    # 2nd index: Steps in UP or DOWN state
    # 3rd index: fail rate (only for storage)
    tmr_states = {
        "server1": [1,0,0.00001],
        "voter1": [1,0,0.00001],
        "bus1": [1,0,0.00001],
        "storage1": [1,0,0],
        "storage2": [1,0,0],
        "storage3": [1,0,0]
    }

    tmr_components = ["server1","voter1","bus1","storage1","storage2","storage3"]

    dss_states = {
        "server1": [1,0,0.00001],
        "bus1": [1,0,0.00001],
        "storage1": [1,0,0],
        "spare1": [1,0,0]
    }

    dss_components = ["server1","bus1","storage1","spare1"]

    recordStory = True # Flag for recording one story sample
    random.seed(0)
    # Begin simulation
    for iteration in range(stories):
        prog = show_progress(iteration, stories, prog)

        # Reset temp variables
        fails_tmr = 0
        fails_dss = 0
        repairs_tmr= 0
        repairs_dss = 0
        sys_state_tmr = 0
        sys_state_dss = 0
        storage_state_tmr = 0
        storage_state_dss = 0

        story_system_fails_tmr = 0
        story_storage_fails_tmr = 0
        story_system_fails_dss = 0
        story_storage_fails_dss = 0
        
        # Reset state maps and steps
        for component in tmr_components:
            tmr_states[component][0] = 1 # Set to UP state

        for component in dss_components:
            dss_states[component][0] = 1 # Set to UP state


        # Run Simulation
        for step in range(steps):
            # reset state variables
            sys_state_tmr = 1
            sys_state_dss = 1
            storage_state_tmr = 1
            storage_state_dss = 1

            #print("FAILS: ",failures_over_story_tmr)
            #print("REPAIRS: ",repairs_over_story_tmr)
            # Determine if component will fail
            for component in tmr_components:
                if (component == "storage1" or component == "storage2" or component == "storage3" or component == "spare1") and (tmr_states[component][2] == 0):
                    comp_fail_rate = random.gauss(0.000178082192, 0.00025)
                    while(comp_fail_rate <= 0):
                        comp_fail_rate = random.gauss(0.000178082192, 0.00025)
                    tmr_states[component][2] = comp_fail_rate


                if (tmr_states[component][0] == 1) and check_failure(component, tmr_states[component][1], tmr_states[component][2]):
                    # Update state mapping
                    #print("FAILURE: ", component)
                    tmr_states[component][0] = 0
                    tmr_states[component][1] = 0
                    if recordStory:
                        fails_tmr += 1

            for component in dss_components:
                if (component == "storage1" or component == "storage2" or component == "storage3" or component == "spare1") and (dss_states[component][2] == 0):
                    comp_fail_rate = random.gauss(0.000178082192, 0.00025)
                    while(comp_fail_rate <= 0):
                        comp_fail_rate = random.gauss(0.000178082192, 0.00025)
                    dss_states[component][2] = comp_fail_rate
                
                if (dss_states[component][0] == 1) and check_failure(component, dss_states[component][1], dss_states[component][2]):
                    # Update state mapping
                    dss_states[component][0] = 0
                    dss_states[component][1] = 0
                    if recordStory:
                        fails_dss += 1

            # Determine if component will repair
            for component in tmr_components:
                if (tmr_states[component][0] == 0) and (check_repair(component, tmr_states[component][1])):
                    # Update state mapping
                    #print("REPAIR: ", component)
                    tmr_states[component][0] = 1
                    tmr_states[component][1] = 0
                    if (component == "storage1" or component == "storage2" or component == "storage3" or component == "spare1"):
                        tmr_states[component][2] = 0
                    if recordStory:
                        repairs_tmr += 1
                    
            for component in dss_components:
                if (dss_states[component][0] == 0) and check_repair(component, dss_states[component][1]):
                    # Update state mapping
                    dss_states[component][0] = 1
                    dss_states[component][1] = 0
                    if (component == "storage1" or component == "storage2" or component == "storage3" or component == "spare1"):
                        dss_states[component][2] = 0
                    if recordStory:
                        repairs_dss += 1

            # Check uptime of storage, and overall system
            # Check TMR
            if (check_storage_availability(tmr_states,"tmr")) == False:
                storage_downtime_tmr += 1
                story_storage_fails_tmr += 1
                storage_state_tmr = 0

            if (check_system_availability(tmr_states,"tmr")) == False:
                total_downtime_tmr += 1
                story_system_fails_tmr += 1
                sys_state_tmr = 0

            # Check DSS
            if (check_storage_availability(dss_states,"dss")) == False:
                storage_downtime_dss += 1
                story_storage_fails_dss += 1
                storage_state_dss = 0

            if (check_system_availability(dss_states,"dss")) == False:
                total_downtime_dss += 1
                story_system_fails_tmr += 1
                sys_state_dss = 0

            # Increment time for each component
            for component in tmr_components:
                tmr_states[component][1] += 1
            for component in dss_components:
                dss_states[component][1] += 1

            # Append story data to lists for time keeping
            failures_over_story_tmr.append(fails_tmr)
            failures_over_story_dss.append(fails_dss)
            repairs_over_story_tmr.append(repairs_tmr)
            repairs_over_story_dss.append(repairs_dss)
            system_state_over_story_tmr.append(sys_state_tmr)
            system_state_over_story_dss.append(sys_state_dss)
            storage_state_over_story_tmr.append(storage_state_tmr)
            storage_state_over_story_dss.append(storage_state_dss)

        # Save data
        if recordStory:
            with open('storySample.txt', 'w') as f:
                f.write("FAILS_OVER_STORY_TMR\n")
                f.writelines(str(failures_over_story_tmr))
                f.write("\n\n FAILS_OVER_STORY_DSS\n")
                f.writelines(str(failures_over_story_dss))
                f.write("\n\n REPAIRS_OVER_STORY_TMR\n")
                f.writelines(str(repairs_over_story_tmr))
                f.write("\n\n REPAIRS_OVER_STORY_DSS\n")
                f.writelines(str(repairs_over_story_dss))
                f.write("\n\n SYS_STATE_TMR\n")
                f.writelines(str(system_state_over_story_tmr))
                f.write("\n\n SYS_STATE_DSS\n")
                f.writelines(str(system_state_over_story_dss))
                f.write("\n\n STOR_STATE_TMR\n")
                f.writelines(str(storage_state_over_story_tmr))
                f.write("\n\n STOR_STATE_DSS\n")
                f.writelines(str(storage_state_over_story_dss))

            recordStory = False # Only record one sample

        system_downtime_story_dss.append(story_system_fails_dss)
        system_downtime_story_tmr.append(story_system_fails_tmr)
        storage_downtime_story_dss.append(story_storage_fails_dss)
        storage_downtime_story_tmr.append(story_storage_fails_tmr)
    # End for loops

    # Calculate statistics and save to output.txt
    with open('results.txt', 'w') as f:
        f.write("Results from Simulation " + str(datetime.now()))
        f.write("\n"+'-'*20)
        f.write("\nDynamic Sparing System Statistics: ")
        f.write("\n\tOverall System Downtime: " + str(total_downtime_dss) + "/" + str(stories*steps) + " = " + str(total_downtime_dss/(stories*steps)))
        f.write("\n\tOverall Storage Downtime: "+ str(storage_downtime_dss) + "/" + str(stories*steps) + " = " + str(storage_downtime_dss/(stories*steps)))
        f.write("\n\tAverage System Downtime Per Story: "+ str(total_downtime_dss/stories) + "/" + str(steps) + " = " + str((total_downtime_dss/stories)/steps))
        f.write("\n\tAverage Storage Downtime Per Story: "+ str(storage_downtime_dss/stories) + "/" + str(steps) + " = " + str((storage_downtime_dss/stories)/steps))
        f.write("\n"+'-'*20)
        f.write("\nTriple Modular Redundancy Statistics: ")
        f.write("\n\tOverall System Downtime: "+ str(total_downtime_tmr) + "/" + str(stories*steps) + " = " + str(total_downtime_tmr/(stories*steps)))
        f.write("\n\tOverall Storage Downtime: "+ str(storage_downtime_tmr) + "/"+ str(stories*steps) + " = " + str(storage_downtime_tmr/(stories*steps)))
        f.write("\n\tAverage System Downtime Per Story: "+ str(total_downtime_tmr/stories) + "/" + str(steps) + " = " + str((total_downtime_tmr/stories)/steps))
        f.write("\n\tAverage Storage Downtime Per Story: "+ str(storage_downtime_tmr/stories) + "/"+ str(steps) + " = " + str((storage_downtime_tmr/stories)/steps))

    print("Program has finished. Check results.txt for statistics.")


if __name__ == '__main__':
  main()