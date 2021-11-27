from math import exp
import os
import random


def show_progress(timestep, total, prev_prog):
    cur_prog = 0
    cur_prog = int((timestep / total) * 100)
    if prev_prog != cur_prog:
        os.system("clear")
        print("Current progress: " + str(cur_prog) + "%")

    return cur_prog 
    
def check_failure(component, time, fail_rate):
    '''
        TRUE = Component failure
        FALSE = Component survives
    '''

    f_prob = 1 - exp(-1*time*fail_rate)

    # Check if it will fail
    rand_p = random.randrange(1,100000000000)
    if rand_p < int(f_prob * 100000000000):
        return True # Component failure
    
    return False


def check_repair(component, time):
    '''
        TRUE = Component repairs
        FALSE = Component remains broken
    '''
    repair_rate = 0.005

    r_prob = 1 - exp(-1*time*repair_rate)

    # Check if it will fail
    rand_p = random.randrange(1,10000000)
    if rand_p < int(r_prob * 10000000):
        return True
    
    return False    

def check_storage_availability(state_map, design_type):
    '''
        TRUE = System is available
        FALSE = System is unavailable
    '''
    if design_type == "tmr":
        if state_map.get("storage1")[0] + state_map.get("storage2")[0] + state_map.get("storage3")[0] < 2: # TMR Fails
            return False
        else:
            return True

    if design_type == "dss":
        if state_map.get("storage1")[0] + state_map.get("spare1")[0] < 1:
            return False
        else:
            return True

    return False

def check_system_availability(state_map, design_type):
    '''
        TRUE = System is available
        FALSE = System is unavailable
    '''

    # Will determine if the server is in a usable condition
    if design_type == "tmr":
        if check_storage_availability(state_map, design_type) == False:
            return False
        elif state_map.get("voter1")[0] + state_map.get("bus1")[0] + state_map.get("server1")[0] != 3: # Other critical components fail
            return False  
        else: # System is up
            return True

    if design_type == "dss":
        if check_storage_availability(state_map, "dss") == False:
            return False
        elif state_map.get("bus1")[0] + state_map.get("server1")[0] != 2: # Other critical components fail
            return False
        else:
            return True

    return False # Failsafe condition
