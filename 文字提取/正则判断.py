import re

def process_string(input_string):
    aa=[]
    # 用空格切分字符串
    parts = input_string.split()
    # 正则表达式1：包含数字和字母
    pattern_alphanumeric = re.compile(r'(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{2,8}$')
    # 正则表达式2：四 ~ 七个纯数字
    pattern_at_least_two_digits = re.compile(r'\d{4,7}$')
    # 遍历每个切分后的部分
    for part in parts:
        # 检查是否包含数字和字母或者纯数字
        if pattern_alphanumeric.match(part) or pattern_at_least_two_digits.match(part):
            aa.append(part)
    return aa

if __name__ == '__main__':
    a='Aceite p04476'
    b='sdighsg'
    c='s4967xl'
    d='v0-4985'
    e='shfsf v0-4985'
    f='123'
    g='1234568956'
    h='45825'

    ylist=[]
    llist=[a,b,c,d,e,f,g,h]
    for i in llist:
        ma= process_string(i)
        ylist.extend(ma)
    print(ylist)
