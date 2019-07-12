
def abs(v):
    if(v<0):
        return -v
    return v

def tointeger(v):
    return int(v)

def max(a,b):
    if(a>b):
        return a
    return b

def min(a,b):
    if(a<b):
        return a
    return b

def floor(v):
    a,b =divmod(v,1)
    return a

def type(v):
     if isinstance(v,int):
         return "int"
     else:
         return "number"


pi = 3.1415926535897931
maxinteger = 9223372036854775807
mininteger = -9223372036854775808