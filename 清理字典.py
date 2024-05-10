def clear_dict(filename="www.txt",path=""):
    print(f"正在清理字典中的非法字符")
    with open(path+filename,"rb") as f:
        txtt=f.read().replace(b'\r',b'').split(b'\n')
        txta=list(set([txtt[j].decode('gbk',errors='ignore') for j in tqdm(range(len(txtt)),"清理非法字符")]))
    print("稍候片刻，正在保存...")
    txt("w",txta,path+'new_'+filename)
    print(f"清理完成，字典{'new_'+filename}的长度为{len(txta)}")
    return txta

while 1:
    filename=input("请输入字典名称：")
    try:clear_dict(filename)
    except FileNotFoundError:print("文件名有误！")
