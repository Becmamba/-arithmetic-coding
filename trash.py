import math
import os
from fnmatch import fnmatch
from datetime import datetime
from tqdm import tqdm

def fileload(filename):
    file_pth = os.path.dirname(__file__) + '/' + filename
    file_in = os.open(file_pth, os.O_BINARY | os.O_RDONLY)
    file_size = os.stat(file_in)[6]
    data = os.read(file_in, file_size)
    os.close(file_in)
    return data

def cal_pr(data):
    pro_dic = {}
    for i in tqdm(data):
        pro_dic[i] = data.count(i)
    sym_pro = []
    accum_pro = []
    keys = []
    accum_p = 0
    data_size = len(data)
    for k in sorted(pro_dic, key=pro_dic.__getitem__, reverse=True):
        sym_pro.append(pro_dic[k])
        keys.append(k)
    for i in sym_pro:
        accum_pro.append(accum_p)
        accum_p += i
    accum_pro.append(data_size)
    tmp = 0
    for k in sorted(pro_dic, key=pro_dic.__getitem__, reverse=True):
        pro_dic[k] = [pro_dic[k], accum_pro[tmp]]
        tmp += 1
    return pro_dic, keys, accum_pro        

def encode(data, pro_dic):
    t_begin = datetime.now()
    print("Encoding begins.")
    print("Please wait...")
    C_up = 0
    A_up = A_down = C_down = 1
    data_size = len(data)
    for i in tqdm(range(data_size)):  
        C_up = C_up * data_size + A_up * pro_dic[data[i]][1]
        C_down = C_down * data_size
        A_up *= pro_dic[data[i]][0]
        A_down *= data_size
    L = len(data) * math.log2(data_size) - math.log2(A_up)
    L = math.ceil(L)
    print("Generating codes...")
    bin_C = dec2bin(C_up, C_down, L)
    acode = bin_C[0:L]
    t_end = datetime.now()
    print("Encoding succeeded.")
    print("Encoding lasts %d seconds." % (t_end - t_begin).seconds)
    return C_up, C_down, acode

def decode(C_up, C_down, pro_dic, keys, accum_pro, data_size):
    t_begin = datetime.now()
    print("Decoding begins.")
    print("Please wait...")
    byte_list = []
    for i in tqdm(range(data_size)):
        k = binarysearch(accum_pro, C_up * data_size / C_down)
        if k == len(accum_pro) - 1:
            k -= 1
        key = keys[k]
        byte_list.append(key)
        C_up = C_up * data_size - C_down * pro_dic[key][1]
        C_down = C_down * data_size
        C_up *= data_size
        C_down *= pro_dic[key][0]
    t_end = datetime.now()
    print("Decoding succeeded.")
    print("Decoding lasts %d seconds." % (t_end - t_begin).seconds)
    return byte_list

def binarysearch(pro_list, target):
    low = 0
    high = len(pro_list) - 1
    if pro_list[0] <= target <= pro_list[-1]:
        while high >= low:
            middle = int((high + low) / 2)
            if (pro_list[middle] < target) & (pro_list[middle+1] < target):
                low = middle + 1
            elif (pro_list[middle] > target) & (pro_list[middle-1] > target):
                high = middle - 1
            elif (pro_list[middle] < target) & (pro_list[middle+1] > target):
                return middle
            elif (pro_list[middle] > target) & (pro_list[middle-1] < target):
                return middle - 1
            elif (pro_list[middle] < target) & (pro_list[middle+1] == target):
                return middle + 1
            elif (pro_list[middle] > target) & (pro_list[middle-1] == target):
                return middle - 1
            elif pro_list[middle] == target:
                return middle
        return middle
    else:
        return False

def int_bin2dec(bins):
    dec = 0
    for i in range(len(bins)):
        dec += int(bins[i]) * 2 ** (len(bins) - i -1)
    return dec
    
def dec2bin(x_up, x_down, L):
    bins = ""
    while ((x_up != x_down) & (len(bins) < L)):
        x_up *= 2
        if x_up > x_down:
            bins += "1"
            x_up -= x_down
        elif x_up < x_down:
            bins += "0"
        else:
            bins += "1"
    return bins

def filesave(data_after, filename):
    file_pth = os.path.dirname(__file__) + '/' + filename
    if (fnmatch(filename, "*_encode.*") == True):
        byte_list = []
        byte_num = math.ceil(len(data_after) / 8)
        for i in range(byte_num):
            byte_list.append(int_bin2dec(data_after[8*i:8*(i+1)]))
        file_open = os.open(file_pth, os.O_WRONLY | os.O_CREAT | os.O_BINARY)
        os.write(file_open, bytes(byte_list))
        os.close(file_open)
        return byte_num
    else:
        file_open = os.open(file_pth, os.O_WRONLY | os.O_CREAT | os.O_BINARY)
        os.write(file_open, data_after)
        os.close(file_open)

def code_efficiency(pro_dic, data_size, bit_num):
    entropy = 0
    for k in pro_dic.keys():
        entropy += (pro_dic[k][0] / data_size) * (math.log2(data_size) - math.log2(pro_dic[k][0]))
    #print(entropy)
    ave_length = bit_num / data_size
    #print(ave_length)
    code_efficiency = entropy / ave_length
    print("The code efficiency is %.2f%%" % (code_efficiency * 100))

def acode():
    filename = ["诺贝尔化学奖", "脑机接口新突破"]
    filetype = [".txt", ".docx"]
    for i in range(len(filename)):
        print(40 * "-")
        print("Loading file:", filename[i] + filetype[i])
        data = fileload(filename[i] + filetype[i])
        data_size = len(data)
        pro_dic, keys, accum_pro = cal_pr(data)
        acode_ls = ""
        C_up, C_down, acode = encode(data, pro_dic)
        acode_ls += acode
        codebyte_num = filesave(acode_ls, filename[i]+'_encode.acode')
        print("Encoding file has been saved.")
        print("The compressing rate is %.2f%%" % ((codebyte_num / data_size) * 100))
        code_efficiency(pro_dic, data_size, len(acode_ls))
        print()

        decodebyte_ls = decode(C_up, C_down, pro_dic, keys, accum_pro, data_size)
        errornum = 0
        for j in range(data_size):
            if data[j] != decodebyte_ls[j]:
                errornum += 1
        print("Error byte num:", errornum)
        filesave(bytes(decodebyte_ls), filename[i] + '_decode'+  filetype[i])
        print("Decoding file has been saved.")

if __name__ == "__main__":
    acode()