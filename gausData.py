import random
import os

data = []
tmp = 0
for i in range(100000):
    tmp = random.gauss(0.00178082192, 0.00025)
    tmp = int(tmp * 10**4) / 10**4
    data.append(tmp)

str_data = str(data)
str_data = str_data.replace('[','')
str_data = str_data.replace(']','')
str_data = str_data.replace(',','\n')
str_data = str_data.replace(' ','')

with open('gausData.txt','w') as f:
    f.write(str_data)