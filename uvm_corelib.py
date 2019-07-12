# coding: utf-8
import random
import string
import dis
import json
from uvm_modules import *


def transfer_from_contract_to_address(addr,symbol,amount):
    arg = ""
    arg=addr
    return 0

def import_contract_from_address(addr):
    arg = ""
    arg = addr
    con = {"name":"conname"}
    return con

caller = "caller_v"
caller_address = "caller_v_address"


def pairs(tab):
    def iterfunc(tab, key):
        rk = None
        rv = None
        found = False
        for k, v in tab._hashitems.items():
            if(key==None):
                rk = k
                rv = v
                break
            if (found):
                rk = k
                rv = v
                found = False
                break
            if (k == key):
                found = True
        return rk, rv
    return iterfunc


def createMap():
    return UvmMap()


def createArray():
    return UvmArray()


def pairs(tab):
    if (not isinstance(tab,UvmMap)) and (type(tab) !="table") :
        print("not UvmMap,error")
        exit(1)
    def iterfunc(tab, key):
        if not isinstance(tab, UvmMap) and  (type(tab) !="table"):
            print("not UvmMap,error")
            exit(1)
        rk = None
        found = False
        if(isinstance(tab, UvmMap)):
            iss = tab._hashitems.items()
        else:
            iss = tab.items()
        for k, v in iss:
            if(key==None):
                rk = k
                break
            if (found):
                rk = k
                found = False
                break
            if (k == key):
                found = True
        return rk
    return iterfunc


def ipairs(tab):
    if (not isinstance(tab,UvmArray)) and (type(tab) !="table") :
        print("not UvmArray,error")
        exit(1)
    def iterfunc(tab, key):
        if not isinstance(tab, UvmArray) and (type(tab) !="table"):
            print("not UvmArray,error")
            exit(1)
        rk = None
        rv = None
        found = False
        i = 0
        if (isinstance(tab, UvmArray)):
            ll = tab._arrayitems
        else:
            ll = tab
        count = len(ll)
        for k in range(0, count):
            if (key == None):
                rk = 0
                rv = ll[k]
                break
            if (found):
                rk = k
                found = False
                break
            if (k == key):
                found = True
        return rk
    return iterfunc

def getLenOf(arg):
    if(type(arg) == "string"):
        return len(arg)
    elif(isinstance(arg,UvmArray)):
        return getArrayCount(arg)
    elif (isinstance(arg, UvmMap)):
        print("error , not support get map len")
        exit(1)
    else:
        print("error , not support get len of type:"+str(type(arg)))
        exit(1)


def emit(eventName,content):
    print("emit:",eventName,content)

def tostring(v):
    return str(v)

def tojsonstring(v):
    return json.dumps(v)

def pprint(o):
    print(o)

def tointeger(o):
    return int(o)


def tonumber(o):
    return float(o)

def type(v):
    if isinstance(v,int):
        return "int"
    elif isinstance(v,dict):
        return "table"
    elif isinstance(v,list):
        return "table"
    elif isinstance(v,float):
        return "number"
    elif isinstance(v,str):
        return "string"
    else:
        return ""



def error(msg):
    print("error:",msg)

def getmetatable(t):
    return {}

def setmetatable(t,metaT):
    return None

def toboolean(v):
    return bool(v)

def totable(v):
    return v

def rawequal(a,b):
    return a==b

def rawget(t,k):
    return t[k]

def rawset(t,k,v):
    t[k]=v

def rawlen(o):
    return len(o)

def get_contract_balance_amount(conaddr,asset):
    return 0

def get_chain_now():
    return 0

def get_chain_random():
    return random(0,100000000)

def get_header_block_num():
    return 1999

def get_waited():
    return 900

def get_transaction_fee():
    return 1

def transfer_from_contract_to_public_account(toacount,asset,amount):
    return 0

def is_valid_address(addr):
    return True

def is_valid_contract_address(addr):
    return True

def get_prev_call_frame_contract_address():
    return "preframe"

def get_prev_call_frame_api_name():
    return "preapi"

def get_contract_call_frame_stack_size():
    return 1

def get_system_asset_symbol():
    return "COIN"

def get_system_asset_precision():
    return 8

def fast_map_get(sn,k):
    return None

def fast_map_set(sn,k,v):
    return None

def call_contract_api(conaddr,api_name,arg):
    return None

def static_call_contract_api(conaddr,api_name,arg):
    return None

#return list: [result,code]
def send_message(conaddr,api_name,arg):
    return ["result",0]

def error(msg):
    print("error:",msg)








