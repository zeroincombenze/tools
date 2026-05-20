#!/usr/bin/env python
# import pdb


def encodebasex(base, number):
    l = len(base)
    if number < l:
        return base[number]
    return encodebasex(base, int(number / l)) + base[number % l] 


base = "0123456789"
for i in range(26):
    base += chr(i+65)
print("Base = %s" % base)
# pdb.set_trace()
for i in range(1000):
     encoded = encodebasex(base, i)
     print("%d -> '%s' " % (i, encoded))
