import os
import wget

#文件夹修理函数
def txt(func, lis="", file=""):
    SEpa="\n"
    if func not in ["r", "a", "w"]:raise ValueError("Invalid value for opening mode. Expected one of: ['r', 'a', 'w']")
    def oper_txt(encod,file=file):
        with open(file, func, encoding=encod) as f:
            if func == "r":return f.read().replace("\ufeff","").split(SEpa)
            else:
                txt = SEpa.join(lis)
                if func == "a":txt = SEpa + txt
                f.write(txt)
                return 0
    try:
        result=oper_txt('gbk')
    except (UnicodeDecodeError, UnicodeEncodeError, FileNotFoundError):
        try:result=oper_txt('utf-8')
        except (UnicodeDecodeError,UnicodeEncodeError):result=oper_txt('utf-16')
        #except:return 0
    if func=="r":return result

'''
下载一个网站目录下的文件
文件列表提前放在filename指定的文件里面
然后url改一下，改成网站目录，结尾不要加'/'
然后下载到本目录下的download文件夹里面
'''

filename="1.txt"
url="http://downloads.skullsecurity.org/passwords"
lis=list(filter(None,txt("r",0,filename)))
os.makedirs("download", exist_ok=True)
for i in lis:
    try:
        wget.download(url+"/"+i,"download"+"\\"+i)
        print("\n",i,"ok")
    except Exception:
        print("\n",i,"\t\tError!")

