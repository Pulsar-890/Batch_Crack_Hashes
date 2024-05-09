import os
import wget

#文件夹修理函数
def txt(func, lis="", file=""):
    import encodings;SEpa="\n"
    if func not in ['r','a','w']:raise ValueError("Invalid mode. Expected one of: ['r','a','w']")
    def oper_txt(encod,file=file):
        with open(file, func, encoding=encod) as f:
            if func == "r":return f.read().replace("\ufeff","").split(SEpa)
            else:f.write({"a":SEpa,"w":""}[func]+SEpa.join(lis));return 0
    for k in ['gbk', 'utf-8', 'utf-16']+list(set(encodings.aliases.aliases.values())):
        try:result=oper_txt(k);break
        except (UnicodeDecodeError, UnicodeEncodeError, FileNotFoundError):result=0
    if func=="r":return result
    
'''
下载一个网站目录下的文件
需要把网站目录填入到url变量中
文件列表提前放在filename指定的文件里面（默认是1.txt）
文件下载到dirname目录里面（默认是download）
file_type记了所有能下载的文件后缀（一定程度上识别文件列表中的文件，有需要可以自己添加后缀）
或者设置all_file为true下载任意格式文件，但请确保文件列表都是你要下载的文件
'''

url="http://downloads.skullsecurity.org/passwords"
filename="1.txt"
dirname="download"
filetype=[".txt",".dic",".gz",".zip",".rar",".bz2",".7z",".tar"]
all_filetype=False

lis=list(filter(None,txt("r",0,filename)))
os.makedirs(dirname, exist_ok=True)
for j in lis:
    for i in j.split():
        if not i in os.listdir(dirname) and (all_filetype or any(i.endswith(t) for t in filetype)):
            print(i,"：")
            try:
                wget.download(url+"/"+i,dirname+"\\"+i)
                print("\tOK!")
            except Exception:
                print("\tError!")

