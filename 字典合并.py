import os
'''
将目录下一个文件夹里的所有字典合并成一个大的字典
然后放到与文件夹同名的文件中
特点：所有文件删重（内容相同的行）、删空格、排序
支持txt/dic，大文件比较慢
'''
name=input("输入文件夹名:")
a=[]
for i in os.listdir(name):
    with open(name+"\\"+i,"rb") as f:
        a+=f.read().split(b"\r\n")
with open(name+".txt","wb") as f:
    f.write(b'\n'.join(sorted(list(set(a)-set(" ")))))    

