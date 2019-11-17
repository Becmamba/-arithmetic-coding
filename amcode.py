#算术编码

import math
import os
from fnmatch import fnmatch
from datetime import datetime

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
    data_set = set(data)
    for i in data_set:
        pro_dic[i] = data.count(i) #统计频数
    sym_pro = [] #频数列表
    accum_pro = [] #累积频数列表
    keys = [] #字节名列表
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
def encode(data, pro_dic, data_size):
    C_up = 0
    A_up = A_down = C_down = 1
    for i in range(len(data)):  
        C_up = C_up * data_size + A_up * pro_dic[data[i]][1]
        C_down = C_down * data_size
        A_up *= pro_dic[data[i]][0]
        A_down *= data_size
    L = math.ceil(len(data) * math.log2(data_size) - math.log2(A_up)) #计算编码长度
    bin_C = dec2bin(C_up, C_down, L)
    amcode = bin_C[0:L] #生成编码
    return C_up, C_down, amcode

#译码
def decode(C_up, C_down, pro_dic, keys, accum_pro, byte_num, data_size):
    byte_list = []
    for i in range(byte_num):
        k = binarysearch(accum_pro, C_up * data_size / C_down) #二分法搜索编码所在频数区间
        if k == len(accum_pro) - 1:
            k -= 1
        key = keys[k]
        byte_list.append(key)
        C_up = (C_up * data_size - C_down * pro_dic[key][1]) * data_size
        C_down = C_down * data_size * pro_dic[key][0]
    return byte_list #返回译码字节列表

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
    #保存译码文件
    if (fnmatch(filename, "*_am.*") == True):
        file_open = os.open(file_pth, os.O_WRONLY | os.O_CREAT | os.O_BINARY)
        os.write(file_open, data_after)
        os.close(file_open)
    #保存编码文件
    else:
        byte_list = []
        byte_num = math.ceil(len(data_after) / 8)
        for i in range(byte_num):
            byte_list.append(int_bin2dec(data_after[8*i:8*(i+1)]))
        file_open = os.open(file_pth, os.O_WRONLY | os.O_CREAT | os.O_BINARY)
        os.write(file_open, bytes(byte_list))
        os.close(file_open)
        return byte_num #返回字节数

#计算编码效率
def code_efficiency(pro_dic, data_size, bit_num):
    entropy = 0
    #计算熵
    for k in pro_dic.keys():
        entropy += (pro_dic[k][0] / data_size) * (math.log2(data_size) - math.log2(pro_dic[k][0]))
    #计算平均码长
    ave_length = bit_num / data_size
    code_efficiency = entropy / ave_length
    print("The code efficiency is %.3f%%" % (code_efficiency * 100))

#主函数
def amcode():
    filename = ["脑机接口新突破", "诺贝尔化学奖"]
    filetype = [".docx", ".txt"]
    for i in range(len(filename)):
        print(60 * "-")
        print("Loading file:", filename[i] + filetype[i])
        t_begin = datetime.now()
        #读取源文件
        data = fileload(filename[i] + filetype[i])
        data_size = len(data)
        print("Calculating probability of bytes..")
        #统计字节频数
        pro_dic, keys, accum_pro = cal_pr(data)
        amcode_ls = ""
        C_upls = []
        C_downls = []
        byte_num = 1000 #每次编码的字节数
        integra = math.ceil(data_size / byte_num) #迭代次数
        print("\nEncoding begins.")
        #编码
        for k in range(integra):
            C_up, C_down, amcode = encode(data[byte_num * k : byte_num * (k+1)], pro_dic, data_size)
            amcode_ls += amcode
            C_upls.append(C_up)
            C_downls.append(C_down)
        #保存编码文件，返回编码总字节数
        codebyte_num = filesave(amcode_ls, filename[i]+'.am')
        t_end = datetime.now()
        print("Encoding succeeded.")
        print("Saved encoding file: " + filename[i] + '.am')
        print("The compressing rate is %.3f%%" % ((data_size / codebyte_num) * 100))  #压缩比
        code_efficiency(pro_dic, data_size, len(amcode_ls))  #编码效率
        print("Encoding lasts %.3f seconds." % (t_end - t_begin).total_seconds())  #编码时间
        print("Encoding speed: %.3f Kb/s" % (data_size / ((t_end - t_begin).total_seconds() * 1024)))  #编码速率
        print()

        decodebyte_ls = []
        print("Decoding begins.")
        #译码
        t_begin = datetime.now()
        for k in range(integra):
            if (k == integra - 1) & (data_size % byte_num != 0):
                decodebyte_ls += decode(C_upls[k], C_downls[k], pro_dic, keys, accum_pro, data_size % byte_num, data_size)
            else:
                decodebyte_ls += decode(C_upls[k], C_downls[k], pro_dic, keys, accum_pro, byte_num, data_size)
        #保存译码文件
        filesave(bytes(decodebyte_ls), filename[i] + '_am'+  filetype[i])
        t_end = datetime.now()
        print("Decoding succeeded.")
        print("Saved decoding file: " + filename[i] + '_am'+  filetype[i])       
        #计算误码率
        errornum = 0
        for j in range(data_size):
            if data[j] != decodebyte_ls[j]:
                errornum += 1
        print("Error rate: %.3f%%" % (errornum / data_size * 100))  #误码率
        print("Decoding lasts %.3f seconds." % (t_end - t_begin).total_seconds())  #译码时间
        print("Decoding speed: %.3f Kb/s" % (codebyte_num / ((t_end - t_begin).total_seconds() * 1024)))  #译码速率

if __name__ == "__main__":
    amcode()