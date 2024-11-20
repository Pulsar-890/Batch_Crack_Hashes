import hashlib
from hashlib import md5,sha256,sha3_256,sha1,sha512
import base64
from time import time,sleep
import datetime
import random
import threading
from tqdm import tqdm, trange
import os
import traceback
import itertools
import re

flows=15000000    #读取明文字典时一次加载的条数

m5 = lambda b:md5(b).hexdigest()
b64 = lambda b:base64.b64encode(b)
s1 = lambda b:sha1(b).hexdigest()
s256 = lambda b:sha256(b).hexdigest()
s3_256 = lambda b:sha3_256(b).hexdigest()
s512 = lambda b:sha512(b).hexdigest()
ntlm = lambda b:hashlib.new('md4', b.encode('utf-16le')).hexdigest() #不能先encode

#13种加密方式
encode_lis=["md5","sha1","sha256","sha3-256",'sha512',"md5_md5","md5_md5_md5","md5_sha1","sha1_md5","md5_b64","md5_sha256","md5-16","ntlm"]

def hash_list(b):
    m=m5(b)
    s=s1(b)
    m2=m5(m.encode())
    s2=s256(b)
    lis=[m,s,s2,s3_256(b),s512(b),m2,m5(m2.encode()),m5(s.encode()),s1(m.encode()),m5(b64(b)),m5(s2.encode()),m[8:24]]
    try:
        n=ntlm(b.decode('utf-8'))
        return lis+[n]
    except:return lis

#哈希存储方式：hash\hash[1]\hash[2]\hash[3]\hash[4].txt
#明文存储方式：dict\md5[1]\md5[2]\md5[3]\md5[4].txt
#明文字典第一行为空行
#哈希坐标：bytes.fromhex(hash[5:8]+md5[0:4])

#日志记录函数
def report(message="",silent=False):            #标准版 #silent：是否在print的时候不加日期
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(report_message:=["["+timestamp+"] ",""][silent]+message)  # 添加时间信息并打印报告
    open("log.txt", 'a').write(report_message + "\n")

#统计字典长度/导出字典函数
def dict_output(only_length=True):
    if "dict" not in os.listdir():return 0
    a=0
    for i,j,k,l in tqdm(itertools.product("0123456789abcdef","0123456789abcdef","0123456789abcdef","0123456789abcdef"),["导出字典","统计长度"][only_length],65536):
        x=open(f"dict\\{i}\\{j}\\{k}\\{l}.txt","rb").read()
        if not only_length:open("out.txt","ab").write(x)
        a+=len(x.splitlines()[1:])  #第一行为空行
    return a

#哈希去重函数
def balance():
    cleans=0
    for i,j,k,l in tqdm(itertools.product("0123456789abcdef","0123456789abcdef","0123456789abcdef","0123456789abcdef"),"哈希去重",65536):
        x=open(f"hash\\{i}\\{j}\\{k}\\{l}.txt","rb").read()
        cleans+=len(x)//4
        x=b''.join(set(x[i:i+4] for i in range(0,len(x),4)))
        cleans-=len(x)//4
        open(f"hash\\{i}\\{j}\\{k}\\{l}.txt","wb").write(x)
    plain_cleans=0
    for i,j,k,l in tqdm(itertools.product("0123456789abcdef","0123456789abcdef","0123456789abcdef","0123456789abcdef"),"明文去重",65536):
        x=open(f"dict\\{i}\\{j}\\{k}\\{l}.txt","rb").read().splitlines()
        plain_cleans+=len(x)
        x=[a for a in set(x) if m5(a)[:4]==i+j+k+l]
        plain_cleans-=len(x)
        open(f"dict\\{i}\\{j}\\{k}\\{l}.txt","wb").write(b'\n'.join(x))
    return cleans,plain_cleans

#加载文件函数
def load_file(infor,filename=""):
    if not filename:
        print("该目录下文件（夹）有:")
        blacklist=["log.txt","main.py","dict","hash","$RECYCLE.BIN","System Volume Information"]
        for i in os.listdir():
            if i not in blacklist:print(i)
    while (not filename or not os.path.exists(filename)) and filename!="t":
        filename = input(f"请输入{infor}文件(夹)名，输入't'返回菜单：").strip()
    filenames=[]
    if filename!="t":                
        if os.path.isdir(filename):     #检测到文件夹则进行递归读取
            for path,_,lis in os.walk(filename):
                filenames+=[path+"\\"+i for i in lis if i.endswith(".txt") or i.endswith(".dic")]
        else:filenames=[filename]       #否则只读取该文件
##    print(filenames)
    return filenames
    
#初始化函数    
def inital():
    try:
        if x:=dict_output():
            a=input(f"警告！出厂设置会删除现有字典的{x}条值,请输入 0263hdas#$@ 以继续进行出厂设置：")
            if a!='0263hdas#$@':return 0
    except Exception:pass
    report("正在进行出厂设置...")
    t=time()
    for i,j,k in tqdm(itertools.product("0123456789abcdef","0123456789abcdef","0123456789abcdef"),"初始化字典文件",4096):
        os.makedirs(f"hash\\{i}\\{j}\\{k}", exist_ok=True)
        os.makedirs(f"dict\\{i}\\{j}\\{k}", exist_ok=True)
        for l in "0123456789abcdef":
            open(f"hash\\{i}\\{j}\\{k}\\{l}.txt","w")
            open(f"dict\\{i}\\{j}\\{k}\\{l}.txt","w")
    report(f"初始化完成，用时{time()-t:.3f}秒，可以输入2开始添加字典了")

#字典写入函数
def dict_write(dic):
    hash_dic={f"{i:04x}":b"" for i in range(65536)}
    
    #查询原字典，进行去重
    all_count=0
    tmp_count=0
    for i,j,k,l in tqdm(itertools.product("0123456789abcdef","0123456789abcdef","0123456789abcdef","0123456789abcdef"),"字典去重与哈希计算",65536):
        #去重的读取文件行↓
        prev=set(open(f"dict\\{i}\\{j}\\{k}\\{l}.txt","rb").read().splitlines())
        i=i+j+k+l
        all_count+=len(dic[i])
        #去重的去重行↓
        dic[i]=set(dic[i])-set(prev)
        tmp_count+=len(dic[i])
        for k in dic[i]:
            for j in hash_list(k):
                hash_dic[j[:4]]+=bytes.fromhex(j[4:8]+i)
##    print(dic)
##    print(hash_dic)
    if tmp_count:
        print(f"\n需要新加载 {tmp_count}/{all_count} 条，以下字典写入时请勿退出！若不慎退出，请在重新写入字典之后进行哈希去重")
    
        #先进行哈希写入，后进行明文写入（防止中途暂停可以重新加载和哈希去重补救）
        for i,j,k,l in tqdm(itertools.product("0123456789abcdef","0123456789abcdef","0123456789abcdef","0123456789abcdef"),"写入哈希字典",65536):
            if x:=hash_dic[i+j+k+l]:
                open(f"hash\\{i}\\{j}\\{k}\\{l}.txt","ab").write(x)
        for i,j,k,l in tqdm(itertools.product("0123456789abcdef","0123456789abcdef","0123456789abcdef","0123456789abcdef"),"写入明文字典",65536):
            if x:=dic[i+j+k+l]:
                open(f"dict\\{i}\\{j}\\{k}\\{l}.txt","ab").write(b'\n'+b'\n'.join(x))
    else:print(f"\n需要新加载 {tmp_count}/{all_count} 条，本批次无需更新")
    return tmp_count

#字典构造函数
def construct_dict(filenames):
    ii=0
    len_count=0     #统计字典加载条数
    count=0         #统计更新条数
    dic={f"{i:04x}":[] for i in range(65536)}
    q=tqdm(desc=f'读取字典第 0-{flows-1} 条',total=flows)
    for filename in filenames:
        print()
        report(f"开始添加{filename}字典")
        with open(filename,"rb") as f:
            x=f.readline()
            while x:
                while q.n<flows and x:
                    q.update(1)
                    if not x:reading=False;break
                    dic[m5(x.strip())[:4]].append(x.strip())
                    x=f.readline()
                if q.n>=flows:
                    len_count+=q.n
                    q.close()
                    report(f"第 {len_count-flows}-{len_count-1} 条读取完成")
                    new_add=dict_write(dic)
                    q=tqdm(desc=f'读取字典第 {len_count}-{len_count+flows-1} 条',total=flows)   
                    count+=new_add
                    dic={f"{i:04x}":[] for i in range(65536)}    
    q.close()
##    print(1)
    count+=dict_write(dic)    
    return count

#哈希格式检查函数
def hash_check(md, pri=False):
    md = md.replace(" ", "")
    if not 10<=len(md)<=128:
        if pri:print(f"密文长度为{len(md)}，不在本程序检测范围内(10<=length<=128)，请重新输入！")
        return 0
    
    if x:=re.search("[^0-9a-fA-F]",md):
        if pri:print(f"密文第{x.start()}位\"{md[x.start()]}\"不是16进制数，请重新输入！")
        return 0
    return md.lower()

#单条文本哈希加密函数
def hash_calcu(text):
    print()
    print("结果如下：")
    a=text.encode("gbk")
    b=text.encode("utf-8")
    li=hash_list(a)
    for j,n in enumerate(li):
        print(n,f"\t({encode_lis[j]})")
    if a!=b:
        print("\n检测到utf-8与gbk编码不同，以上为gbk编码，以下为utf-8编码")
        li2=hash_list(b)
        for j,n in enumerate(li2):
            print(n,f"\t({encode_lis[j]})")
            
    report(f"检查字典中是否有 {text}")
    t=time()
    flag=True
    
    ma=m5(a)
    if not a in open(f"dict\\{ma[0]}\\{ma[1]}\\{ma[2]}\\{ma[3]}.txt","rb").read().splitlines():
        for j in li:
            open(f"hash\\{j[0]}\\{j[1]}\\{j[2]}\\{j[3]}.txt","ab").write(bytes.fromhex(j[4:8]+ma))
        open(f"dict\\{ma[0]}\\{ma[1]}\\{ma[2]}\\{ma[3]}.txt","ab").write(b"\n"+a)
        flag=False
        
    if a!=b:
        mb=m5(b)
        if not b in open(f"dict\\{mb[0]}\\{mb[1]}\\{mb[2]}\\{mb[3]}.txt","rb").read().splitlines():
            for j in li2:
                open(f"hash\\{j[0]}\\{j[1]}\\{j[2]}\\{j[3]}.txt","ab").write(bytes.fromhex(j[4:8]+mb))
            open(f"dict\\{mb[0]}\\{mb[1]}\\{mb[2]}\\{mb[3]}.txt","ab").write(b"\n"+b)
            flag=False
            
    if flag:report(f"字典中已存在 {text}，用时{time()-t:.3f}秒")
    else:report(f"字典中不存在 {text}，添加完成！用时{time()-t:.3f}秒.")

#哈希判断正误函数
def hash_judge(md,t,lis):
    flag=[]
    for j in lis:
        for k,n in enumerate(hash_list(j)):
            if n.startswith(md) or md.startswith(n):
                try:print(f"SUCCESS!\n\n{j.decode('utf-8')}\n")
                except:print(f"SUCCESS!\n\n{j}\n")
                report(f"严谨形式:{[j]}\n哈希值为:{n}",True)
                report(f"碰撞成功！加密方式为{encode_lis[k]}，用时{time()-t:.5f}秒")
                try:flag+=[j.decode('utf-8'),encode_lis[k],n]
                except:flag+=[str(j),encode_lis[k],n]
                
    return flag

#哈希碰撞函数
def hash_crash(md,silent=False):
    t=time()
    flag=[]
    txt=open(f"hash\\{md[0]}\\{md[1]}\\{md[2]}\\{md[3]}.txt","rb").read()
    for i in range(0,len(txt),4):
        if txt[i:i+2].hex()==md[4:8]:
            x=txt[i+2:i+4].hex()
            flag+=hash_judge(md,t,open(f"dict\\{x[0]}\\{x[1]}\\{x[2]}\\{x[3]}.txt","rb").read().splitlines())
    flag+=hash_judge(md,t,[b"\n",b"\n\n",b"\n\n\n",b""])
    if not flag:
        report(f"碰撞失败，用时{time()-t:.3f}秒，字典中不存在该哈希值。")
    return flag
        
#新增算法函数
#新算法只能手动修改程序添加，此函数只是写了个框架但是具体还是要改，改完才能运行程序
#为字典内已经有的词条新增哈希算法...应该会很慢
def add_algorithm():
    t=time()
    length=dict_output()
    report(f"现有字典长度为{length}")
    report("开始添加新算法...应该会很慢，但请勿退出！")
    count=0
    sum_length=0
    hash_dic={f"{_:04x}":b"" for _ in range(65536)}
    for i,j,k,l in tqdm(itertools.product("0123456789abcdef","0123456789abcdef","0123456789abcdef","0123456789abcdef"),"字典读取",65536):
        with open(f"dict\\{i}\\{j}\\{k}\\{l}.txt","rb") as f:
            x=f.readline()
            while x:
                x=f.readline()
                if x:
                    #↓↓↓要改的地方
                    n=s512(x)   #新算法（文本变量为m）
                    #↑↑↑此处函数添加完之后有两处需要添加的地方，分别是：
                    #开头名称列表 encode_lis 一处，开头计算列表 hash_list -> lis 一处
                    #注意两个列表内索引需相同，以及不要加在ntlm后面
                    #若有如ntlm单独一种编码方式，请咨询开发者详细事宜
                    hash_dic[n[:4]]+=bytes.fromhex(n[4:8]+i+j+k+l)
                    count+=1
        if count>flows:
            sum_length+=count
            for i,j,k,l in tqdm(itertools.product("0123456789abcdef","0123456789abcdef","0123456789abcdef","0123456789abcdef"),f"本轮写入哈希至 {sum_length/length*100:.2f}%",65536):
                open(f"hash\\{i}\\{j}\\{k}\\{l}.txt","ab").write(hash_dic[i+j+k+l])
            count=0        
            hash_dic={f"{_:04x}":b"" for _ in range(65536)}
    sum_length+=count
    for i,j,k,l in tqdm(itertools.product("0123456789abcdef","0123456789abcdef","0123456789abcdef","0123456789abcdef"),f"本轮写入哈希至 {sum_length/length*100:.2f}%",65536):
        open(f"hash\\{i}\\{j}\\{k}\\{l}.txt","ab").write(hash_dic[i+j+k+l])
    report(f"写入完成！用时{time()-t:.3f}秒")
    
#主程序    
if __name__ == "__main__":
        
    try:
        if "dict" not in os.listdir():
            print("发现是第一次使用，请输入1进行初始设置，否则后续步骤无法进行")
        while True:
            file_path=""
            mode = input('''请选择模式:
0.查看字典长度
1.出厂设置
2.添加字典
3.哈希加密
4.导出字典
5.批量爆破(所有哈希需一行一条存在文件里)
6.哈希去重(程序异常导致字典混乱的时候使用)
7.添加算法(需要手动修改程序)
回车直接开始字典破解：''')
            if mode not in ["0","1","2","3","4","5","6","7"] and os.path.exists(mode):
                file_path=mode
                mode = input('''
程序检测到系统下存在该文件（夹），请选择
1.添加字典
2.批量爆破
其他任意键返回菜单，请输入:''')
                if mode=="1":mode="2"
                elif mode=="2":mode="5"
                else:print();continue
            if mode == "0":
                report(f"现有字典长度为{dict_output()}")
                
            elif mode == "1":
                inital()
                pass
            
            elif mode == "2":
                if filenames:=load_file("待载入字典",file_path):
                    t=time()
                    new_add=construct_dict(filenames)
                    report(f"所有字典合并完成！原字典里没有的词条数目为{new_add}，字典总条数为{dict_output()}，总共用时{time()-t:.3f}秒")

            elif mode == "3":
                text = input("请输入需要哈希加密的数据：")
                hash_calcu(text)
                
            elif mode == "4":
                t=time()
                length=dict_output(False)
                report(f"已经导出到output.txt,总条数为{length}，用时{time()-t:.3f}秒")
                
               
            elif mode == "5":
                if filenames:=load_file("待爆破哈希列表",file_path):
                    t=time()
                    sum_length=0
                    crack_num=0
                    with open("output.csv","w",encoding="gbk") as f:
                        f.write("哈希,明文,哈希算法,原哈希,...\n")
                        for filename in filenames:
                            if os.path.getsize(filename)>1024*1024*10:
                                choose=input(f"您想要爆破文件大小超过了10MB,其大小为{os.path.getsize(filename)//1048576}MB,是否继续进行爆破(Y/N)?")
                                if choose.lower() not in ["y","yes"]:continue
                            report(f"准备批量爆破 {filename} 哈希列表文件")
                            l=open(filename,"r",encoding="utf-8",errors="ignore").read().splitlines()
                            sum_length+=len(l)
                            for i in l:
                                if hash_check(i):
                                    report(f"正在爆破 {i}")
                                    if lis:=hash_crash(i):
                                        f.write(",".join([i]+lis)+"\n")
                                        crack_num+=1
                    report(f"批量爆破完成！爆破成功数{crack_num}/{sum_length}，爆破结果已保存在output.csv中，总共用时{time()-t:.3f}秒")
                    if crack_num:os.startfile("output.csv")

            elif mode == "6":
                t=time()
                length,plain_length=balance()
                report(f"哈希去重完成，清理哈希条数{length}条，清理明文条数{plain_length}条，用时{time()-t:.3f}秒")
                          
            elif mode == "7":
                print("比较危险，可以咨询开发者运行此模式")
##                add_algorithm()
                pass

            else:
                begin=hash_check(mode)
                if not begin and mode:
                    hash_calcu(mode)
                else:
                    while not begin:
                        begin = input("请输入你的哈希密文，输入't'返回菜单：")
                        if begin == "t":break
                        begin = hash_check(begin, True)
                    if begin!="t":
                        hash_crash(begin)
            print()
    except Exception as e:
        #error_type = type(e).__name__  # 获取错误类型
        #error_msg = str(e)  # 获取错误消息
        traceback.print_exc()  # 打印异常追踪信息
        traceback.print_exc(file=open('log.txt','a'))
    while 1:
        input("程序出错:请将报错信息及之前运行的内容截图并联系开发者")
