import hashlib
from hashlib import md5,sha256,sha3_256,sha1
import base64
from time import time,sleep
import datetime
import random
import threading
from tqdm import tqdm, trange
import os
import traceback

addtxt = lambda a:a+[".txt",""][a[-4:]==".txt"]
m5 = lambda b:md5(b).hexdigest()
b64 = lambda b:base64.b64encode(b)
s1 = lambda b:sha1(b).hexdigest()
s256 = lambda b:sha256(b).hexdigest()
s3_256 = lambda b:sha3_256(b).hexdigest()
ntlm = lambda b:hashlib.new('md4', b.encode('utf-16le')).hexdigest() #不能先encode
encode_lis=["ntlm","md5","sha1","sha256","sha3_256","m5_m5","m5_m5_m5","m5_sha1","sha1_m5","m5_b64","m5_sha256"]
#坐标：md5前三位+文件夹内地址
filename="1.txt"

#txt读取函数
def txt(func, lis="", file=filename):    #txt('w',text);txt('a',text);
    import encodings;SEpa="\n"
    if func not in ['r','a','w']:raise ValueError("Invalid mode. Expected one of: ['r','a','w']")
    def oper_txt(encod,file=file):
        with open(file, func, encoding=encod) as f:
            if func == "r":return f.read().replace("\ufeff","").split(SEpa)
            else:f.write({"a":SEpa,"w":""}[func]+SEpa.join(lis));return 0
    result=oper_txt('gbk')
    if func=="r":return result

#日志记录函数
def report(message=""):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report_message = f"{timestamp} {message}"  # 添加时间信息
    print(report_message)  # 打印报告
    with open("log.txt", 'a') as f:
        f.write(report_message + "\n")

#初始化函数    
def inital():
    try:
        x=infom()
        if x:
            a=input(f"警告！出厂设置会删除现有字典的{x}条值,请输入 0263hdas#$@ 以继续进行出厂设置：")
            if a!='0263hdas#$@':return 0
    except Exception:pass
    report("正在进行出厂设置...")
    t=time()
    os.makedirs("dict", exist_ok=True)
    os.makedirs("base", exist_ok=True)
    for i in tqdm(range(16),"初始化字典文件"):
        i=hex(i)[2:]
        os.makedirs("dict\\"+i, exist_ok=True)
        os.makedirs(i, exist_ok=True)
        for j in "0123456789abcdef":
            os.makedirs("dict\\"+i+"\\"+j, exist_ok=True)
            os.makedirs(i+"\\"+j, exist_ok=True)
            for k in "0123456789abcdef":
                open(f"dict\\{i}\\{j}\\{k}.txt","w").write("")
                os.makedirs(i+"\\"+j+"\\"+k, exist_ok=True)
                for l in "0123456789abcdef":
                    open(f"{i}\\{j}\\{k}\\{l}.txt","w").write("")
    report(f"初始化完成，用时{time()-t:.3f}秒")

#清理字典函数
def clear_dict(filename="www.txt",path=""):
    report(f"正在清理字典中的非法字符")
    with open(path+filename,"rb") as f:
        txtt=f.read().replace(b'\r',b'').split(b'\n')
        txta=list(set([txtt[j].decode('gbk',errors='ignore') for j in tqdm(range(len(txtt)),"清理非法字符")]))
    print("稍候片刻，正在保存...")
    txt("w",txta,path+'new_'+filename)
    report(f"清理完成，字典{'new_'+filename}的长度为{len(txta)}")

#合并字典函数
def combine_dict(text):
    report("开始合并字典...")
    #按照首字节分类并检查是否已经存在
    x=[f"{i:0>3x}" for i in range(4096)]
    b={i:[] for i in x}  #新加字典，用于记录
    new_add=[]   #新加字典，用于哈希写入
    for i in tqdm(range(len(text)),"数据载入"):
        i=text[i]
        if i:b[m5(i.encode())[:3]].append(i)
    for i in tqdm(range(4096),"字典分类"):
        i=x[i]
        if b[i]:
            a=set(txt("r",0,f"dict\\{i[0]}\\{i[1]}\\{i[2]}.txt"))
            la=len(a)
            if len(b[i])<=la:
                b[i]=[j for j in b[i] if not j in a]
            else:
                b[i]=list(set(b[i])-a)
            new_add+=[[n,i+str(j+la)] for j,n in enumerate(b[i])]
    print("开始进行字典写入，请不要中断程序...")
    if new_add:
        for i in x:
            if b[i]:
                txt("a",b[i],f"dict\\{i[0]}\\{i[1]}\\{i[2]}.txt")
    return new_add

#构建哈希字典函数
def hash_built(new_add):
    report("开始构建哈希字典...")
    built={f"{i:0>4x}":[] for i in range(65536)}
    for k in tqdm(range(len(new_add)),"哈希构建"):
        i=new_add[k]
        b=i[0].encode("gbk")
        a=i[0].encode("utf-8")
        li=[ntlm(i[0]),m5(b),s1(b),s256(b),s3_256(b),m5(m5(b).encode()),m5(m5(m5(b).encode()).encode()),m5(s1(b).encode()),s1(m5(b).encode()),m5(b64(b)),m5(s256(b).encode())]
        if a!=b:
            li+=[m5(a),s1(a),s256(a),s3_256(a),m5(m5(a).encode()),m5(m5(m5(a).encode()).encode()),m5(s1(a).encode()),s1(m5(a).encode()),m5(b64(a)),m5(s256(a).encode())]
        for j,n in enumerate(li):
            built[n[:4]].append(n[4:]+" "+i[1])
        if k%5000000==4999999:
            for n in built:
                if built[n]:
                    txt("a",built[n],f"{n[0]}\\{n[1]}\\{n[2]}\\{n[3]}.txt")
                    built[n]=[]
    for n in built:
        txt("a",built[n],f"{n[0]}\\{n[1]}\\{n[2]}\\{n[3]}.txt")

#单条文本哈希加密函数
def hash_calcu(text):
    print()
    print("结果如下：")
    b=text.encode("gbk")
    a=text.encode("utf-8")
    li=[m5(b),s1(b),s256(b),s3_256(b),m5(m5(b).encode()),m5(m5(m5(b).encode()).encode()),m5(s1(b).encode()),s1(m5(b).encode()),m5(b64(b)),m5(s256(b).encode())]
    for j,n in enumerate(li):
        print(n,f"\t({encode_lis[j+1]})")
    if a!=b:
        print("检测到utf-8与gbk编码不同，以上为gbk编码，以下为utf-8编码")
        li2=[m5(a),s1(a),s256(a),s3_256(a),m5(m5(a).encode()),m5(m5(m5(a).encode()).encode()),m5(s1(a).encode()),s1(m5(a).encode()),m5(b64(a)),m5(s256(a).encode())]
        for j,n in enumerate(li2):
            print(n,f"\t({encode_lis[j+1]})")
    n=ntlm(text)
    print(n,f"\t({encode_lis[0]})")
    t=time()
    x=m5(text.encode())[:3]
    report(f"检查字典中是否有 {text}")
    a=txt("r",0,f"dict\\{x[0]}\\{x[1]}\\{x[2]}.txt")
    if text in a:
        report(f"字典中已存在 {text}，用时{time()-t:.3f}秒")
    else:
        report(f"字典中不存在 {text}，正在进行添加...")
        i=x+str(len(a))
        txt("a",[text],f"dict\\{x[0]}\\{x[1]}\\{x[2]}.txt")
        txt("a",[n[4:]+" "+i],f"{n[0]}\\{n[1]}\\{n[2]}\\{n[3]}.txt")
        for j,n in enumerate(li):
            txt("a",[n[4:]+" "+i],f"{n[0]}\\{n[1]}\\{n[2]}\\{n[3]}.txt")
        if text.encode("gbk")!=text.encode("utf-8"):
            txt("a",[n[4:]+" "+i],f"{n[0]}\\{n[1]}\\{n[2]}\\{n[3]}.txt")
        report(f"添加完成！用时{time()-t:.3f}秒")

#哈希格式检查函数
def hash_check(md, pri=0):
    md = md.replace(" ", "")
    if not len(md) in [16,32,40,64]:
        if pri:print(f"密文长度为{len(md)}，不符合哈希规范(16,32,40,64)，请重新输入！")
        return 0
    md = md.lower()
    for i in range(len(md)):
       if not md[i] in "0123456789abcdef":
            if pri:print(f"密文第{i+1}位\"{md[i]}\"不是16进制数，请重新输入！")
            return 0
    return md

#哈希碰撞函数
def hash_crash(md):
    t=time()
    flag=0
    for i in txt("r",0,f"{md[0]}\\{md[1]}\\{md[2]}\\{md[3]}.txt"):
        if not i or i[0]!=md[4]:continue
        if i.split()[0][:12]==md[4:16]:
            num=i.split()[1]
            value=txt('r',0,f"dict\\{num[0]}\\{num[1]}\\{num[2]}.txt")[int(num[3:])]
            end=time()-t
            print(f"SUCCESS!\n\n{value}\n")
            b=value.encode("gbk")
            a=value.encode("utf-8")
            method=0
            li=[ntlm(value),m5(b),s1(b),s256(b),s3_256(b),m5(m5(b).encode()),m5(m5(m5(b).encode()).encode()),m5(s1(b).encode()),s1(m5(b).encode()),m5(b64(b)),m5(s256(b).encode())]
            li_16=[i[:16] for i in li]
            if md in li:method=encode_lis[li.index(md)]
            elif md in li_16:method=encode_lis[li_16.index(md)]
            elif a!=b:
                li2=[m5(a),s1(a),s256(a),s3_256(a),m5(m5(a).encode()),m5(m5(m5(a).encode()).encode()),m5(s1(a).encode()),s1(m5(a).encode()),m5(b64(a)),m5(s256(a).encode())]
                li2_16=[i[:16] for i in li2]
                if md in li2:method=encode_lis[li2.index(md)]
                elif md in li2_16:method=encode_lis[li2_16.index(md)]
            if method:report(f"碰撞成功！加密方式为{method}，用时{end:.5f}秒")
            else:print("程序出错！")
            flag+=1
    if not flag:
        lis=['31d6cfe0d16ae931b73c59d7e0c089c0', 'd41d8cd98f00b204e9800998ecf8427e', 'da39a3ee5e6b4b0d3255bfef95601890afd80709', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a', '74be16979710d4c4e7c6647856088456', 'acf7ef943fdeb3cbfed8dd0d8f584731', '0144712dd81be0c3d9724f5e56ce6685', '67a74306b06d0c01624fe0d0249a570f4d093747', 'd41d8cd98f00b204e9800998ecf8427e', 'fa1269ea0d8c8723b5734305e48f7d46']
        lis_16=[i[:16] for i in lis]
        if md in lis:
            report(f"碰撞成功！明文为\\x00, 加密方式为{encode_lis[lis.index(md)]}，用时{time()-t:.5f}秒")
        elif md in lis_16:
            report(f"碰撞成功！明文为\\x00, 加密方式为{encode_lis[lis_16.index(md)]}，用时{time()-t:.5f}秒")
        else:
            report(f"碰撞失败，用时{time()-t:.3f}秒，字典中不存在该哈希值。")

#新增算法函数
#算法只能手动修改程序添加，此函数只是用来将之前字典内已经有的来构建哈希字典
def add_algorithm():
    t=time()
    report("开始添加新算法")
    li="0123456789abcdef"
    built={i:{i:{i:{i:[] for i in li} for i in li} for i in li} for i in li}
    for i in tqdm(range(256),"哈希计算"):
        x=txt("r",0,f"dict\\{i}.txt")
        for j,y in enumerate(x):
            b=y.encode("gbk")
            a=y.encode("utf-8")
            n=s1(b64(b))#新算法
            num=11#算法序号==列表长度
            #此函数添加完之后有七处需要添加的地方，分别是：
            #开头列表一处，字典合并两处，单独计算哈希两处，碰撞获取哈希方法两处
            #然后才能重新运行程序
            built[n[0]][n[1]][n[2]][n[3]].append(n[4:]+" "+str(j*256+i))
            if a!=b:
                n=s1(b64(a))#新算法
                #print(n)
                built[n[0]][n[1]][n[2]][n[3]].append(n[4:]+" "+str(j*256+i))
    report("正在写入...")
    for i in "0123456789abcdef":
        for j in "0123456789abcdef":
            for k in "0123456789abcdef":
                for l in "0123456789abcdef":
                    txt("a",built[i][j][k][l],f"{i}\\{j}\\{k}\\{l}.txt")
    report(f"写入完成！用时{time()-t:.3f}秒")

#统计字典长度函数
def infom():
    a=-4096
    for i in tqdm(range(4096),"统计字典长度"):
        a+=len(txt("r",0,"dict\\"+'\\'.join(f"{i:0>3x}")+".txt"))
    return a

#导出字典函数
def output():
    open("output.txt","w").write("")
    for i in tqdm(range(4096),"导出字典"):
        a=txt("r",0,"dict\\"+'\\'.join(f"{i:0>3x}")+".txt")
        txt("a",list(filter(None,a)),"output.txt")

#主程序    
if __name__ == "__main__":
        
    try:
        while True:
            mode = input('''请选择模式:
0.查看字典长度
1.出厂设置
2.添加字典
3.哈希加密
4.添加算法
5.导出字典
回车直接开始字典破解：''')
            if mode == "0":
                a=infom()
                report(f"现有字典长度为{a}")
            elif mode == "1":
                inital()
                pass
            elif mode == "2":
                filename = addtxt(input("请输入待载入字典文件名："))
                while not filename in os.listdir() and filename != "t.txt" and filename!=".txt" and not "new_"+filename in os.listdir():
                    filename=addtxt(input("该字典不存在，请重新输入："))
                if filename!="t.txt":
                    if filename==".txt":
                        t=time()
                        for filename in os.listdir('base'):
                            report(f"准备合并{filename}字典")
                            if filename[:4]=="new_":filename=filename[4:]
                            elif not "new_"+filename in os.listdir('base'):
                                text=clear_dict(filename,'base\\')
                            text=txt("r",0,"base\\new_"+filename)
                            new_add=combine_dict(text)
                            if new_add:
                                report(f"字典合并完成！原字典里没有的词条数目为{len(new_add)}")
                                hash_built(new_add)
                            else:report(f"{filename}输入字典条目均已存在，无需更新")
                        
                    else:
                        t=time()
                        report(f"准备合并{filename}字典")
                        if filename[:4]=="new_":filename=filename[4:]
                        elif not "new_"+filename in os.listdir():
                            clear_dict(filename)
                        text=txt("r",0,"new_"+filename)
                        new_add=combine_dict(text)
                        if new_add:
                            report(f"字典合并完成！原字典里没有的词条数目为{len(new_add)}")
                            hash_built(new_add)
                        else:report("输入字典条目均已存在，无需更新")
                    report(f"字典合并完成！字典总条数为{infom()}，总共用时{time()-t:.3f}秒")

            elif mode == "3":
                text = input("请输入需要哈希加密的数据：")
                hash_calcu(text)
                
            elif mode == "4":
                print("比较危险，可以咨询开发者运行此模式")
##                add_algorithm()
                pass
            elif mode == "5":
                t=time()
                output()
                report(f"已经导出到output.txt，用时{time()-t:.3f}秒")
            else:
                begin=hash_check(mode)
                while not begin:
                    begin = input("请输入你的哈希密文，输入't'退出：")
                    if begin == "t":break
                    begin = hash_check(begin, 1)
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
