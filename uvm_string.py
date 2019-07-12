
def len(v):
    return v.__len__()

def byte(v):
    return v[0:0]

def char(i):
    return ""+char(i)

def dump(toDumpFunction,strip):
    return "mock of dump function"

def find(text, pattern, init = 0, plain = False):
    return text.find(pattern,init)


def format(format,arg1):
    print("暂时不支持py中模式字符串库的mock")
    return ""


def gmatch(text, pattern):
    print("暂时不支持py中模式字符串库的mock")
    return ""

def gsub(text, pattern):
    print("暂时不支持py中模式字符串库的mock")
    return ""

def split(str, sep):
    return str.split(sep)


def match():
    print("暂时不支持py中模式字符串库的mock")
    return ""

def lower(v):
    s =v
    s.lower()
    return s

def upper(v):
    s =v
    s.upper()
    return s

def rep(str,n,sep):
    if str==None or len(str)<1:
        return ""
    result=""
    for i in range(0,n):
        if i>0:
            result+=sep
        result+=str
    return result

def reverse(v):
    return ''.join(reversed(v))

def sub(str,i,j):
    if i>=0 and j>=i:
        return str[i:j-i]
    elif i<=0 and j<=i:
        temp = reverse(str)
        return temp[-i:-j-i]
    else:
        print("error i j")
        exit(1)


def pack(str):
    print("暂时不支持py中模式字符串库的mock")
    return ""

def packsize(str):
    print("暂时不支持py中模式字符串库的mock")
    return ""

def unpack(str):
    print("暂时不支持py中模式字符串库的mock")
    return ""
