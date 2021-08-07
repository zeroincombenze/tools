from __future__ import print_function
from builtins import input
# import pdb


def eval_GTIN(code, code_len):
    if code_len == 13:
        pad_code = '%012d' % code
        range_code = 12
    elif code_len == 8:
        pad_code = '%07d' % code
        range_code = 7
    else:
        print("Invalid code len %d" % code_len)
        return False
    chkdgt = 0
    for i in range(range_code):
        n = int(pad_code[range_code - i - 1])
        if (i % 2):
            chkdgt = chkdgt + n
        else:
            chkdgt = chkdgt + n * 3
    chkdgt = chkdgt % 10
    if chkdgt:
        chkdgt = 10 - chkdgt
    pad_code = pad_code + str(chkdgt)
    return pad_code


def test_gtin():
    code_len = 8
    test_dict = {}
    test_dict[1] = '00000017'
    test_dict[1000] = '00010009'
    test_dict[1001] = '00010016'
    test_dict[1123] = '00011235'
    test_dict[8005068] = '80050681'
    test_dict[2969675] = '29696758'
    for code in test_dict:
        pad_code = eval_GTIN(code, code_len)
        if pad_code == test_dict[code]:
            res = "OK"
        else:
            res = "***Failed***"
        print("%08d -> %s (%s)" % (code, pad_code, res))
    code_len = 13
    test_dict = {}
    test_dict[1] = '0000000000017'
    test_dict[2] = '0000000000024'
    test_dict[3] = '0000000000031'
    test_dict[807680208573] = '8076802085738'
    test_dict[807680019503] = '8076800195033'
    test_dict[78332083122] = '0783320831225'
    test_dict[7742816007] = '0077428160074'
    for code in test_dict:
        pad_code = eval_GTIN(code, code_len)
        if pad_code == test_dict[code]:
            res = "OK"
        else:
            res = "***Failed*** expected:" + test_dict[code]
        print("%013d -> %s (%s)" % (code, pad_code, res))


test_gtin()
code_len = '8'
code = input('GTIN Code: ')
if code == '':
    code = '00011268'
code = ('00000000' + code)[-8:]
nums = input('How many codes? ')
if nums == '':
    nums = '8'
start_code = int(code)
code_len = int(code_len)
nums = int(nums)
for i in range(nums):
    code = start_code + i
    pad_code = eval_GTIN(code, code_len)
    print("%s " % pad_code)
