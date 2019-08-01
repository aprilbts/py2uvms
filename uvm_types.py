
class UvmTypeInfoEnum:
    LTI_OBJECT = 0
    LTI_NIL = 1
    LTI_STRING = 2
    LTI_INT = 3
    LTI_NUMBER = 4
    LTI_BOOL = 5
    LTI_TABLE = 6
    LTI_FUNCTION = 7
    LTI_UNION = 8
    LTI_RECORD = 9
    LTI_GENERIC = 10
    LTI_ARRAY = 11
    LTI_MAP = 12
    LTI_LITERIAL_TYPE = 13
    LTI_STREAM = 14
    LTI_UNDEFINED = 100

class UvmOpCodeEnum:
    OP_MOVE=0
    OP_LOADK=1
    OP_LOADKX=2
    OP_LOADBOOL=3
    OP_LOADNIL=4
    OP_GETUPVAL=5
    OP_GETTABUP=6
    OP_GETTABLE=7
    OP_SETTABUP=8
    OP_SETUPVAL=9
    OP_SETTABLE=10
    OP_NEWTABLE=11
    OP_SELF=12

    OP_ADD=13
    OP_SUB=14
    OP_MUL=15
    OP_MOD=16
    OP_POW=17
    OP_DIV=18
    OP_IDIV=19
    OP_BAND=20
    OP_BOR=21
    OP_BXOR=22
    OP_SHL=23
    OP_SHR=24
    OP_UNM=25
    OP_BNOT=26
    OP_NOT=27
    OP_LEN=28

    OP_CONCAT=29
    OP_JMP=30
    OP_EQ=31
    OP_LT=32
    OP_LE=33

    OP_TEST=34
    OP_TESTSET=35

    OP_CALL=36
    OP_TAILCALL=37
    OP_RETURN=38

    OP_FORLOOP=39
    OP_FORPREP=40
    OP_TFORCALL=41
    OP_TFORLOOP=42

    OP_SETLIST=43
    OP_CLOSURE=44
    OP_VARARG=45
    OP_EXTRAARG=46
    OP_PUSH=47
    OP_POP=48
    OP_GETTOP=49

    OP_CMP=50
    OP_CMP_EQ=51
    OP_CMP_NE=52
    OP_CMP_GT=53
    OP_CMP_LT=54
    OP_CCALL=55
    OP_CSTATICCALL=56

class StorageValueTypes:
    storage_value_null = 0
    storage_value_int = 1
    storage_value_number = 2
    storage_value_bool = 3
    storage_value_string = 4
    storage_value_stream = 5

    storage_value_unknown_table = 50
    storage_value_int_table = 51
    storage_value_number_table = 52
    storage_value_bool_table = 53
    storage_value_string_table = 54
    storage_value_stream_table = 55

    storage_value_unknown_array = 100
    storage_value_int_array = 101
    storage_value_number_array = 102
    storage_value_bool_array = 103
    storage_value_string_array = 104
    storage_value_stream_array = 105

    storage_value_userdata = 201
    storage_value_not_support = 202

class UvmInstruction:
    def __init__(self,uvmOpCode,insInpython,uvmAsmLine):
        self.uvmOpCode=uvmOpCode
        self.insInpython = insInpython
        self.uvmAsmLine = uvmAsmLine
        self.uvmOpArgs = []
        self.LineInSource = -1
        self.HasLocationLabel = False
        self.label = ""

class UvmLocVar:
    def __init__(self, name, slotIndex):
        self.Name=name
        self.SlotIndex=slotIndex
        self.StartPc = 0
        self.EndPc = -1

class UvmUpvaldesc:
    def __init__(self,name):
        self.Name=name
        self.Instack = False
        self.Idx = -1

class UvmProto:
    def __init__(self):
        self.Name=""
        self.IsVararg=False
        self.Numparams=0
        self.MaxStackSize=0
        self.LineDefined=-1
        self.LastLineDefined=-1
        self.PycoConstsNum=0
        self.ConstantValues=[]
        self.CodeInstructions=[]
        self.SubProtos=[]
        self.Lineinfo=[]
        self.Locvars=[]
        self.Upvalues=[]
        self.Source=""
        self.pyInsToUvmInss = []
        self.IlInstructionsToUvmInstructionsMap={}
        self.NeededLocationsMap={}
        self.Parent=None

        self.tmp1StackTopSlotIndex=0
        self.tmp2StackTopSlotIndex=0
        self.tmp3StackTopSlotIndex=0
        self.tmpMaxStackTopSlotIndex=0

        self.EventNames=[]
        self.ContractApiNames=[]
        self.ContractOfflineApiNames=[]
        self.ContractStoragePropertiesTypes={}
        self.ContractApiArgsTypes={}
        self.isOfflineFunc = False

        self.blockStack = []

    def AddInstructionLine(self,op,line,ins):
        uvmIns = UvmInstruction(op, ins, line)
        self.CodeInstructions.append(uvmIns)


    def FindLocvar(self,name):
        for loc in self.Locvars:
            if(loc.Name == name):
                return loc
        return None

    def InternConstantValue(self, cons):
        i=0
        consnum= len(self.ConstantValues)
        for i in range(0,consnum):
            if self.ConstantValues[i]==cons:
                return i
        self.ConstantValues.append(cons)
        return consnum


    def InternUpvalue(self,upname):
        #if InNotAffectMode:
         #   return 0
        i=0
        for up in self.Upvalues:
            if(up.Name == upname):
                return i
            i=i+1
        upval=UvmUpvaldesc(upname)
        if(self.Parent!=None):
            loc = self.Parent.FindLocvar(upname)
            if(loc != None):
                upval.Instack= True
                upval.Idx = loc.SlotIndex
        else:
            upval.Instack = False

        if(not upval.Instack):
            if(self.Parent==None):
                upval.Idx = len(self.Upvalues)
                upval.Instack = True
            else:
                parentUpvalueIndex = self.Parent.InternUpvalue(upname)
                upval.Idx = parentUpvalueIndex
                upval.Instack = False
        self.Upvalues.append(upval)
        return (len(self.Upvalues)-1)

base_conss = [True,False,None]
uvm_globals = ["print", "pprint", "table", "string", "time", "math", "safemath", "json", "type", "require", "Array", "Stream",\
                "import_contract_from_address", "import_contract", "emit", "is_valid_address", "is_valid_contract_address",\
				"get_prev_call_frame_contract_address", "get_prev_call_frame_api_name", "get_contract_call_frame_stack_size",\
                "uvm", "storage", "exit", "self", "debugger", "exit_debugger","delegate_call",\
                "caller", "caller_address",\
                "contract_transfer", "contract_transfer_to", "transfer_from_contract_to_address",\
				"transfer_from_contract_to_public_account",\
                "get_chain_random", "get_transaction_fee", "fast_map_get", "fast_map_set",\
                "get_transaction_id", "get_header_block_num", "wait_for_future_random", "get_waited",\
                "get_contract_balance_amount", "get_chain_now", "get_current_contract_address", "get_system_asset_symbol", "get_system_asset_precision",\
                "pairs", "ipairs", "pairsByKeys", "collectgarbage", "error", "getmetatable", "_VERSION",\
                "tostring", "tojsonstring", "tonumber", "tointeger", "todouble", "totable", "toboolean",\
                "next", "rawequal", "rawlen", "rawget", "rawset", "select",\
                "setmetatable",\
				"hex_to_bytes", "bytes_to_hex", "sha256_hex", "sha1_hex", "sha3_hex", "ripemd160_hex",\
				"cbor_encode", "cbor_decode", "signature_recover","get_address_role","send_message",\
               "createMap","createArray","setMap","getMap","setArray","appendArray","getArrayCount","getLenOf","insertArray","sortArray","removeArray"]

