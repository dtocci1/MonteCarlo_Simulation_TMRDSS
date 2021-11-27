import os
def main(fileName):
    data = ""
    with open(fileName,'r') as f:
        data = f.read()

    #print(data)
    data= data.replace(',', '\n')
    #print(data)

    with open(fileName,'w') as f:
        f.write(data)

if __name__ == '__main__':
  main("sys_state_tmr.csv")