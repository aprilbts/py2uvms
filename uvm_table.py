# coding: utf-8

def concat(t,sep):
    count =len(t)
    result=""
    for i in range(count):
        if i>0 and sep!=None:
            result+=sep
        result+=str(t[i])
    return result


def length(t):
    return len(t)

def insert(col,pos,value):
    if col==None:
        return
    if pos>len(col) or pos<0:
        return
    col.insert(pos,value)

def append(col,value):
    col.append(value)

def remove(col,pos):
    if pos<0 or pos>=len(col):
        return
    col.pop(pos)

def sort(col):
    col.sort()

