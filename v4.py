import math
import os
from fnmatch import fnmatch
from datetime import datetime
from tqdm import tqdm

#以二进制的方式读取文件，结果为字节
def fileload(filename):
    file_pth = os.path.dirname(__file__) + '/' + filename
    file_in = os.open(file_pth, os.O_BINARY | os.O_RDONLY)
    file_size = os.stat(file_in)[6]
    data = os.read(file_in, file_size)
    os.close(file_in)
    return data

#计算文件中不同字节的频数和累积频数
def cal_pr(data):
    pro_dic = {}
    for i in data:
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

#编码
def encode(data, pro_dic):
    C_up = 0
    A_up = A_down = C_down = 1
    #data_size = len(data)
    for i in range(len(data)):  
        C_up = C_up * data_size + A_up * pro_dic[data[i]][1]
        C_down = C_down * data_size
        A_up *= pro_dic[data[i]][0]
        A_down *= data_size
    L = len(data) * math.log2(data_size) - math.log2(A_up)
    L = math.ceil(L)
    #print(L)
    #print("Generating codes...")
    bin_C = dec2bin(C_up, C_down, L)
    acode = bin_C[0:L]
    '''
    if acode[-1] == "0":
        acode = acode.replace(acode[-1], "1") 
    else:
        acode = acode.replace(acode[-1], "0") 
    '''
    #print("Encoding succeeded.")
    #print("Encoding lasts %d seconds." % (t_end - t_begin).seconds)
    return acode

#译码
def decode(C_up, C_down, pro_dic, keys, accum_pro, byte_num):
    #print("Decoding begins.")
    #print("Please wait...")
    byte_list = []
    for i in range(byte_num):
        k = binarysearch(accum_pro, C_up * data_size / C_down)
        if k == len(accum_pro) - 1:
            k -= 1
        key = keys[k]
        print(C_up, C_down, C_up * data_size / C_down, key)
        byte_list.append(key)
        C_up = C_up * data_size - C_down * pro_dic[key][1]
        C_down = C_down * data_size
        C_up *= data_size
        C_down *= pro_dic[key][0]
    #print("Decoding succeeded.")
    #print("Decoding lasts %d seconds." % (t_end - t_begin).seconds)
    return byte_list

#二分法搜索
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

#整数二进制转十进制
def int_bin2dec(bins):
    dec = 0
    for i in range(len(bins)):
        dec += int(bins[i]) * 2 ** (len(bins) - i -1)
    return dec

#小数二进制转十进制
def float_bin2dec(bins):
    dec_up = 0
    for i in range(len(bins)):
        dec_up += int(bins[i]) * 2 ** (len(bins) - i - 1) 
    dec_down = 2 ** len(bins)
    return dec_up, dec_down

#小数十进制转二进制
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

#保存文件
def filesave(data_after, filename):
    file_pth = os.path.dirname(__file__) + '/' + filename
    #保存编码文件
    if (fnmatch(filename, "*_encode.*") == True):
        byte_list = []
        byte_num = int(len(data_after) / 8)
        #print(byte_num)
        for i in range(byte_num):
            byte_list.append(int_bin2dec(data_after[8*i:8*(i+1)]))
        file_open = os.open(file_pth, os.O_WRONLY | os.O_CREAT | os.O_BINARY)
        os.write(file_open, bytes(byte_list))
        os.close(file_open)
        #return byte_num
    #保存译码文件
    else:
        file_open = os.open(file_pth, os.O_WRONLY | os.O_CREAT | os.O_BINARY)
        os.write(file_open, data_after)
        os.close(file_open)

#计算编码效率
def code_efficiency(pro_dic, data_size, bit_num):
    entropy = 0
    for k in pro_dic.keys():
        entropy += (pro_dic[k][0] / data_size) * (math.log2(data_size) - math.log2(pro_dic[k][0]))
    #print(entropy)
    ave_length = bit_num / data_size
    #print(ave_length)
    code_efficiency = entropy / ave_length
    print("The coding efficiency is %.2f%%" % (code_efficiency * 100))

#主函数
def acode():
    filename = ["诺贝尔化学奖", "脑机接口新突破", "README"]
    filetype = [".txt", ".docx", ".md"]
    for i in range(2, len(filename)):
        print(40 * "-")
        print("Loading file:", filename[i] + filetype[i])
        t_begin = datetime.now()
        data = fileload(filename[i] + filetype[i])
        global data_size
        data_size = len(data)
        print(data_size)
        pro_dic, keys, accum_pro = cal_pr(data)
        for j in sorted(pro_dic, key=pro_dic.__getitem__, reverse=True):
            print(j, pro_dic[j])
        #print(pro_dic)
        byte_num = 5
        acode_ls = ""
        #C_upls = C_downls = []
        integra = math.ceil(data_size / byte_num)
        print(integra)
        decodebyte_ls = []
        codebyte_num = []
        print("Encoding begins.")
        print("Please wait...")
        for k in range(integra):
            acode = encode(data[byte_num * k : byte_num * (k+1)], pro_dic)
            if len(acode) % 8 != 0:
                #print(len(acode_ls) % 8)
                tmp = acode[-(len(acode) % 8):].zfill(8)
                acode = acode[0:-(len(acode) % 8)]
                acode += tmp
                #print(k)
            codebyte_num.append(int(len(acode) / 8))
            acode_ls += acode
        #codebyte_num.insert(0, 0)
        print(len(codebyte_num))
        print(codebyte_num)
        print(sum(codebyte_num))
        filesave(acode_ls, filename[i]+'_encode.acode')
        #print(len(C_downls))
        #print(C_upls)
        #print(C_downls)
        #codebyte_num = filesave(acode_ls, filename[i]+'_encode.acode')
        print("Encoding succeeded. Encoding file has been saved.")
        print("The compressing rate is %.2f%%" % ((sum(codebyte_num) / data_size) * 100))
        code_efficiency(pro_dic, data_size, len(acode_ls))
        t_end = datetime.now()
        print("Encoding lasts %d seconds." % (t_end - t_begin).seconds)
        print()

        print("Loading file:", filename[i] + '_encode.acode')
        t_begin = datetime.now()
        codes = fileload(filename[i]+'_encode.acode')
        print(len(codes))
        #print(len(codes))
        print("Decoding begins.")
        print("Please wait...")
        for m in range(len(codebyte_num)):
            bitstream = ""
            for code in codes[sum(codebyte_num[:m]): sum(codebyte_num[:m+1])]:
                bitstream += bin(code)[2:].zfill(8)
        #print(new_dic)
        #print(len(bitstream))
            C_up, C_down = float_bin2dec(bitstream)
            if (m == integra - 1) & (data_size % byte_num != 0):
                decodebyte_ls += decode(C_up, C_down, pro_dic, keys, accum_pro, data_size % byte_num)
            else:
                decodebyte_ls += decode(C_up, C_down, pro_dic, keys, accum_pro, byte_num)
        print(len(decodebyte_ls))
        filesave(bytes(decodebyte_ls), filename[i] + '_decode'+  filetype[i])
        print("Decoding succeeded. Decoding file has been saved.")
        errornum = 0
        for j in range(data_size):
            if data[j] != decodebyte_ls[j]:
                errornum += 1
            print(j, data[j], decodebyte_ls[j], pro_dic[data[j]], pro_dic[decodebyte_ls[j]])
        #print(len(decodebyte_ls))
        print("Error rate: %.2f%%" % (errornum / data_size * 100))
        t_end = datetime.now()
        print("Decoding lasts %d seconds." % (t_end - t_begin).seconds)

if __name__ == "__main__":
    acode()