# coding: utf-8
#

import dis

import uvm_json
from uvm_modules import *
from uvm_corelib import *
import uvm_modules
import uvm_corelib
import uvm_math
import uvm_safemath
import uvm_string
import uvm_table

events = ["Inited","Transfer","Locked","Unlocked","Paused","Stopped","Resumed","Approved"]


class Storage():
    def __init__(self):
        self.name = ""
        self.symbol = ""
        self.supply = "0"
        self.precision = 0
        self.state = ""
        self.allowLock = False
        self.admin = ""



def getFromAddress():
    fromaddr = caller_address
    return fromaddr

def checkAdmin(self):
    if self.storage.admin!=getFromAddress():
        error("you are not admin, can't call this function")

def parseArgs(str,count,errmsg):
    if str ==None:
        return error(errmsg)
    parsed = uvm_string.split(str,",")
    if parsed==None or uvm_table.length(parsed)!=count:
        return error(errmsg)
    return parsed

def parseAtLeastArgs(str,count,errmsg):
    if str ==None:
        return error(errmsg)
    parsed = uvm_string.split(str,",")
    if parsed==None or uvm_table.length(parsed)<count:
        return error(errmsg)
    return parsed

def arrayContains(col,v):
    if col==None or v==None:
        return False
    count = rawlen(col)
    i=1  #start from 1
    while i<=count:
        if col[i]==v:
            return True
        i+=1
    return False


def checkState(self):
    state = self.storage.state
    if state == "NOT_INITED":
        return error("contract token not inited")
    elif state == "PAUSED":
        return error("contract token not paused")
    elif state == "STOPPED":
        return error("contract token not stopped")

def checkStateInited(self):
    state = self.storage.state
    if state == "NOT_INITED":
        return error("contract token not inited")

def checkAddress(addr):
    result = is_valid_address(addr)
    if not result:
        return error("address format error")
    return True

def getBalanceOfUser(self,addr):
    balance = fast_map_get("users",addr)
    if balance==None:
        return "0"
    return tostring(balance)

class Contract(UvmContract):
    storage = Storage()
    def init(self):
        self.storage.name = ""
        self.storage.symbol = ""
        self.storage.supply = "0"
        self.storage.precision = 1
        self.storage.state = "NOT_INITED"
        self.storage.allowLock = False
        self.storage.admin = caller_address
        print("init")

    def test_pairs(self):
        bmap = {}
        bmap["b1"] = "bb1111"
        bmap["b2"] = "bb22222"

        #pairs
        it = pairs(bmap)
        k = None
        v = None
        k = it(bmap, k)
        while (k):
            print(k)
            k = it(bmap, k)


    def offlinestate(self, s):
        return self.storage.state

    def offlinetokenName(self, s):
        return self.storage.tokenName

    def offlinetokenSymbol(self, s):
        return self.storage.tokenSymbol

    def offlineprecision(self, s):
        return self.storage.precision

    def offlinesupply(self, s):
        return self.storage.supply

    def offlineadmin(self, s):
        return self.storage.admin

    def offlineisAllowLock(self, s):
        return self.storage.isAllowLock

    def offlinebalanceOf(self, owner):
        checkStateInited(self)
        return getBalanceOfUser(self,owner)

    def offlineapprovedBalanceFrom(self,arg):
        parsed = parseAtLeastArgs(arg, 2,
                                        "argument format error, need format is spenderAddress,authorizerAddress")
        spender = tostring(parsed[1])
        authorizer = tostring(parsed[2])
        checkAddress(spender)
        checkAddress(authorizer)
        allowedDataStr = fast_map_get("allowed", authorizer)
        if (allowedDataStr == None):
            return "0"
        allowedDataTable = totable(uvm_json.loads(tostring(allowedDataStr)))
        if (allowedDataTable == None):
            return "0"
        allowedAmount = allowedDataTable[spender]
        if (allowedAmount == None):
            return "0"
        return allowedAmount

    def offlinelockedBalanceOf(self,owner):
        lockedInfo = fast_map_get("lockedAmounts", owner)
        if (lockedInfo == None):
            return "0,0"
        return lockedInfo

    def offlineallApprovedFromUser(self,arg):
        authorizer = arg
        checkAddress(authorizer)

        allowedDataStr = fast_map_get("allowed", authorizer)
        if (allowedDataStr == None):
            return "{}"
        return allowedDataStr

    def init_token(self,arg):
        checkAdmin(self)
        if self.storage.state != "NOT_INITED":
            return error("this token contract inited before")

        parsed = parseAtLeastArgs(arg,4,"argument format error, need format: name,symbol,supply,precision")
        info ={}
        name = parsed[1]
        symbol = parsed[2]
        supplystr = parsed[3]
        precision = tointeger(parsed[4])
        info["name"] = name
        info["symbol"] = symbol
        info["supply"] = supplystr
        info["precision"] = precision
        if name==None or rawlen(name)<1:
            return error("name needed")

        if (symbol == None or rawlen(symbol) < 1):
            return error("symbol needed")

        bigintSupply = uvm_safemath.bigint(supplystr)
        bigint0 = uvm_safemath.bigint(0)

        if uvm_safemath.le(bigintSupply,bigint0):
            return error("invalid supply:"+supplystr)

            fromAddress = getFromAddress()
            if(fromAddress!=caller_address):
                return error("init_token can't be called from other contract:" + fromAddress)

        if precision<1:
            return error("precision must be positive integer:" + tostring(precision))

        allowedPrecisions = [1,10,100,1000,10000,100000,1000000,10000000,100000000]
        if not arrayContains(allowedPrecisions, precision):
            return error("precision can only be positive integer in " + uvm_json.dumps(allowedPrecisions))

        self.storage.name = name
        self.storage.symbol = symbol
        self.storage.supply = supplystr
        self.storage.precision = precision
        self.storage.state = "COMMON"

        fast_map_set("users",self.storage.admin,supplystr)

        emit("Inited",supplystr)

        eventArg = {}
        eventArg["from"] = ""
        eventArg["to"] = caller_address
        eventArg["amount"] = supplystr
        emit("Transfer", uvm_json.dumps(eventArg))


    def transfer(self,arg):
        checkState(self)
        parsed = parseAtLeastArgs(arg, 2, "argument format error, need format is to_address,integer_amount[,memo]")

        to = parsed[1]
        amountStr = parsed[2]
        checkAddress(to)

        bigintAmount = uvm_safemath.bigint(amountStr)
        bigint0 = uvm_safemath.bigint(0)
        if (amountStr == None or uvm_safemath.le(bigintAmount, bigint0)):
            return error("invalid amount:" + amountStr)

        fromAddress = getFromAddress()
        if fromAddress==to:
            return error("fromAddress and toAddress is same："+fromAddress)

        temp = fast_map_get("users", fromAddress)
        if temp==None:
            temp="0"
        fromBalance = uvm_safemath.bigint(temp)
        temp = fast_map_get("users", to)
        if temp == None:
            temp = "0"
        toBalance = uvm_safemath.bigint(temp)
        if (uvm_safemath.lt(fromBalance, bigintAmount)):
            return error("insufficient balance:"+uvm_safemath.tostring(fromBalance))

        fromBalance = uvm_safemath.sub(fromBalance, bigintAmount)
        toBalance = uvm_safemath.add(toBalance, bigintAmount)

        frombalanceStr = uvm_safemath.tostring(fromBalance)
        if (frombalanceStr == "0"):
            fast_map_set("users", fromAddress, None)
        else:
            fast_map_set("users", fromAddress, frombalanceStr)
        fast_map_set("users", to, uvm_safemath.tostring(toBalance))

        if (is_valid_contract_address(to)):
            #call_contract_api(to,"on_deposit_contract_token",amountStr)
            r,code = send_message(to, "on_deposit_contract_token", amountStr)
            if(code!=0):
                print("send_message to call contract:"+to+" api:on_deposit_contract_token fail!! code="+str(code))

        eventArg={}
        eventArg["from"] = fromAddress
        eventArg["to"] = to
        eventArg["amount"] = amountStr
        eventArgStr = tojsonstring(eventArg)
        emit("Transfer", eventArgStr)

    def transferFrom(self,arg):
        checkState(self)
        parsed = parseAtLeastArgs(arg, 3, "argument format error, need format is fromAddress,to_address,integer_amount[,memo]")
        withdrawFromAddress = tostring(parsed[1])
        to = parsed[2]
        amountStr = parsed[3]
        checkAddress(withdrawFromAddress)
        checkAddress(to)

        if (withdrawFromAddress == to) :
            return error("fromAddress and toAddress is same：$fromAddress")

        bigintAmount = uvm_safemath.bigint(amountStr)
        bigint0 = uvm_safemath.bigint(0)

        if (amountStr == None or uvm_safemath.le(bigintAmount, bigint0)):
            return error("invalid amount:" + amountStr)

        if withdrawFromAddress==to:
            return error("fromAddress and toAddress is same："+withdrawFromAddress)

        temp = fast_map_get("users", withdrawFromAddress)
        if temp==None:
            temp="0"
        withdrawFromBalance = uvm_safemath.bigint(temp)
        temp = fast_map_get("users", to)
        if temp == None:
            temp = "0"
        toBalance = uvm_safemath.bigint(temp)
        if (uvm_safemath.lt(withdrawFromBalance, bigintAmount)):
            return error("insufficient balance:"+uvm_safemath.tostring(withdrawFromBalance))

        #check allowed
        allowedDataStr = fast_map_get("allowed", withdrawFromAddress)
        if allowedDataStr==None:
            return error("not enough approved amount to withdraw")

        allowedData = totable(uvm_json.loads(allowedDataStr))
        if allowedData==None:
            return error("not enough approved amount to withdraw")
        contractCaller = getFromAddress()
        approvedAmountStr = allowedData[contractCaller]
        if approvedAmountStr == None:
            return error("no approved amount to withdraw")
        bigintApprovedAmount = uvm_safemath.bigint(approvedAmountStr)
        if bigintApprovedAmount==None or uvm_safemath.gt(bigintAmount,bigintApprovedAmount):
            return error("not enough approved amount to withdraw")

        ####################
        withdrawFromBalance = uvm_safemath.sub(withdrawFromBalance, bigintAmount)
        toBalance = uvm_safemath.add(toBalance, bigintAmount)

        frombalanceStr = uvm_safemath.tostring(withdrawFromBalance)
        if (frombalanceStr == "0"):
            fast_map_set("users", withdrawFromAddress, None)
        else:
            fast_map_set("users", withdrawFromAddress, frombalanceStr)
        fast_map_set("users", to, uvm_safemath.tostring(toBalance))
        bigintApprovedAmount = uvm_safemath.sub(bigintApprovedAmount, bigintAmount)
        bigintApprovedAmountStr = uvm_safemath.tostring(bigintApprovedAmount)
        if bigintApprovedAmountStr == "0":
            allowedData[contractCaller] = None
        else:
            allowedData[contractCaller] = bigintApprovedAmountStr
        allowedDataStr = tojsonstring(allowedData)
        fast_map_set("allowed", withdrawFromAddress, allowedDataStr)

        eventArg={}
        eventArg["from"] = withdrawFromAddress
        eventArg["to"] = to
        eventArg["amount"] = amountStr
        eventArgStr = tojsonstring(eventArg)
        emit("Transfer", eventArgStr)

    def approve(self,arg):
        checkState(self)
        parsed = parseAtLeastArgs(arg, 2,
                                        "argument format error, need format is spenderAddress,amount(with precision)")
        spender = tostring(parsed[1])
        checkAddress(spender)
        amountStr = tostring(parsed[2])
        bigintAmount = uvm_safemath.bigint(amountStr)
        bigint0 = uvm_safemath.bigint(0)
        if (amountStr == None or uvm_safemath.lt(bigintAmount, bigint0)):
            return error("amount must be non-negative integer")
        contractCaller = getFromAddress()
        allowedDataStr = fast_map_get("allowed", contractCaller)
        if (allowedDataStr == None):
            allowedDataTable={}
        else:
            allowedDataTable = uvm_json.loads(allowedDataStr)
            if allowedDataTable==None:
                return error("allowed storage data error")

        if (uvm_safemath.eq(bigintAmount, bigint0)):
            allowedDataTable[spender] = None
        else:
            allowedDataTable[spender] = amountStr
        fast_map_set("allowed", contractCaller, tojsonstring(allowedDataTable))

        eventArg = {}
        eventArg["from"] = contractCaller
        eventArg["spender"] = spender
        eventArg["amount"] = amountStr
        eventArgStr = tojsonstring(eventArg)
        emit("Approved", eventArgStr)

    def pause(self,arg):
        checkAdmin(self)
        state = self.storage.state
        if(state != "COMMON"):
            return error("wrong state")
        self.storage.state = "PAUSED"
        emit("Paused", "")

    def resume(self,arg):
        checkAdmin(self)
        state = self.storage.state
        if(state != "PAUSED"):
            return error("wrong state")
        self.storage.state = "COMMON"
        emit("Resumed", "")

    def stop(self,arg):
        checkAdmin(self)
        state = self.storage.state
        if(state == "STOPPED"):
            return error("already stopped")
        if (state == "PAUSED"):
            return error("this contract paused now, can't stop")
        self.storage.state = "STOPPED"
        emit("Stopped", "")

    def lock(self,arg):
        checkState(self)
        if (self.storage.allowLock == False):
            return error("this token contract not allow lock balance")
        parsed = parseAtLeastArgs(arg, 2, "arg format error, need format is integer_amount,unlockBlockNumber")
        toLockAmount = parsed[1]
        unlockBlockNumber = tointeger(parsed[2])
        bigintToLockAmount = uvm_safemath.bigint(toLockAmount)
        bigint0 = uvm_safemath.bigint(0)
        if (toLockAmount == None or uvm_safemath.le(bigintToLockAmount, bigint0)):
            return error("to unlock amount must be positive integer")
        if unlockBlockNumber < get_header_block_num():
            return error(
                "to unlock block number can't be earlier than current block number " + tostring(get_header_block_num()))
        fromAddress = getFromAddress()
        if (fromAddress != caller_address):
            return error("only common user account can lock balance") # contract account can't lock token

        temp = fast_map_get("users", fromAddress)
        if (temp == None):
            return error("your balance is 0")
        bigintFromBalance = uvm_safemath.bigint(temp)
        if (uvm_safemath.gt(bigintToLockAmount, bigintFromBalance)):
            return error("you have not enough balance to lock")
        lockedAmount = fast_map_get("lockedAmounts", fromAddress)
        if (lockedAmount == None):
            fast_map_set("lockedAmounts", fromAddress, (tostring(toLockAmount) + "," + tostring(unlockBlockNumber)))
        else:
            return error("you have locked balance now, before lock again, you need unlock them or use other address to lock")

        bigintFromBalance = uvm_safemath.sub(bigintFromBalance, bigintToLockAmount)
        bigintFromBalanceStr = uvm_safemath.tostring(bigintFromBalance)
        if (bigintFromBalanceStr == "0"):
            bigintFromBalanceStr = None
        fast_map_set("users", fromAddress, bigintFromBalanceStr)
        emit("Locked", tostring(toLockAmount))

    def forceUnlock(self,arg):
        checkState(self)
        if (self.storage.allowLock == False):
            return error("this token contract not allow lock balance")
        unlockAdress = arg
        if (unlockAdress == None or unlockAdress == ""):
            return error("unlockAdress should not be empty")

        lockedStr = fast_map_get("lockedAmounts", unlockAdress)
        if (lockedStr ==None):
            return error("you have not locked balance")
        lockedInfoParsed = parseAtLeastArgs(tostring(lockedStr), 2, "locked amount info format error")
        lockedAmountStr = lockedInfoParsed[1]
        canUnlockBlockNumber = tointeger(lockedInfoParsed[2])
        if (get_header_block_num() < canUnlockBlockNumber):
            return error("your locked balance only can be unlock after block #"+tostring(canUnlockBlockNumber))

        fast_map_set("lockedAmounts", unlockAdress, None)
        temp = fast_map_get("users", unlockAdress)
        if (temp == None):
            temp="0"

        bigintFromBalance = uvm_safemath.bigint(temp)
        bigintLockedAmount = uvm_safemath.bigint(tostring(lockedAmountStr))
        bigintFromBalance = uvm_safemath.add(bigintFromBalance, bigintLockedAmount)
        fast_map_set("users", unlockAdress, uvm_safemath.tostring(bigintFromBalance))

        tempevent = unlockAdress + "," + tostring(lockedStr)
        emit("Unlocked", tempevent)

    def unlock(self,arg):
        checkState(self)
        if (self.storage.allowLock == False):
            return error("this token contract not allow lock balance")
        unlockAdress = getFromAddress()
        if (unlockAdress == None or unlockAdress == ""):
            return error("unlockAdress should not be empty")

        lockedStr = fast_map_get("lockedAmounts", unlockAdress)
        if (lockedStr == None):
            return error("you have not locked balance")
        lockedInfoParsed = parseAtLeastArgs(tostring(lockedStr), 2, "locked amount info format error")
        lockedAmountStr = lockedInfoParsed[1]
        canUnlockBlockNumber = tointeger(lockedInfoParsed[2])
        if (get_header_block_num() < canUnlockBlockNumber):
            return error("your locked balance only can be unlock after block #" + tostring(canUnlockBlockNumber))

        fast_map_set("lockedAmounts", unlockAdress, None)
        temp = fast_map_get("users", unlockAdress)
        if (temp == None):
            temp = "0"

        bigintFromBalance = uvm_safemath.bigint(temp)
        bigintLockedAmount = uvm_safemath.bigint(tostring(lockedAmountStr))
        bigintFromBalance = uvm_safemath.add(bigintFromBalance, bigintLockedAmount)
        fast_map_set("users", unlockAdress, uvm_safemath.tostring(bigintFromBalance))

        tempevent = unlockAdress + "," + tostring(lockedStr)
        emit("Unlocked", tempevent)

    def on_deposit_contract_token(self,arg):
        precontr = get_prev_call_frame_contract_address()
        if (precontr == None or precontr == ""):
            return error("null precontr"+arg)
        print("receive token of "+precontr + " amount:"+ arg)

    def openAllowLock(self,arg):
        checkAdmin(self)
        checkState(self)
        if self.storage.allowLock==True:
            return error("allowLock already opened")
        self.storage.allowLock = True
        emit("AllowLockOpened","")



if __name__ == '__main__':
    con = Contract()
    con.init()
    con.init_token("ABCname,ABC,80000000,1000")

    #print(sys.path)
    # dis.dis(Contract)


