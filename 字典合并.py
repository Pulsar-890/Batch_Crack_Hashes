import os
'''
将目录下一个文件夹里（包括所有子文件夹）的所有字典合并成一个大的字典
然后放到与文件夹同名的文件中
特点：所有文件删重（内容相同的行）、删空格、排序
支持txt/dic，大文件比较慢
'''

file_type=[".txt",".dic"]
all_filetype=False

show=[["┣━","┗━"],["┃ ","  "]]
def opendirs(path,p=""): #┃┣┗━
    a=[]
    x=os.listdir(path)
    for i in x:
        if os.path.isdir(path+"\\"+i):
            print(p+show[0][i==x[-1]]+i)
            a+=opendirs(path+"\\"+i,p+show[1][i==x[-1]])
        elif (all_filetype or any(i.lower().endswith(t) for t in file_type)):
            with open(path+"\\"+i,"rb") as f:
                b=f.read().replace(b"\r",b"").split(b"\n")
                a+=b
            print(p+show[0][i==x[-1]]+i,f"\t{len(b)}")
    return a
                
#准备做嵌套合并
import traceback
try:
    name=input("输入文件夹名:")
    b=opendirs(name)
    print('读取完成，正在合并...')
    with open(name+".txt","wb") as f:
        f.write(b'\n'.join(sorted(list(set(b)-set(" ")))))    
    print('OK!')
except Exception as e:
    error_type = type(e).__name__  # 获取错误类型
    if error_type=="MemoryError":
        while 1:
            input("文件夹太大，内存空间不足！程序自动终止！")
    else:
        traceback.print_exc()  # 打印异常追踪信息
        while 1:
            input("程序出错:请将报错信息及之前运行的内容截图并联系开发者")
