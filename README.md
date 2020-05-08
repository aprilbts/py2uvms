# py2uvms

支持python版本 3.7

合约：
不支持合约方法内部再调用本合约的方法
不支持python内置builtin方法

支持通过如下方法调用其他合约：
call_contract_api(conaddr,api_name,arg)
static_call_contract_api(conaddr,api_name,arg)
#return list: [result,code]
send_message(conaddr,api_name,arg)
delegate_call(conaddr,api_name,arg)

使用：
python translate_py_code.py  G:\contract.py
例子见: py_contract_demo.py