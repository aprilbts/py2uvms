
# coding: utf-8
import random
import string
import dis_to_instructions
import json
import dis
from uvm_types import *

import types
from uvm_modules import *
import os, sys

_have_code = (types.MethodType, types.FunctionType, types.CodeType,
              classmethod, staticmethod, type)

eventsNames =[]

pyoplen = 2 # 2 byte
def MakeLoadConstInst(proto, ins, result, targetSlot, value, commentPrefix):
    literalval = ""
    if type(value) is str:
        literalval = "\"" + str(value) + "\""
    elif type(value) is bool:
        if value:
            literalval = "true"
        else:
            literalval = "false"
    elif value is None:
        literalval = "nil"
    else:
        literalval = str(value)
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_LOADK, ins,
                            ("loadk %" + str(targetSlot) + " const " + literalval + commentPrefix))
    result.append(uvmIns)


def PushIntoEvalStackTopSlot(proto, slotIndex, ins, result, commentPrefix):
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_PUSH, ins, ("push %" + str(slotIndex) + commentPrefix))
    result.append(uvmIns)


def PopFromEvalStackTopSlot(proto, slotIndex, ins, result, commentPrefix):
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_POP, ins, ("pop %" + str(slotIndex) + commentPrefix))
    result.append(uvmIns)


#################################################################################################

def translate_BINARY_SUBSCR(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    keyidx = proto.tmp3StackTopSlotIndex
    PopFromEvalStackTopSlot(proto, keyidx, ins, result, newcommentPrefix)
    tabidx = keyidx - 1
    PopFromEvalStackTopSlot(proto, tabidx, ins, result, newcommentPrefix)
    validx = keyidx - 2
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABLE, ins,
                            ("gettable %" + str(validx) + " %" + str(tabidx) + " %" + str(keyidx) + newcommentPrefix))
    result.append(uvmIns)
    PushIntoEvalStackTopSlot(proto, validx, ins, result, newcommentPrefix);
    return result


userdefined_metheds = []
userdefined_methedsNames = []
uvm_modules = {"uvm_json":"json","uvm_math":"math","uvm_safemath":"safemath","uvm_string":"string","uvm_table":"table"}
builtin_g_funcs = {"str":"tostring","int":"tointeger","float":"tonumber","bool":"toboolean"}

wrapped_g_funcs = ["call_contract_api","static_call_contract_api"]

def translate_LOAD_GLOBAL(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    constValue = proto.ConstantValues[ins.arg + proto.PycoConstsNum]
    targetSlotIdx = proto.tmp1StackTopSlotIndex
    if (constValue in base_conss):
        if (constValue == True):
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_LOADBOOL, ins,
                                    ("loadbool %" + str(targetSlotIdx) + " 1 0" + newcommentPrefix))
            result.append(uvmIns)
        elif (constValue == False):
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_LOADBOOL, ins,
                                    ("loadbool %" + str(targetSlotIdx) + " 0 0" + newcommentPrefix))
            result.append(uvmIns)
        elif (constValue == None):
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_LOADNIL, ins,
                                    ("loadnil %" + str(targetSlotIdx) + " 0" + newcommentPrefix))
            result.append(uvmIns)
    elif (constValue in builtin_g_funcs.keys()):
        envIndex = proto.InternUpvalue("ENV")
        realvalue = builtin_g_funcs[constValue]
        proto.InternConstantValue(realvalue)
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABUP, ins,
                                ("gettabup %" + str(targetSlotIdx) + " @" + str(
                                    envIndex) + " const " + "\"" + realvalue + "\"" + newcommentPrefix))
        result.append(uvmIns)
    elif (constValue in uvm_modules.keys()):
        envIndex = proto.InternUpvalue("ENV")
        realvalue = uvm_modules[constValue]
        proto.InternConstantValue(realvalue)
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABUP, ins,
                                ("gettabup %" + str(targetSlotIdx) + " @" + str(
                                    envIndex) + " const " + "\"" + realvalue + "\"" + newcommentPrefix))
        result.append(uvmIns)
    elif (constValue in uvm_globals):
        envIndex = proto.InternUpvalue("ENV")
        if (constValue == "appendArray"):
            proto.InternConstantValue("table")
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABUP, ins,
                                    ("gettabup %" + str(targetSlotIdx) + " @" + str(
                                        envIndex) + " const " + "\"table\"" + newcommentPrefix))
            result.append(uvmIns)
            proto.InternConstantValue("append")
            funckeyslotIdx = targetSlotIdx + 1
            MakeLoadConstInst(proto, ins, result, funckeyslotIdx, "append", newcommentPrefix)
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABLE, ins,
                                    ("gettable %" + str(targetSlotIdx) + " %" + str(
                                        targetSlotIdx) + " %" + str(funckeyslotIdx) + newcommentPrefix))
            result.append(uvmIns)
        elif (constValue == "insertArray"):
            proto.InternConstantValue("table")
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABUP, ins,
                                    ("gettabup %" + str(targetSlotIdx) + " @" + str(
                                        envIndex) + " const " + "\"table\"" + newcommentPrefix))
            result.append(uvmIns)
            proto.InternConstantValue("insert")
            funckeyslotIdx = targetSlotIdx + 1
            MakeLoadConstInst(proto, ins, result, funckeyslotIdx, "insert", newcommentPrefix)
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABLE, ins,
                                    ("gettable %" + str(targetSlotIdx) + " %" + str(
                                        targetSlotIdx) + " %" + str(funckeyslotIdx) + newcommentPrefix))
            result.append(uvmIns)
        elif (constValue == "removeArray"):
            proto.InternConstantValue("table")
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABUP, ins,
                                    ("gettabup %" + str(targetSlotIdx) + " @" + str(
                                        envIndex) + " const " + "\"table\"" + newcommentPrefix))
            result.append(uvmIns)
            proto.InternConstantValue("remove")
            funckeyslotIdx = targetSlotIdx + 1
            MakeLoadConstInst(proto, ins, result, funckeyslotIdx, "remove", newcommentPrefix)
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABLE, ins,
                                    ("gettable %" + str(targetSlotIdx) + " %" + str(
                                        targetSlotIdx) + " %" + str(funckeyslotIdx) + newcommentPrefix))
            result.append(uvmIns)
        elif (constValue == "getArrayCount"):
            proto.InternConstantValue("table")
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABUP, ins,
                                    ("gettabup %" + str(targetSlotIdx) + " @" + str(
                                        envIndex) + " const " + "\"table\"" + newcommentPrefix))
            result.append(uvmIns)
            proto.InternConstantValue("length")
            funckeyslotIdx = targetSlotIdx + 1
            MakeLoadConstInst(proto, ins, result, funckeyslotIdx, "length", newcommentPrefix)
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABLE, ins,
                                    ("gettable %" + str(targetSlotIdx) + " %" + str(
                                        targetSlotIdx) + " %" + str(funckeyslotIdx) + newcommentPrefix))
            result.append(uvmIns)
        elif (constValue == "sortArray"):
            proto.InternConstantValue("table")
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABUP, ins,
                                    ("gettabup %" + str(targetSlotIdx) + " @" + str(
                                        envIndex) + " const " + "\"table\"" + newcommentPrefix))
            result.append(uvmIns)
            proto.InternConstantValue("sort")
            funckeyslotIdx = targetSlotIdx + 1
            MakeLoadConstInst(proto, ins, result, funckeyslotIdx, "sort", newcommentPrefix)
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABLE, ins,
                                    ("gettable %" + str(targetSlotIdx) + " %" + str(
                                        targetSlotIdx) + " %" + str(funckeyslotIdx) + newcommentPrefix))
            result.append(uvmIns)
        else:
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABUP, ins,
                                    ("gettabup %" + str(targetSlotIdx) + " @" + str(
                                        envIndex) + " const " + "\"" + constValue + "\"" + newcommentPrefix))
            result.append(uvmIns)
    elif (constValue in userdefined_methedsNames) or (constValue in wrapped_g_funcs):
        idx = proto.InternUpvalue(constValue)
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETUPVAL, ins,
                                ("getupval %" + str(targetSlotIdx) + " @" + str(idx) + newcommentPrefix))
        result.append(uvmIns)
    else:
        print("not suporte load gloabal:", constValue)
        exit(1)
    PushIntoEvalStackTopSlot(proto, targetSlotIdx, ins, result, newcommentPrefix);
    return result


def translate_LOAD_ATTR(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    constValue = proto.ConstantValues[proto.PycoConstsNum + ins.arg]
    if (constValue == "items"):  # get pairs -> get iter
        pairsFuncIdx = proto.tmp1StackTopSlotIndex
        envIndex = proto.InternUpvalue("ENV")
        tableIdx = pairsFuncIdx + 1
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABUP, ins,
                                ("gettabup %" + str(pairsFuncIdx) + " @" + str(
                                    envIndex) + " const " + "\"pairs\"" + newcommentPrefix))
        result.append(uvmIns)
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTOP, ins,
                                ("gettop %" + str(tableIdx) + newcommentPrefix))
        result.append(uvmIns)
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_CALL, ins,
                                ("call %" + str(pairsFuncIdx) + " 2 2" + newcommentPrefix))
        result.append(uvmIns)
        PushIntoEvalStackTopSlot(proto, pairsFuncIdx, ins, result, newcommentPrefix)
    else:
        keyidx = proto.tmp2StackTopSlotIndex
        MakeLoadConstInst(proto, ins, result, keyidx, constValue, newcommentPrefix);
        tabidx = proto.tmp1StackTopSlotIndex
        PopFromEvalStackTopSlot(proto, tabidx, ins, result, newcommentPrefix);
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABUP, ins,
                                ("gettable %" + str(tabidx) + " %" + str(
                                    tabidx) + " %" + str(keyidx) + newcommentPrefix))
        result.append(uvmIns)
        PushIntoEvalStackTopSlot(proto, tabidx, ins, result, newcommentPrefix);
    return result


# method 是成员函数
def translate_LOAD_METHOD(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    constValue = proto.ConstantValues[proto.PycoConstsNum + ins.arg]
    keyidx = proto.tmp2StackTopSlotIndex

    MakeLoadConstInst(proto, ins, result, keyidx, constValue, newcommentPrefix);
    tabidx = proto.tmp1StackTopSlotIndex
    methodIdx = proto.tmp3StackTopSlotIndex
    PopFromEvalStackTopSlot(proto, tabidx, ins, result, newcommentPrefix);
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABUP, ins,
                            ("gettable %" + str(methodIdx) + " %" + str(
                                tabidx) + " %" + str(keyidx) + newcommentPrefix))
    result.append(uvmIns)
    PushIntoEvalStackTopSlot(proto, methodIdx, ins, result, newcommentPrefix);
    #PushIntoEvalStackTopSlot(proto, tabidx, ins, result, newcommentPrefix); #push self
    return result


def translate_LOAD_CONST(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    constValue = proto.ConstantValues[ins.arg]
    MakeLoadConstInst(proto, ins, result, proto.tmp1StackTopSlotIndex, constValue, newcommentPrefix);
    PushIntoEvalStackTopSlot(proto, proto.tmp1StackTopSlotIndex, ins, result, newcommentPrefix);
    return result


def translate_STORE_FAST(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    slotidx = proto.Locvars[ins.arg].SlotIndex
    PopFromEvalStackTopSlot(proto, slotidx, ins, result, newcommentPrefix);
    return result


def translate_LOAD_FAST(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    slotidx = ins.arg
    PushIntoEvalStackTopSlot(proto, slotidx, ins, result, newcommentPrefix);
    return result


# 限制只有1个返回值
def translate_CALL_FUNCTION(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    argcount = ins.arg
    if (argcount >= 256):
        print("error, not support call function by identify argName")
        exit(1)
    funcidx = proto.tmp1StackTopSlotIndex
    slotidx = funcidx + argcount
    for i in range(0, argcount):
        PopFromEvalStackTopSlot(proto, slotidx, ins, result, newcommentPrefix)
        slotidx = slotidx - 1
    PopFromEvalStackTopSlot(proto, funcidx, ins, result, newcommentPrefix)
    returncount = 1
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_CALL, ins,
                            ("call %" + str(funcidx) + " " + str(argcount + 1) + " " + str(
                                returncount + 1) + newcommentPrefix))
    result.append(uvmIns)
    PushIntoEvalStackTopSlot(proto, funcidx, ins, result, newcommentPrefix)  # 返回值push
    return result

def translate_CALL_METHOD(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    argcount = ins.arg
    if (argcount >= 256):
        print("error, not support call function by identify argName")
        exit(1)
    funcidx = proto.tmp1StackTopSlotIndex
    #selfidx = funcidx+1
    slotidx = funcidx + argcount
    for i in range(0, argcount):
        PopFromEvalStackTopSlot(proto, slotidx, ins, result, newcommentPrefix)
        slotidx = slotidx - 1
    #PopFromEvalStackTopSlot(proto, selfidx, ins, result, newcommentPrefix)
    PopFromEvalStackTopSlot(proto, funcidx, ins, result, newcommentPrefix)
    returncount = 1
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_CALL, ins,
                            ("call %" + str(funcidx) + " " + str(argcount + 1) + " " + str(
                                returncount + 1) + newcommentPrefix))
    result.append(uvmIns)
    PushIntoEvalStackTopSlot(proto, funcidx, ins, result, newcommentPrefix)  # 返回值push
    return result


def translate_STORE_SUBSCR(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    tabidx = proto.tmp1StackTopSlotIndex
    keyidx = tabidx + 1
    validx = keyidx + 1
    PopFromEvalStackTopSlot(proto, keyidx, ins, result, newcommentPrefix)
    PopFromEvalStackTopSlot(proto, tabidx, ins, result, newcommentPrefix)
    PopFromEvalStackTopSlot(proto, validx, ins, result, newcommentPrefix)

    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_SETTABLE, ins,
                            ("settable %" + str(tabidx) + " %" + str(keyidx) + " %" + str(
                                validx) + newcommentPrefix))
    result.append(uvmIns)
    return result


# STORE_ATTR(namei)   Implements TOS.name = TOS1, where namei is the index of name in co_names.
def translate_STORE_ATTR(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    tabidx = proto.tmp1StackTopSlotIndex
    keyidx = tabidx + 1
    validx = keyidx + 1
    constValue = proto.ConstantValues[proto.PycoConstsNum + ins.arg]  # in co_names
    PopFromEvalStackTopSlot(proto, tabidx, ins, result, newcommentPrefix)
    PopFromEvalStackTopSlot(proto, validx, ins, result, newcommentPrefix)
    MakeLoadConstInst(proto, ins, result, keyidx, constValue, newcommentPrefix);

    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_SETTABLE, ins,
                            ("settable %" + str(tabidx) + " %" + str(keyidx) + " %" + str(
                                validx) + newcommentPrefix))
    result.append(uvmIns)
    return result


def translate_STORE_MAP(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    tabidx = proto.tmp1StackTopSlotIndex
    keyidx = tabidx + 1
    validx = keyidx + 1
    PopFromEvalStackTopSlot(proto, keyidx, ins, result, newcommentPrefix)
    PopFromEvalStackTopSlot(proto, validx, ins, result, newcommentPrefix)
    PopFromEvalStackTopSlot(proto, tabidx, ins, result, newcommentPrefix)
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_SETTABLE, ins,
                            ("settable %" + str(tabidx) + " %" + str(keyidx) + " %" + str(
                                validx) + newcommentPrefix))
    result.append(uvmIns)
    PushIntoEvalStackTopSlot(proto, tabidx, ins, result, newcommentPrefix)  # leave table
    return result


def translate_DELETE_SUBSCR(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    tabidx = proto.tmp1StackTopSlotIndex
    keyidx = tabidx + 1
    PopFromEvalStackTopSlot(proto, keyidx, ins, result, newcommentPrefix)
    PopFromEvalStackTopSlot(proto, tabidx, ins, result, newcommentPrefix)
    validx = keyidx + 1
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_LOADNIL, ins,
                            ("loadnil %" + str(validx) + " 0" + newcommentPrefix))
    result.append(uvmIns)
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_SETTABLE, ins,
                            ("settable %" + str(tabidx) + " %" + str(keyidx) + " %" + str(
                                validx) + newcommentPrefix))
    result.append(uvmIns)
    return result


def translate_JUMP_FORWARD(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    jmpdelta = ins.arg
    if jmpdelta > 0:
        jmplabel = proto.Name + "_" + ins.opname + str(ins.offset)
        jmpPos = jmpdelta + pyoplen + ins.offset
        if (jmpPos in proto.NeededLocationsMap):
            jmplabel = proto.NeededLocationsMap[jmpPos]
        proto.NeededLocationsMap[jmpPos] = jmplabel
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_JMP, ins,
                                ("jmp 1 $" + jmplabel + newcommentPrefix))
        result.append(uvmIns)
    return result


def translate_POP_JUMP_IF_XX(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    jmpPos = ins.arg
    validx = proto.tmp1StackTopSlotIndex
    PopFromEvalStackTopSlot(proto, validx, ins, result, newcommentPrefix)
    if (ins.opname == "POP_JUMP_IF_FALSE"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_TEST, ins,
                                ("test %" + str(
                                    validx) + " 0" + newcommentPrefix))  # test  if not (R(A)<=>C) then PC++   如果不等于false 则PC++ 跳过下一条指令
    else:
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_TEST, ins,
                                ("test %" + str(
                                    validx) + " 1" + newcommentPrefix))  # test  if not (R(A)<=>C) then PC++   如果不等于true 则PC++ 跳过下一条指令
    result.append(uvmIns)
    jmplabel = proto.Name + "_" + ins.opname + str(ins.offset)
    if (jmpPos in proto.NeededLocationsMap):
        jmplabel = proto.NeededLocationsMap[jmpPos]
    proto.NeededLocationsMap[jmpPos] = jmplabel
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_JMP, ins,
                            ("jmp 1 $" + jmplabel + newcommentPrefix))
    result.append(uvmIns)
    return result


def translate_JUMP_IF_XX_OR_POP(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    jmpPos = ins.arg
    validx = proto.tmp1StackTopSlotIndex
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTOP, ins, ("gettop %" + str(validx) + newcommentPrefix))
    result.append(uvmIns)
    if (ins.opname == "JUMP_IF_FALSE_OR_POP"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_TEST, ins,
                                ("test %" + str(
                                    validx) + " 0" + newcommentPrefix))  # test  if not (R(A)<=>C) then PC++   如果不等于false 则PC++ 跳过下一条指令
    else:  # JUMP_IF_FALSE_OR_POP
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_TEST, ins,
                                ("test %" + str(
                                    validx) + " 1" + newcommentPrefix))  # test  if not (R(A)<=>C) then PC++   如果不等于true 则PC++ 跳过下一条指令
    result.append(uvmIns)
    jmplabel = proto.Name + "_" + ins.opname + str(ins.offset)
    if (jmpPos in proto.NeededLocationsMap):
        jmplabel = proto.NeededLocationsMap[jmpPos]
    proto.NeededLocationsMap[jmpPos] = jmplabel
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_JMP, ins,
                            ("jmp 1 $" + jmplabel + newcommentPrefix))
    result.append(uvmIns)
    PopFromEvalStackTopSlot(proto, validx, ins, result, newcommentPrefix)
    return result


def translate_JUMP_ABSOLUTE(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    jmpPos = ins.arg
    jmplabel = proto.Name + "_" + ins.opname + str(ins.offset)
    if (jmpPos in proto.NeededLocationsMap):
        jmplabel = proto.NeededLocationsMap[jmpPos]
    proto.NeededLocationsMap[jmpPos] = jmplabel
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_JMP, ins,
                            ("jmp 1 $" + jmplabel + newcommentPrefix))
    result.append(uvmIns)
    return result


def translate_BUILD_LIST(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    listcount = ins.arg
    n = ins.arg
    tableslotidx = proto.tmp1StackTopSlotIndex
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_NEWTABLE, ins,
                            ("newtable %" + str(tableslotidx) + " 0 0" + newcommentPrefix))
    result.append(uvmIns)

    while n > 0:
        slotidx = tableslotidx + n
        if (slotidx > proto.tmpMaxStackTopSlotIndex):
            print("exceed tmpMaxStackTopSlotIndex,too many items")
            exit(1)
        PopFromEvalStackTopSlot(proto, slotidx, ins, result, newcommentPrefix)
        n = n - 1

    if (listcount > 0):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_SETLIST, ins,
                                ("setlist %" + str(tableslotidx) + " " + str(listcount) + " 1" + newcommentPrefix))
    result.append(uvmIns)
    PushIntoEvalStackTopSlot(proto, tableslotidx, ins, result, newcommentPrefix)
    return result


def translate_BUILD_MAP(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    n = ins.arg
    tableslotidx = proto.tmp1StackTopSlotIndex
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_NEWTABLE, ins,
                            ("newtable %" + str(tableslotidx) + " 0 0" + newcommentPrefix))
    result.append(uvmIns)
    PushIntoEvalStackTopSlot(proto, tableslotidx, ins, result, newcommentPrefix)
    return result


def translate_UNPACK_SEQUENCE(proto, ins):
    result = []
    num = ins.arg
    tableslotidx = proto.tmpMaxStackTopSlotIndex
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname

    PopFromEvalStackTopSlot(proto, tableslotidx, ins, result, newcommentPrefix)

    validx = proto.tmp1StackTopSlotIndex
    keyidx = proto.tmp2StackTopSlotIndex
    key1idx = proto.tmp3StackTopSlotIndex
    cons1 = proto.InternConstantValue(1)
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_LOADK, ins,
                            ("loadk %" + str(key1idx) + " const 1" + newcommentPrefix))
    result.append(uvmIns)
    for i in range(0, num):
        if (i == 0):
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_MOVE, ins,
                                    ("move %" + str(keyidx) + " %" + str(key1idx) + newcommentPrefix))
            result.append(uvmIns)
        if (i > 0):
            uvmIns = UvmInstruction(UvmOpCodeEnum.OP_ADD, ins,
                                    ("add %" + str(keyidx) + " %" + str(keyidx) + " %" + str(
                                        key1idx) + newcommentPrefix))
            result.append(uvmIns)

        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABLE, ins,
                                ("gettable %" + str(validx) + " %" + str(tableslotidx) + " %" + str(
                                    keyidx) + newcommentPrefix))
        result.append(uvmIns)
        PushIntoEvalStackTopSlot(proto, validx, ins, result, newcommentPrefix)
    return result


def translate_POP_TOP(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    slotidx = proto.tmp1StackTopSlotIndex
    PopFromEvalStackTopSlot(proto, slotidx, ins, result, newcommentPrefix);
    return result


def translate_BINARY_ADD(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    slotidx1 = proto.tmp2StackTopSlotIndex
    slotidx2 = slotidx1 + 1
    tmpslot1 = slotidx1 + 2
    tmpslot2 = slotidx1 + 3
    PopFromEvalStackTopSlot(proto, slotidx2, ins, result, newcommentPrefix)
    PopFromEvalStackTopSlot(proto, slotidx1, ins, result, newcommentPrefix)
    resultidx = proto.tmp1StackTopSlotIndex

    proto.InternConstantValue("type")
    envIndex = proto.InternUpvalue("ENV")
    funcidx = tmpslot1
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABUP, ins,
                            ("gettabup %" + str(funcidx) + " @" + str(
                                envIndex) + " const \"type\"" + newcommentPrefix))
    result.append(uvmIns)
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_MOVE, ins,
                            ("move %" + str(tmpslot2) + " %" + str(slotidx1) + newcommentPrefix))
    result.append(uvmIns)
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_CALL, ins,
                            ("call %" + str(funcidx) + " 2 2" + newcommentPrefix))
    result.append(uvmIns)
    # check type if is string  use concat
    typeslotidx = funcidx
    proto.InternConstantValue("string")
    MakeLoadConstInst(proto, ins, result, tmpslot2, "string", newcommentPrefix);
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_EQ, ins,
                            ("eq 1 %" + str(typeslotidx) + " %" + str(tmpslot2) + newcommentPrefix))
    result.append(uvmIns)
    # jmp to concat
    concatLabel = proto.Name + "_" + ins.opname + str(ins.offset) + "_concat"
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_JMP, ins, ("jmp 1 $" + concatLabel + newcommentPrefix))
    result.append(uvmIns)
    # jmp to add
    addLabel = proto.Name + "_" + ins.opname + str(ins.offset) + "_add"
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_JMP, ins, ("jmp 1 $" + addLabel + newcommentPrefix))
    result.append(uvmIns)
    # concat
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_CONCAT, ins,
                            ("concat %" + str(resultidx) + " %" + str(slotidx1) + " %" + str(
                                slotidx2) + newcommentPrefix))
    uvmIns.HasLocationLabel = True
    uvmIns.label = concatLabel
    result.append(uvmIns)

    # jmp out
    outlabel = proto.Name + "_" + ins.opname + str(ins.offset) + "_out"
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_JMP, ins,
                            ("jmp 1 $" + outlabel + newcommentPrefix))
    result.append(uvmIns)
    # add
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_ADD, ins,
                            ("add %" + str(resultidx) + " %" + str(slotidx1) + " %" + str(
                                slotidx2) + newcommentPrefix))
    uvmIns.HasLocationLabel = True
    uvmIns.label = addLabel
    result.append(uvmIns)

    # push into eval stack
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_PUSH, ins, ("push %" + str(resultidx) + newcommentPrefix))
    uvmIns.HasLocationLabel = True
    uvmIns.label = outlabel
    result.append(uvmIns)

    return result


def translate_COMPARE_OP(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    cmpOpName = dis_to_instructions.cmp_op[ins.arg]
    result = []
    slotidx1 = proto.tmp2StackTopSlotIndex
    slotidx2 = slotidx1 + 1
    PopFromEvalStackTopSlot(proto, slotidx2, ins, result, newcommentPrefix)
    PopFromEvalStackTopSlot(proto, slotidx1, ins, result, newcommentPrefix)
    resultidx = proto.tmp1StackTopSlotIndex
    if (cmpOpName == "<"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_LT, ins,
                                ("lt 0 %" + str(slotidx1) + " %" + str(slotidx2) + newcommentPrefix))  # if <  pc++
        result.append(uvmIns)
    elif (cmpOpName == "<="):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_LT, ins,
                                ("lt 1 %" + str(slotidx2) + " %" + str(slotidx1) + newcommentPrefix))  # if <=  pc++
        result.append(uvmIns)
    elif (cmpOpName == ">="):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_LT, ins,
                                ("lt 1 %" + str(slotidx1) + " %" + str(slotidx2) + newcommentPrefix))  # if <=  pc++
        result.append(uvmIns)
    elif (cmpOpName == ">"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_LT, ins,
                                ("lt 0 %" + str(slotidx2) + " %" + str(slotidx1) + newcommentPrefix))  # if >  pc++
        result.append(uvmIns)
    elif (cmpOpName == "=="):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_EQ, ins,
                                ("eq 0 %" + str(slotidx1) + " %" + str(slotidx2) + newcommentPrefix))  # if == pc++
        result.append(uvmIns)
    elif (cmpOpName == "!="):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_EQ, ins,
                                ("eq 1 %" + str(slotidx1) + " %" + str(slotidx2) + newcommentPrefix))  # if == pc++
        result.append(uvmIns)
    else:
        print("error not support:" + cmpOpName)
        exit(1)

    # jmp to load false
    falseLabel = proto.Name + "_" + ins.opname + str(ins.offset) + "_false"
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_JMP, ins, ("jmp 1 $" + falseLabel + newcommentPrefix))
    result.append(uvmIns)

    # jmp to load true
    trueLabel = proto.Name + "_" + ins.opname + str(ins.offset) + "_true"
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_JMP, ins, ("jmp 1 $" + trueLabel + newcommentPrefix))
    result.append(uvmIns)

    # load false
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_LOADBOOL, ins,
                            ("loadbool %" + str(resultidx) + " 0 0" + newcommentPrefix))
    uvmIns.label = falseLabel
    uvmIns.HasLocationLabel = True
    result.append(uvmIns)
    labelout = proto.Name + "_" + ins.opname + str(ins.offset) + "_out"
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_JMP, ins, ("jmp 1 $" + labelout + newcommentPrefix))
    result.append(uvmIns)

    # load true
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_LOADBOOL, ins,
                            ("loadbool %" + str(resultidx) + " 1 0" + newcommentPrefix))
    uvmIns.label = trueLabel
    uvmIns.HasLocationLabel = True
    result.append(uvmIns)

    PushIntoEvalStackTopSlot(proto, resultidx, ins, result, newcommentPrefix)
    result[len(result) - 1].label = labelout
    result[len(result) - 1].HasLocationLabel = True
    return result


def translate_UNARY_XX(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    slotidx1 = proto.tmp2StackTopSlotIndex
    PopFromEvalStackTopSlot(proto, slotidx1, ins, result, newcommentPrefix)

    resultidx = proto.tmp1StackTopSlotIndex
    if (ins.opname == "UNARY_NEGATIVE"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_UNM, ins,
                                ("unm %" + str(resultidx) + " %" + str(slotidx1) + newcommentPrefix))
    elif (ins.opname == "UNARY_NOT"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_NOT, ins,
                                ("not %" + str(resultidx) + " %" + str(slotidx1) + newcommentPrefix))
    elif (ins.opname == "UNARY_INVERT"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_BNOT, ins,
                                ("bnot %" + str(resultidx) + " %" + str(slotidx1) + newcommentPrefix))
    else:
        print("error not support:" + ins.opname)
        exit(1)
    result.append(uvmIns)
    PushIntoEvalStackTopSlot(proto, resultidx, ins, result, newcommentPrefix)
    return result


def translate_BINARY_CACULATE(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    slotidx1 = proto.tmp2StackTopSlotIndex
    slotidx2 = slotidx1 + 1

    PopFromEvalStackTopSlot(proto, slotidx2, ins, result, newcommentPrefix)
    PopFromEvalStackTopSlot(proto, slotidx1, ins, result, newcommentPrefix)
    resultidx = proto.tmp1StackTopSlotIndex

    if (ins.opname == "BINARY_POWER") or (ins.opname == "INPLACE_POWER"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_POW, ins,
                                ("pow %" + str(resultidx) + " %" + str(slotidx1) + " %" + str(
                                    slotidx2) + newcommentPrefix))
    elif (ins.opname == "BINARY_MULTIPLY") or (ins.opname == "INPLACE_MULTIPLY"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_MUL, ins,
                                ("mul %" + str(resultidx) + " %" + str(slotidx1) + " %" + str(
                                    slotidx2) + newcommentPrefix))
    elif (ins.opname == "BINARY_MODULO") or (ins.opname == "INPLACE_MODULO"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_MOD, ins,
                                ("mod %" + str(resultidx) + " %" + str(slotidx1) + " %" + str(
                                    slotidx2) + newcommentPrefix))
    elif (ins.opname == "BINARY_SUBTRACT") or (ins.opname == "INPLACE_SUBTRACT"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_SUB, ins,
                                ("sub %" + str(resultidx) + " %" + str(slotidx1) + " %" + str(
                                    slotidx2) + newcommentPrefix))
    elif (ins.opname == "BINARY_AND") or (ins.opname == "INPLACE_AND"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_BAND, ins,
                                ("band %" + str(resultidx) + " %" + str(slotidx1) + " %" + str(
                                    slotidx2) + newcommentPrefix))
    elif (ins.opname == "BINARY_OR") or (ins.opname == "INPLACE_OR"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_BOR, ins,
                                ("bor %" + str(resultidx) + " %" + str(slotidx1) + " %" + str(
                                    slotidx2) + newcommentPrefix))
    elif (ins.opname == "BINARY_RSHIFT") or (ins.opname == "INPLACE_RSHIFT"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_SHL, ins,
                                ("shl %" + str(resultidx) + " %" + str(slotidx1) + " %" + str(
                                    slotidx2) + newcommentPrefix))
    elif (ins.opname == "BINARY_RSHIFT") or (ins.opname == "INPLACE_RSHIFT"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_SHR, ins,
                                ("shr %" + str(resultidx) + " %" + str(slotidx1) + " %" + str(
                                    slotidx2) + newcommentPrefix))
    elif (ins.opname == "BINARY_XOR") or (ins.opname == "INPLACE_XOR"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_BXOR, ins,
                                ("bxor %" + str(resultidx) + " %" + str(slotidx1) + " %" + str(
                                    slotidx2) + newcommentPrefix))
    elif (ins.opname == "BINARY_DIVIDE") or (
            ins.opname == "INPLACE_DIVIDE") or (ins.opname == "BINARY_TRUE_DIVIDE"):  # todo check type if all integer , apply idiv
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_DIV, ins,
                                ("div %" + str(resultidx) + " %" + str(slotidx1) + " %" + str(
                                    slotidx2) + newcommentPrefix))
    elif (ins.opname == "BINARY_FLOOR_DIVIDE") or (ins.opname == "INPLACE_FLOOR_DIVIDE"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_IDIV, ins,
                                ("idiv %" + str(resultidx) + " %" + str(slotidx1) + " %" + str(
                                    slotidx2) + newcommentPrefix))
    else:
        print("error not support:" + ins.opname)
        exit(1)
    result.append(uvmIns)
    PushIntoEvalStackTopSlot(proto, resultidx, ins, result, newcommentPrefix)
    return result


def translate_PRINT_ITEM(proto, ins):
    result = []
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    proto.InternConstantValue("print")
    envIndex = proto.InternUpvalue("ENV")
    printfuncidx = proto.tmp1StackTopSlotIndex
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_GETTABUP, ins,
                            ("gettabup %" + str(printfuncidx) + " @" + str(
                                envIndex) + " const \"print\"" + newcommentPrefix))
    result.append(uvmIns)
    validx = proto.tmp2StackTopSlotIndex
    PopFromEvalStackTopSlot(proto, validx, ins, result, newcommentPrefix)

    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_CALL, ins,
                            ("call %" + str(printfuncidx) + " 2 1" + newcommentPrefix))
    result.append(uvmIns)
    return result


# push block onto block stack   no uvminss
def translate_SETUP_LOOP(proto, ins):
    result = []
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    jmpdelta = ins.arg

    jmplabel_end = proto.Name + "_" + ins.opname + str(ins.offset) + "_loop_end"
    blockStartPos = pyoplen + ins.offset
    blockEndPos = jmpdelta + blockStartPos

    if (blockEndPos in proto.NeededLocationsMap):
        jmplabel_end = proto.NeededLocationsMap[blockEndPos]
    else:
        proto.NeededLocationsMap[blockEndPos] = jmplabel_end
    proto.blockStack.append(blockEndPos)

    return result


# pop block from block stack no inss
def translate_POP_BLOCK(proto, ins):
    result = []
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname + " ;as jmp target"
    if len(proto.blockStack) == 0:
        print("error pop block")
        exit(1)
    proto.blockStack.pop()

    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_MOVE, ins,
                            ("move %" + str(proto.tmpMaxStackTopSlotIndex) + "  %" + str(
                                proto.tmpMaxStackTopSlotIndex) + newcommentPrefix))
    result.append(uvmIns)

    return result


# pop block from block stack and jmp
def translate_BREAK_LOOP(proto, ins):
    result = []
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname

    count = len(proto.blockStack)
    if (count <= 0):
        print("error when BREAK_LOOP, block stack empty ")
        exit(1)

    jmpPos = proto.blockStack[count - 1]

    if jmpPos not in proto.NeededLocationsMap:
        print("error  BREAK_LOOP")
        exit(1)
    labelout = proto.NeededLocationsMap[jmpPos]
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_JMP, ins, ("jmp 1 $" + labelout + newcommentPrefix))
    result.append(uvmIns)
    return result


def translate_DO_NOTHING(proto, ins):
    return []


def translate_RETURN_VALUE(proto, ins):
    newcommentPrefix = ";L" + str(ins.source_line) + ";" + ins.opname
    result = []
    slotidx = proto.tmp1StackTopSlotIndex
    PopFromEvalStackTopSlot(proto, slotidx, ins, result, newcommentPrefix);
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_RETURN, ins,
                            ("return %" + str(slotidx) + " 2" + newcommentPrefix))
    result.append(uvmIns)
    return result


def translate_DEFAULT(proto, ins):
    print("not support ins:" + ins.opname)
    exit(1)
    return []


switchDic = {"LOAD_CONST": translate_LOAD_CONST,
             "STORE_FAST": translate_STORE_FAST,
             "BUILD_LIST": translate_BUILD_LIST,
             "BUILD_TUPLE": translate_BUILD_LIST,
             "LOAD_FAST": translate_LOAD_FAST,

             "LOAD_METHOD":translate_LOAD_METHOD,
            "CALL_METHOD": translate_CALL_METHOD,
             "CALL_FUNCTION": translate_CALL_FUNCTION,
             "LOAD_ATTR": translate_LOAD_ATTR,
             "LOAD_GLOBAL": translate_LOAD_GLOBAL,
             "POP_TOP": translate_POP_TOP,
             "RETURN_VALUE": translate_RETURN_VALUE,
             "STORE_SUBSCR": translate_STORE_SUBSCR,
             "DELETE_SUBSCR": translate_DELETE_SUBSCR,
             "UNPACK_SEQUENCE": translate_UNPACK_SEQUENCE,
             "BINARY_SUBSCR": translate_BINARY_SUBSCR,

             "BINARY_ADD": translate_BINARY_ADD,
             "BINARY_MULTIPLY": translate_BINARY_CACULATE,
             "BINARY_POWER": translate_BINARY_CACULATE,
             "BINARY_MODULO": translate_BINARY_CACULATE,
             "BINARY_SUBTRACT": translate_BINARY_CACULATE,
             "BINARY_OR": translate_BINARY_CACULATE,
             "BINARY_AND": translate_BINARY_CACULATE,
             "BINARY_LSHIFT": translate_BINARY_CACULATE,
             "BINARY_RSHIFT": translate_BINARY_CACULATE,
             "BINARY_XOR": translate_BINARY_CACULATE,
             "BINARY_DIVIDE": translate_BINARY_CACULATE,
            "BINARY_TRUE_DIVIDE": translate_BINARY_CACULATE,
             "BINARY_FLOOR_DIVIDE": translate_BINARY_CACULATE,

             "INPLACE_POWER": translate_BINARY_CACULATE,
             "INPLACE_MULTIPLY": translate_BINARY_CACULATE,
             "INPLACE_DIVIDE": translate_BINARY_CACULATE,
             "INPLACE_FLOOR_DIVIDE": translate_BINARY_CACULATE,
             "INPLACE_MODULO": translate_BINARY_CACULATE,
             "INPLACE_ADD": translate_BINARY_ADD,
             "INPLACE_SUBTRACT": translate_BINARY_CACULATE,
             "INPLACE_LSHIFT": translate_BINARY_CACULATE,
             "INPLACE_RSHIFT": translate_BINARY_CACULATE,
             "INPLACE_AND": translate_BINARY_CACULATE,
             "INPLACE_XOR": translate_BINARY_CACULATE,
             "INPLACE_OR": translate_BINARY_CACULATE,

             "PRINT_ITEM": translate_PRINT_ITEM,
             "PRINT_NEWLINE": translate_DO_NOTHING,
             "BUILD_MAP": translate_BUILD_MAP,
             "STORE_MAP": translate_STORE_MAP,
             "SETUP_LOOP": translate_SETUP_LOOP,
             "POP_BLOCK": translate_POP_BLOCK,
             "BREAK_LOOP": translate_BREAK_LOOP,
             "POP_JUMP_IF_FALSE": translate_POP_JUMP_IF_XX,
             "POP_JUMP_IF_TRUE": translate_POP_JUMP_IF_XX,
             "JUMP_IF_TRUE_OR_POP": translate_JUMP_IF_XX_OR_POP,
             "JUMP_IF_FALSE_OR_POP": translate_JUMP_IF_XX_OR_POP,
             "JUMP_ABSOLUTE": translate_JUMP_ABSOLUTE,
             "JUMP_FORWARD": translate_JUMP_FORWARD,
             "UNARY_NOT": translate_UNARY_XX,
             "UNARY_NEGATIVE": translate_UNARY_XX,
             "UNARY_INVERT": translate_UNARY_XX,
             "STORE_ATTR": translate_STORE_ATTR,
             "COMPARE_OP": translate_COMPARE_OP,
             "EXTENDED_ARG":translate_DO_NOTHING,
             }
'''

             "BINARY_DIVIDE": translate_BINARY_DIVIDE,
             "BINARY_TRUE_DIVIDE": translate_BINARY_DIVIDE,
             "BINARY_FLOOR_DIVIDE": translate_BINARY_FLOOR_DIVIDE,
             "BINARY_SUBTRACT": translate_BINARY_SUBTRACT,
             "BINARY_LSHIFT": translate_BINARY_LSHIFT,
             "BINARY_RSHIFT": translate_BINARY_RSHIFT,
             "BINARY_XOR": translate_BINARY_XOR,
             "BINARY_OR": translate_BINARY_OR,
             "INPLACE_POWER": translate_INPLACE_POWER,
             "INPLACE_MULTIPLY": translate_INPLACE_MULTIPLY,
             "INPLACE_FLOOR_DIVIDE": translate_INPLACE_FLOOR_DIVIDE,
             "INPLACE_MODULO": translate_INPLACE_MODULO,
             "INPLACE_ADD": translate_INPLACE_ADD,
             "INPLACE_SUBTRACT": translate_INPLACE_SUBTRACT,
             "INPLACE_LSHIFT": translate_INPLACE_LSHIFT,
             "INPLACE_RSHIFT": translate_INPLACE_RSHIFT,
             "INPLACE_AND": translate_INPLACE_AND,
             "INPLACE_XOR": translate_INPLACE_XOR,
             "INPLACE_OR": translate_INPLACE_OR,
'''


# STORE_ATTR  DELETE_ATTR
# STORE_NAME  DELETE_NAME
# STORE_GLOBAL  DELETE_GLOBAL
# LOAD_NAME

# IMPORT_NAME
# IMPORT_FROM


def translateIns(funcproto, inss):
    insIdx = 0
    for ins in inss:
        result = switchDic.get(ins.opname, translate_DEFAULT)(funcproto, ins)
        for item in result:
            funcproto.CodeInstructions.append(item)
        funcproto.pyInsToUvmInss.append((ins, result))
        insIdx = insIdx + 1


#################################################################################################

def generateDotUvms(TopProto, filename):
    with open(filename, 'w+') as f:
        printProtoUvms(TopProto, f, True)


def printProtoUvms(proto, f, isTop):
    if isTop:
        f.write(".upvalues 1\r\n")
    if (isinstance(proto, UvmProto)):
        f.write(".func " + proto.Name + " " + str(proto.MaxStackSize) + ' ' + str(proto.Numparams) + ' ' + str(
            len(proto.Locvars)) + '\r\n')

        f.write(".begin_const\r\n")
        for cons in proto.ConstantValues:
            f.write("\t")
            if cons == None:
                f.write("nil\r\n")
            elif type(cons) is str:
                valstr = cons
                if valstr.find("\"") >= 0:
                    valstr = valstr.replace("\"", '\\"')
                f.write("\"" + valstr + "\"\r\n")
            elif type(cons) is bool:
                val = "true"
                if cons == False:
                    val = "false"
                f.write(val + "\r\n")
            else:
                val = str(cons)
                f.write(val + "\r\n")
        f.write(".end_const\r\n")

        f.write(".begin_upvalue\r\n")
        for upvalue in proto.Upvalues:
            instack = "0"
            if (upvalue.Instack == True):
                instack = "1"
            f.write("\t" + instack + " " + str(upvalue.Idx) + " \"" + upvalue.Name + "\"" + "\r\n")
        f.write(".end_upvalue\r\n")

        f.write(".begin_local\r\n")
        sizeCodeStr = str(len(proto.CodeInstructions))
        for local in proto.Locvars:
            f.write("\t\"" + local.Name + "\" " + str(local.StartPc) + " " + sizeCodeStr + "\r\n")
        f.write(".end_local\r\n")

        f.write(".begin_code\r\n")
        for inst in proto.CodeInstructions:
            if inst.HasLocationLabel:
                f.write(inst.label + ":\r\n")
            f.write("\t" + inst.uvmAsmLine + "\r\n")
        f.write(".end_code\r\n")

        for subProto in proto.SubProtos:
            f.write("\r\n")
            printProtoUvms(subProto, f, False)


#################################################################################################

def translateClassType(r, parentProto, name):
    proto = UvmProto()
    proto.Name = name
    proto.isOfflineFunc = True
    proto.Parent = parentProto;
    proto.Numparams = 1
    tableSlot = 0
    newcommentPrefix = ""
    proto.AddInstructionLine(UvmOpCodeEnum.OP_NEWTABLE,
                             ("newtable %" + str(tableSlot) + " 0 0" + newcommentPrefix), None)
    tmp1Slot = len(r) + 1
    for k, v in r.items():
        subpro = translateContractMethodType(v, proto)
        if subpro == None:
            print("error subpro")
            exit(1)

        proto.ContractApiNames.append(subpro.Name)
        # proto.contractOfflineApiNames
        if subpro.isOfflineFunc==True:
            proto.ContractOfflineApiNames.append(subpro.Name)

        if (subpro.Numparams > 2):
            print("error , not support muti args")
            exit(1)
        elif (subpro.Numparams < 1):
            print("error , not support function:" + subpro.Name)
            exit(1)
        elif (subpro.Numparams == 2):
            subMethodapiArgs = [UvmTypeInfoEnum.LTI_STRING]
            proto.ContractApiArgsTypes[subpro.Name] = subMethodapiArgs
        elif (subpro.Numparams == 1):
            subMethodapiArgs = [UvmTypeInfoEnum.LTI_STRING]
            proto.ContractApiArgsTypes[subpro.Name] = []

        proto.InternConstantValue(subpro.Name)
        slotIndex = proto.Numparams + len(proto.SubProtos)
        proto.AddInstructionLine(UvmOpCodeEnum.OP_CLOSURE,
                                 ("closure %" + str(slotIndex) + " " + subpro.Name + newcommentPrefix), None)
        proto.InternConstantValue(subpro.Name)
        proto.AddInstructionLine(UvmOpCodeEnum.OP_LOADK, "loadk %" + str(tmp1Slot) + " const \"" + subpro.Name + "\"",
                                 None)
        proto.AddInstructionLine(UvmOpCodeEnum.OP_SETTABLE,
                                 "settable %" + str(tableSlot) + " %" + str(tmp1Slot) + " %" + str(slotIndex), None);
        proto.Locvars.append(UvmLocVar(subpro.Name, slotIndex))
        proto.SubProtos.append(subpro)

    proto.MaxStackSize = tmp1Slot + 1
    proto.AddInstructionLine(UvmOpCodeEnum.OP_RETURN, "return %" + str(tableSlot) + " 2", None)
    return proto

def generate_wrapped_proto(name,parentProto):
    funcproto = UvmProto()
    funcproto.Parent = parentProto

    funcproto.PycoConstsNum = len(funcproto.ConstantValues)

    locvar = UvmLocVar("contract_address", 0)
    funcproto.Locvars.append(locvar)
    locvar = UvmLocVar("api_name", 1)
    funcproto.Locvars.append(locvar)
    locvar = UvmLocVar("args", 2)
    funcproto.Locvars.append(locvar)

    funcproto.Numparams = 3
    funcproto.LineDefined = -1
    funcproto.LastLineDefined = -1

    funcproto.Name = name
    funcproto.isOfflineFunc = False

    if (name == "call_contract_api"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_CCALL, None,("ccall %0 2 2" ))
        funcproto.CodeInstructions.append(uvmIns)
    elif (name == "static_call_contract_api"):
        uvmIns = UvmInstruction(UvmOpCodeEnum.OP_CSTATICCALL, None, ("cstaticcall %0 2 2"))
        funcproto.CodeInstructions.append(uvmIns)
    else:
        print("not support wrap func:"+name)
        exit(1)
    uvmIns = UvmInstruction(UvmOpCodeEnum.OP_RETURN, None, ("return %0 2"))
    funcproto.CodeInstructions.append(uvmIns)
    funcproto.MaxStackSize = 3
    return funcproto


def translateMethod(coinfo,parentProto,funco):
    funcproto = UvmProto()
    funcproto.Parent = parentProto
    for cons in coinfo.co_consts:
        consval = cons
        funcproto.ConstantValues.append(consval)
    funcproto.PycoConstsNum = len(funcproto.ConstantValues)
    for attrName in coinfo.co_names:
        cons = attrName
        if (attrName == "None"):
            cons = None
        elif (attrName == "True"):
            cons = True
        elif (attrName == "False"):
            cons = False
        # elif type(attrName) is str:
        #   if attrName.find("\"")>=0:
        #      cons.replace("\"",'\\"')
        funcproto.ConstantValues.append(cons)
    i = 0
    for loc in coinfo.co_varnames:
        locvar = UvmLocVar(loc, i)
        i = i + 1
        funcproto.Locvars.append(locvar)
    funcproto.Numparams = coinfo.co_argcount
    funcproto.LineDefined = coinfo.co_firstlineno
    funcproto.LastLineDefined = -1

    funcproto.InternConstantValue(0)
    funcproto.InternConstantValue(1)

    tempSlotStartIdx = len(funcproto.Locvars)
    funcproto.tmp1StackTopSlotIndex = tempSlotStartIdx + 1
    funcproto.tmp2StackTopSlotIndex = tempSlotStartIdx + 2
    funcproto.tmp3StackTopSlotIndex = tempSlotStartIdx + 3
    funcproto.tmpMaxStackTopSlotIndex = funcproto.tmp1StackTopSlotIndex + 17

    realname = coinfo.co_name
    if realname.startswith("offline") and len(realname) > 7:
        realname = realname[7:]

    funcproto.Name = realname
    funcproto.isOfflineFunc = True

    translateIns(funcproto, funco)

    # 处理NeededLocationsMap，忽略empty lines
    locationkeys = sorted(funcproto.NeededLocationsMap.keys())
    count = len(funcproto.CodeInstructions)
    while (i < count):
        if len(locationkeys) <= 0:
            break
        if funcproto.CodeInstructions[i].insInpython is not None:
            rawpycodeidx = funcproto.CodeInstructions[i].insInpython.offset
            needloc = locationkeys[0]
            if rawpycodeidx < needloc:
                i = i + 1
                continue
            else:
                if (funcproto.CodeInstructions[i].HasLocationLabel):
                    print("already has label,can't assign again")
                    exit(1)
                funcproto.CodeInstructions[i].HasLocationLabel = True
                funcproto.CodeInstructions[i].label = funcproto.NeededLocationsMap[needloc]
                funcproto.NeededLocationsMap.pop(needloc)
                locationkeys.remove(needloc)

    if len(locationkeys) > 0:
        print("erro NeededLocationsMap")
        exit(1)

    # reduce
    if (len(funcproto.CodeInstructions) < 1):
        funcproto.AddInstructionLine(UvmOpCodeEnum.OP_RETURN, "return %0 1", None);

    funcproto.MaxStackSize = funcproto.tmpMaxStackTopSlotIndex + 2
    reduceProtoUvmInsts(funcproto)
    return funcproto


def translateToolMethodType(x, parentProto):
    funcinfo = x.__code__
    funco = dis_to_instructions.dis(x)

    if hasattr(funcinfo, '__code__'):
        coinfo = funcinfo.__code__
    else:
        coinfo = funcinfo

    return translateMethod(coinfo,parentProto,funco)

    for cons in coinfo.co_consts:
        funcproto.ConstantValues.append(cons)
    funcproto.PycoConstsNum = len(funcproto.ConstantValues)
    for attrName in coinfo.co_names:
        funcproto.ConstantValues.append(attrName)
    i = 0
    for loc in coinfo.co_varnames:
        locvar = UvmLocVar(loc, i)
        i = i + 1
        funcproto.Locvars.append(locvar)
    funcproto.Numparams = coinfo.co_argcount
    funcproto.LineDefined = coinfo.co_firstlineno
    funcproto.LastLineDefined = -1
    funcproto.Name = coinfo.co_name
    funcproto.MaxStackSize = coinfo.co_stacksize
    translateIns(funcproto, r)

    # 处理NeededLocationsMap，忽略empty lines
    locationkeys = sorted(funcproto.NeededLocationsMap.keys())
    count = len(funcproto.CodeInstructions)
    while (i < count):
        if len(locationkeys) <= 0:
            break
        if funcproto.CodeInstructions[i].insInpython is not None:
            rawpycodeidx = funcproto.CodeInstructions[i].insInpython.offset
            needloc = locationkeys[0]
            if rawpycodeidx < needloc:
                i = i + 1
                continue
            else:
                if (funcproto.CodeInstructions[i].HasLocationLabel):
                    print("already has label,can't assign again")
                    exit(1)
                funcproto.CodeInstructions[i].HasLocationLabel = True
                funcproto.CodeInstructions[i].label = funcproto.NeededLocationsMap[needloc]
                funcproto.NeededLocationsMap.pop(needloc)
                locationkeys.remove(needloc)

    if len(locationkeys) > 0:
        print("erro NeededLocationsMap")
        exit(1)

    reduceProtoUvmInsts(funcproto)
    return funcproto


def translateContractMethodType(v, parentProto):
    if 'funcinfo' in v:
        funcinfo = v['funcinfo']
        if isinstance(funcinfo, _have_code):
            if isinstance(funcinfo, staticmethod):
                print("not support staticmethod ")
                exit(1)

            if hasattr(funcinfo, '__code__'):
                coinfo = funcinfo.__code__
            else:
                coinfo = funcinfo
            return translateMethod(coinfo,parentProto,v['funccode'])
    return None


######################################################################################################


def reduceProtoUvmInsts(proto):
    print("begin reduce: proto name = " + proto.Name + " totalLines = " + str(len(proto.CodeInstructions)) + "\n")
    r = 1
    totalReduceLines = 0
    idx = 0
    while (r > 0):
        print("idx=" + str(idx) + " , reduce proto begin:" + proto.Name)
        r = reduceUvmInstsImp(proto)
        totalReduceLines += r
        idx += 1
    print("proto name = " + proto.Name + " totalReduceLines = " + str(totalReduceLines) + " , now totalLines = " + str(
        len(proto.CodeInstructions)) + "\n")


def reduceUvmInstsImp(proto):
    CodeInstructions = proto.CodeInstructions
    delIndexes = []
    modifyIndexes = []
    modifyUvmIns = []
    uvmJmpIns = []

    UvmInstCount = len(CodeInstructions)
    affectedSlot = ""
    uvmInsstr = ""
    commentIndex = -1
    commentPrefix = ""
    constStr = ""

    for gIndex in range(UvmInstCount):
        uvmIns = CodeInstructions[gIndex]
        uvmInsstr = uvmIns.uvmAsmLine;
        commentIndex = uvmInsstr.index(";");
        if (commentIndex >= 0):
            commentPrefix = "" + uvmInsstr[commentIndex:]
            uvmInsstr = uvmInsstr[0:commentIndex]
        else:
            commentPrefix = ""
        ss = uvmInsstr.split()
        opcode1 = CodeInstructions[gIndex].uvmOpCode
        if ((opcode1 == UvmOpCodeEnum.OP_PUSH) and (not CodeInstructions[gIndex].HasLocationLabel)):
            if (gIndex + 1 < UvmInstCount):
                ins2 = CodeInstructions[gIndex + 1]
                if ((ins2.uvmOpCode == UvmOpCodeEnum.OP_POP) and (not ins2.HasLocationLabel)):
                    ssCount = len(ss)
                    if ((ssCount == 2) and ss[1].startswith("%")):
                        affectedSlot = ss[1]
                    else:
                        affectedSlot = ""
                        constidx = uvmInsstr.index("const")
                        if (constidx >= 0):
                            constStr = uvmInsstr[constidx:]
                        else:
                            print("error ReduceUvmInsts,invalid uvm inst:" + uvmInsstr)
                            exit(1)

                    uvmInsstr2 = ins2.uvmAsmLine.strip()
                    commentIndex2 = uvmInsstr2.index(";")
                    if (commentIndex2 >= 0):
                        commentPrefix = commentPrefix + "," + uvmInsstr2[commentIndex2:]
                        uvmInsstr2 = uvmInsstr2[0:commentIndex2]

                    ss2 = uvmInsstr2.split()
                    targetSlot = ss2[1]
                    if (not targetSlot.startswith("%")):
                        print("error ReduceUvmInsts,invalid uvm inst:" + uvmInsstr)
                        exit(1)

                    if (affectedSlot.startswith("%")):
                        inst = UvmInstruction(UvmOpCodeEnum.OP_MOVE, uvmIns.insInpython,
                                              "move " + targetSlot + " " + affectedSlot + commentPrefix + ";pushpop slot")
                    elif (constStr.startswith("const ")):
                        inst = UvmInstruction(UvmOpCodeEnum.OP_LOADK, uvmIns.insInpython,
                                              "loadk " + targetSlot + " " + constStr + commentPrefix + ";pushpop slot")
                    else:
                        print("error ReduceUvmInsts,invalid uvm inst:" + uvmInsstr)
                        exit(1)

                    delIndexes.append(gIndex)
                    modifyIndexes.append(gIndex + 1)
                    modifyUvmIns.append(inst)

    delcount = len(delIndexes)
    for mi in modifyIndexes:
        proto.CodeInstructions[mi] = modifyUvmIns[modifyIndexes.index(mi)]

    if (delcount > 0):
        for j in reversed(range(delcount)):
            instr = proto.CodeInstructions[delIndexes[j]].uvmAsmLine
            del proto.CodeInstructions[delIndexes[j]]

    print("reduce codeslines =" + str(delcount) + "\n")
    return delcount


#################################################################################################
from pathlib import Path
py_version_major = 3
py_version_minor = 7
def main(argv):
    path = Path.cwd()
    print("cur path:",path)
    print("current python version:", sys.version)
    if(sys.version_info.major <py_version_major) or ( (sys.version_info.major==py_version_major) and (sys.version_info.minor <py_version_minor)):
        print("need python version >= "+str(py_version_major)+"."+str(py_version_minor))
        exit(1)

    if len(argv) < 2:
        print("error,need pass 1 arg :source_contract_filepath")
        print("for example :E:\pythonProjects\py2uvms\py_contract_demo.py")
        exit(1)
    sourcePath = Path(argv[1])

    if not sourcePath.exists():
        print("error,arg source_filepath is not exist ")
        exit(1)
    if(sourcePath.suffix != ".py"):
        print("error,arg source_filepath is not py , "+sourcePath.suffix)
        exit(1)

    sourcePathDir =sourcePath.parent
    sourcePathDirStr = str(sourcePathDir)
    sys.path.append(sourcePathDirStr)

    contractModname = sourcePath.stem

    pyContract = __import__(contractModname)

    # pyContract = compile('', argv[1], 'eval')
    # print("compile done")
    print("#############################")

    topProto = UvmProto()
    contractStoragePropertiesTypes = {}
    if hasattr(pyContract, '__dict__'):
        dictresult = {}
        ditems = pyContract.__dict__.items()
        filepath = pyContract.__file__

        if not hasattr(pyContract, 'events'):
            print("need define events list in contract")
            exit(1)

        eventsNames = pyContract.events

        if (not hasattr(pyContract, 'Storage')) or (not hasattr(pyContract.Storage, '__init__')):
            print("need define class Storage in contract")
            exit(1)
        scc = pyContract.Storage.__init__.__code__

        stor_names = scc.co_names
        sto = pyContract.Storage()
        for sn in stor_names:
            if hasattr(sto, sn):
                stotype = 0
                v = getattr(sto, sn)
                if type(v) is str:
                    print(sn, "str")
                    stotype = StorageValueTypes.storage_value_string
                elif type(v) is int:
                    print(sn, "int")
                    stotype = StorageValueTypes.storage_value_int
                elif isinstance(v, UvmArray):
                    print(sn, "UvmArray")
                    stotype = StorageValueTypes.storage_value_unknown_array
                elif isinstance(v, UvmMap):
                    print(sn, "UvmMap")
                    stotype = StorageValueTypes.storage_value_unknown_table
                else:
                    print("error not support storage type:" + str(type(v)))
                contractStoragePropertiesTypes[sn] = stotype

        for name, x in ditems:
            # if isinstance(type(x),UvmContract):
            if str(type(x)) == "<class 'function'>" and hasattr(x, '__code__'):
                funcinfo = x.__code__
                if (((funcinfo.co_filename + "c") != filepath) and (funcinfo.co_filename != filepath)):
                    print("don't translate method: " + funcinfo.co_name + " from " + funcinfo.co_filename)
                    continue
                if(name in wrapped_g_funcs):
                    print("can't define method name :"+name)
                    exit(1)
                userdefined_methedsNames.append(name)
                userdefined_metheds.append(x)

        # top proto
        topProto.InternUpvalue("ENV")
        topProto.Numparams = 0;
        topProto.Name = "main"
        tableSlot = 0
        tempslot = len(userdefined_metheds) + 1
        newcommentPrefix = ";topmain"

        for x in userdefined_metheds:
            utilProto = translateToolMethodType(x, topProto)
            topProto.InternConstantValue(utilProto.Name);
            slotIndex = topProto.Numparams + len(topProto.SubProtos)
            topProto.AddInstructionLine(UvmOpCodeEnum.OP_CLOSURE, "closure %" + str(slotIndex) + " " + utilProto.Name,
                                        None);
            subProtoName = utilProto.Name;
            topProto.Locvars.append(UvmLocVar(subProtoName, slotIndex))
            topProto.SubProtos.append(utilProto)

        for func_name in wrapped_g_funcs:
            utilProto = generate_wrapped_proto(func_name,topProto)
            topProto.InternConstantValue(utilProto.Name);
            slotIndex = topProto.Numparams + len(topProto.SubProtos)
            topProto.AddInstructionLine(UvmOpCodeEnum.OP_CLOSURE, "closure %" + str(slotIndex) + " " + utilProto.Name,
                                        None);
            subProtoName = utilProto.Name;
            topProto.Locvars.append(UvmLocVar(subProtoName, slotIndex))
            topProto.SubProtos.append(utilProto)

        tmp1Slot = len(topProto.SubProtos) + 2

        r = dis_to_instructions.dis(pyContract.Contract)
        # add contract class proto
        contractName = pyContract.Contract.__name__
        contractProto = translateClassType(r, topProto, contractName)
        if contractProto == None:
            print("error translateClassType")
            exit(1)
        topProto.InternConstantValue(contractProto.Name);
        contractProtoslotIndex = topProto.Numparams + len(topProto.SubProtos)
        topProto.AddInstructionLine(UvmOpCodeEnum.OP_CLOSURE,
                                    "closure %" + str(contractProtoslotIndex) + " " + contractProto.Name,
                                    None);
        topProto.AddInstructionLine(UvmOpCodeEnum.OP_MOVE,
                                    "move %" + str(tmp1Slot) + " %" + str(contractProtoslotIndex),
                                    None);
        topProto.AddInstructionLine(UvmOpCodeEnum.OP_CALL, "call %" + str(tmp1Slot) + " 1 2", None);

        subProtoName = contractProto.Name;
        topProto.Locvars.append(UvmLocVar(subProtoName, contractProtoslotIndex))
        topProto.SubProtos.append(contractProto)

        topProto.MaxStackSize = tmp1Slot + 4
        returnCount = 1

        topProto.AddInstructionLine(UvmOpCodeEnum.OP_RETURN,
                                    "return %" + str(tmp1Slot) + " " + str(returnCount + 1), None);

        info = {}
        info["event"] = eventsNames
        info["api"] = contractProto.ContractApiNames
        info["offline_api"] = contractProto.ContractOfflineApiNames
        storagePropertiesTypesArray = []
        for key in contractStoragePropertiesTypes.keys():
            storagePropertiesTypesArray.append([key, contractStoragePropertiesTypes[key]])
        info["storage_properties_types"] = storagePropertiesTypesArray
        contractApiArgsTypesArray = []
        for key in contractProto.ContractApiArgsTypes.keys():
            contractApiArgsTypesArray.append([key, contractProto.ContractApiArgsTypes[key]])
        info["api_args_types"] = contractApiArgsTypesArray

        meta_infostr = json.dumps(info)
        sourcePathDirStr = str(sourcePathDir)
        metaFile = sourcePathDirStr + "\\" + contractModname +".meta.json"
        with open(metaFile, 'w+') as f:
            f.write(meta_infostr)
        uvmsFile = sourcePathDirStr  + "\\" + contractModname  + ".uvms"
        generateDotUvms(topProto, uvmsFile)
    # r2 = dis_to_instructions.dis(pyContract.Toollib)

    # switchDic.get("", translate_DEFAULT)()

import builtins
# def main(argv):
if __name__ == '__main__':
    main(sys.argv)

    #print("dir:::::::")
    #print(dir(builtins))

