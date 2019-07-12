
class UvmBigInt:
    @staticmethod
    def createBigInt(o):
        return UvmBigInt(o)

    def __init__(self,o):
        self._o = o


def bigint(v):
    return UvmBigInt(v)

def add(a,b):
    return int(a)+int(b)

def sub(a,b):
    return int(a)-int(b)

def mul(a,b):
    return int(a)*int(b)

def div(a,b):
    return int(a)/int(b)

def pow(a,b):
    return int(a)**int(b)

def rem(a,b):
    return int(a)%int(b)

def tohex(v):
    return hex(v)

def toint(v):
    return int(v)

def tostring(v):
    return str(v)

def gt(a,b):
    return int(a)>int(b)

def ge(a,b):
    return int(a)>=int(b)

def lt(a,b):
    return int(a)<int(b)

def le(a,b):
    return int(a)<=int(b)

def eq(a,b):
    return int(a)==int(b)

def ne(a,b):
    return int(a)!=int(b)

def max(a,b):
    if int(a)>int(b):
        return a
    return b

def min(a,b):
    if int(a)<int(b):
        return a
    return b



pi = 3.1415926535897931
maxinteger = 9223372036854775807
mininteger = -9223372036854775808