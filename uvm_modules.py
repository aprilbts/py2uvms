# coding: utf-8

import string
import json

class UvmContract:
    def init(self):
        print("init")

class UvmTable:
    type="table"



class UvmMap(UvmTable):
    def __init__(self):
        self._hashitems = {}
    #_items = []
    #_hashitems = {}

def setMap(tab,k,v):
    if (isinstance(tab, UvmMap)):
        iss = tab._hashitems.items()
    else:
        iss = tab.items()
    iss[k]=v

def getMap(tab,k):
    if (isinstance(tab, UvmArray)):
        ll = tab._arrayitems
    else:
        ll = tab
    return ll[k]

def setArray(tab,idx,v):
    if (isinstance(tab, UvmArray)):
        ll = tab._arrayitems
    else:
        ll = tab
    ll[idx]=v

def appendArray(tab,v):
    if (isinstance(tab, UvmArray)):
        ll = tab._arrayitems
    else:
        ll = tab
    ll.append(v)

def getArrayCount(tab):
    if (isinstance(tab, UvmArray)):
        ll = tab._arrayitems
    else:
        ll = tab
    return len(ll)

class UvmArray(UvmTable):
    def __init__(self):
        self._arrayitems = []

