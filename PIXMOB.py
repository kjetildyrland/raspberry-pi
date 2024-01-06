import json
import os

# Assuming the script is run from the project root
FilesPath = './rf/edited_rf_captures/868Mhz/'

for filename in os.listdir(FilesPath):
    if '.sub' in filename:
        with open(os.path.join(FilesPath, filename), 'r') as file:
            l = [int(int(x)/510) for x in file.read().split('RAW_Data: ')[1].split(' ')]
        s = ''
        for i in l:
            if i > 0:
                for d in range(i):
                    s += '1'
            else:
                for d in range(-1*i):
                    s += '0'
        s=s+'00000000'
        Hex = ''
        for i in range(0, len(s), 8):
            Hex = Hex + hex(int(s[i:i+8], 2)) + ','
        print(('// {' + Hex[:-1] + '}, //' + filename.replace('.sub', '')).replace(',0x0}','}'))