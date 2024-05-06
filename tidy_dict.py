def clear_dict(filename="www.txt",path=""):
    with open(path+filename,"r",encoding="gbk",errors='ignore') as f:
        txta=sorted(list(set(f.read().split())))
    with open(path+"new_"+filename,"w") as f:
        f.write('\n'.join(txta))
    print(f"清理完成，字典{'new_'+filename}的长度为{len(txta)}")
    return txta

while 1:
    filename=input("请输入字典名称：")
    try:clear_dict(filename)
    except FileNotFoundError:print("文件名有误！")
