#!/usr/bin/env python3

"""
UPI: sche619
Name: Shunying Chen
"""

import os
import sys
import shutil
import time
import hashlib
import json

def get_modify_time(directory,file):
    t = time.strftime("%Y-%m-%d %H:%M:%S %z", time.localtime(os.path.getmtime(os.path.join(directory, file))))
    return t

def get_digest_of_file(directory,file):
    content = open(os.path.join(directory, file)).read()
    h = hashlib.sha256(bytes(content,'utf-8')).hexdigest()
    return h

def create_sync_file(dir1,dir2):
    files1 = os.listdir(dir1)
    sync1 = open(dir1+"/.sync","w")
    j1={}
    name='.sync'
    for f1 in files1:
        if f1 != name and (not os.path.isdir(os.path.join(dir1, f1))):
            t1 = get_modify_time(dir1,f1)
            h1 = get_digest_of_file(dir1,f1)
            j1[f1]=[[t1,h1]]
    json.dump(j1,sync1,indent=4)
    sync1.close()

    files2 = os.listdir(dir2)
    sync2 = open(dir2+"/.sync","w")
    j2={}
    for f2 in files2:
        if f2 != name and (not os.path.isdir(os.path.join(dir2, f2))):
            t2 = get_modify_time(dir2,f2)
            h2 = get_digest_of_file(dir2,f2)
            j2[f2]=[[t2,h2]]
    json.dump(j2,sync2,indent=4)
    sync2.close()

def update(directory):
    files = os.listdir(directory)
    s = open(directory+"/.sync",'r').read()
    data_dict = json.loads(s)
    name='.sync'
    for f in files:
        if f != name and (not os.path.isdir(os.path.join(directory, f))) :
            d = get_digest_of_file(directory,f)
            t_new = get_modify_time(directory,f) 
            for i in range(len(data_dict[f])):
                if d in data_dict[f][i]:
                    exist = True
                    t_sync = data_dict[f][i][0]
                    if t_sync != t_new:
                        t_sync = t_new
                        old = data_dict[f]
                        data_dict[f] = [[t_new,d]]+old
                    break
                else:
                    exist = False
            if not exist:
                old = data_dict[f]
                data_dict[f] = [[t_new,d]]+old

    sync = open(directory+"/.sync","w")
    json.dump(data_dict,sync,indent=4)
    sync.close()

def sync(dir1,dir2):
    files1 = os.listdir(dir1)
    files2 = os.listdir(dir2)
    
    for f2 in files2:
        if f2 not in files1 and (not os.path.isdir(os.path.join(dir2, f2))):
            shutil.copy("{}/{}".format(dir2,f2),dir1)
    for f1 in files1:
        if f1 not in files2 and (not os.path.isdir(os.path.join(dir1, f1))):
            shutil.copy("{}/{}".format(dir1,f1),dir2)

def check_overlap(dir1,dir2):
    files1 = os.listdir(dir1)
    files2 = os.listdir(dir2)
    name='.sync'
    
    s1 = open(dir1+"/.sync",'r').read()
    data1 = json.loads(s1)
    s2 = open(dir2+"/.sync",'r').read()
    data2 = json.loads(s2)
        
    for f in files1:
        if f in files2 and f != name and (not os.path.isdir(os.path.join(dir1, f))):
            h1 = get_digest_of_file(dir1,f)
            h2 = get_digest_of_file(dir2,f)
            t1 = get_modify_time(dir1,f)
            t2 = get_modify_time(dir2,f)
            if h1 != h2:
                if t1 > t2:
                    os.remove("{}/{}".format(dir2,f))
                    shutil.copy("{}/{}".format(dir1,f),dir2)
                    print(1)
                else:
                    os.remove("{}/{}".format(dir1,f))
                    shutil.copy("{}/{}".format(dir2,f),dir1)

            else:
                if t1 > t2:
                    data1[f].insert(0,[t2])
                    data1[f][0].append(h1)
                else:
                    data2[f].insert(0,[t1])
                    data2[f][0].append(h2)
                    
    sync1 = open(dir1+"/.sync","w")
    json.dump(data1,sync1,indent=4)
    sync1.close()
    
    sync2 = open(dir2+"/.sync","w")
    json.dump(data2,sync2,indent=4)
    sync2.close()

def check_deletion(dir1,dir2):
    s1 = open(dir1+"/.sync",'r').read()
    data1 = json.loads(s1)
    s2 = open(dir2+"/.sync",'r').read()
    data2 = json.loads(s2)
    
    files1 = os.listdir(dir1)
    files2 = os.listdir(dir2)
            
    for f1 in data1:
        #if (not os.path.isdir(os.path.join(dir1, f1))):
            for i in range(len(data1[f1])):
                if "deleted" in data1[f1][i]:
                    if f1 in files2:
                        sync(dir1,dir2)
                            
            if f1 not in files1:
                data1[f1].insert(0,[time.strftime("%c"),"deleted"])
                if f1 in files2:
                    os.remove("{}/{}".format(dir2,f1))

    for f2 in data2:
        #if (not os.path.isdir(os.path.join(dir2, f2))):
            for j in range(len(data2[f2])):
                if "deleted" in data2[f2][j]:
                    if f2 in files1:
                        sync(dir1,dir2)
                        
            if f2 not in files2:
                data2[f2].insert(0,[time.strftime("%c"),"deleted"])
                if f2 in files1:
                    os.remove("{}/{}".format(dir1,f2))

    sync1 = open(dir1+"/.sync","w")
    json.dump(data1,sync1,indent=4)
    sync1.close()
    
    sync2 = open(dir2+"/.sync","w")
    json.dump(data2,sync2,indent=4)
    sync2.close()

def subdir(dir1,dir2):
    a = [x[0] for x in os.walk(dir1)]
    b = [x[0] for x in os.walk(dir2)]

    for dirpath in a:
        if dirpath != dir1:
            path = dir2 + dirpath[len(dir1):]
            if path not in b:
                os.mkdir(path)
            do(dirpath,path)
                
    for dirpath in b:
        if dirpath != dir2:
            path = dir1 + dirpath[len(dir2):]
            if path not in a:
                os.mkdir(path)
            do(dirpath,path)

def do(dir1,dir2):
    files1 = os.listdir(dir1)
    files2 = os.listdir(dir2)
    name='.sync'

    if (name not in files1) or (name not in files2):
        sync(dir1,dir2)
        create_sync_file(dir1,dir2)
        check_overlap(dir1,dir2)
        update(dir1)
        update(dir2)

    else:
        check_deletion(dir1,dir2)
        
        sync(dir1,dir2)
        
        check_overlap(dir1,dir2)         
        
        update(dir1)
        update(dir2)

def main():
    dir1 = sys.argv[1]
    dir2 = sys.argv[2]

    if ((not os.path.isdir(dir1)) and (not os.path.isdir(dir2))):
        print("Usage: sync directory1 directory2")
    else:
        if (not os.path.exists(dir2)):
            shutil.copytree(dir1,dir2)     
        elif (not os.path.exists(dir1)):
            shutil.copytree(dir2,dir1)

        do(dir1,dir2)

        a = [x[0] for x in os.walk(dir1)]
        b = [x[0] for x in os.walk(dir2)]
        if len(a) > 1 or len(b) > 1 :
           subdir(dir1,dir2)
           do(dir1,dir2)
 
main()
