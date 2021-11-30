# Chicken scratch code to get stats about up/down time

def main():
    with open('data/sys_state_tmr.csv','r') as f:
        data = f.readlines()
        new_data=[]
        for ind in data:
            new_data.append(int(ind.replace('\n','')))

    d_count = 0
    u_count = 0
    downtime = []
    uptime = []
    for i in range(len(new_data)):
        if new_data[i] == 0:
            uptime.append(u_count)
            u_count = 0
            d_count += 1

        elif new_data[i] == 1:
            downtime.append(d_count)
            d_count = 0
            u_count += 1
    
    uptime.append(u_count)
    downtime.append(d_count)

    new_downtime = []
    new_uptime = []

    for i in range(len(downtime)):
        if downtime[i] != 0:
            new_downtime.append(downtime[i])

    for i in range(len(uptime)):
        if uptime[i] != 0:
            new_uptime.append(uptime[i])

    print(new_uptime)
    print(new_downtime)

    print("UPTIME: ", int(sum(new_uptime)/len(new_uptime)))
    print("DOWNTIME: ", int(sum(new_downtime)/len(new_downtime)))

if __name__ == '__main__':
    main()