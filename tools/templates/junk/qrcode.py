# Example of code to recognize QRCode
#
import re

print("Please, set GS1 text marker; hint: use '\[GS1\]' or '\([0-9]+?\)'")
decode_gs1 = input("GS1 text marker: ")
sanitized = decode_gs1.replace("\\","")
sn_concat_char = input("Lot and S/N concat char: ")
sn_concat_char = sn_concat_char or "."
bc_regex = "[0-9]{8,14}"

code_dixi = "DIXI;39932;pf;2565.234.1;https://www.dixipolytool.ch"
code_ridix = "TS.NATURHB2200"
barcode = "07630036147481"
# Build Blaser code (GS1 type QRCode)
if "[0-9]+?" in decode_gs1:
    print("GS1 text marker includes Application Identifier")
    code_blaser = (sanitized + "00870-40-1022").replace("[0-9]+?", "240")
    code_blaser += (sanitized + "339905").replace("[0-9]+?", "10")
    code_blaser += (sanitized + "25032415270324301").replace("[0-9]+?", "11")
    code_blaser += (sanitized + "1").replace("[0-9]+?", "21")
    code_blaser += (sanitized + "07630036147481").replace("[0-9]+?", "01")
else:
    print("GS1 text marker does not include Application Identifier")
    code_blaser = sanitized + "24000870-40-1022"
    code_blaser += sanitized + "10339905"
    code_blaser += sanitized + "1125032415270324301"
    code_blaser += sanitized + "211"
    code_blaser += sanitized + "0107630036147481"
print("Read Blaser code is '%s'" % code_blaser)

# Now build the recognition pattern
gs1_regex = r"((%s??[^\%s]+))+$" % (decode_gs1, sanitized[0])

# Test #1: GS1 type QRCode (Blaser QRCode)
# Now check for right recognition
res = re.match(gs1_regex, code_blaser)
if not res or re.match(bc_regex, code_blaser):
    print("*** ERROR! Blaser code not recognized! ***")
else:
    print("Blaser code is a GS1 QRCode")
    print(res)
    # Now split QRCode items
    items = re.split("(%s)" % decode_gs1, code_blaser)[1:]
    print(items)
    if "[0-9]+?" in decode_gs1:
        res = dict([(re.search("[0-9]+", k).group(), v) for (k, v) in zip(items[:: 2], items[1:: 2])])
    else:
        res = {}
        for k in items[1:: 2]:
            if k.startswith(("70", "8")):
                res[k[: 4]] = k[4:]
            elif k.startswith(("24", "25", "31", "32", "33", "34", "35", "36", "39", "4", "71")):
                res[k[: 3]] = k[3:]
            else:
                res[k[: 2]] = k[2:]
    print(res)
    # now convert common AI in Odoo name
    for (k, x) in (("01", "barcode"), ("10", "lot"), ("21", "serial"), ("240", "ref")):
        if k in res:
            res[x] = res[k]
            del res[k]
    # Odoo cannot manage lot + s/n
    if "lot" in res and "serial" in res:
        res["21"] = res["serial"]
        res["10"] = res["lot"]
        del res["lot"]
        res["serial"] = res["10"] + sn_concat_char + res["21"]
    print(res)

# Test #2 with Dixi QRCode (testual with separator)
res = re.match(gs1_regex, code_dixi)
if res or re.match(bc_regex, code_dixi):
    print("*** ERROR! Dixi code not recognized! ***")
else:
    print("Found Dixi QRCode")
    if ";" in code_dixi:
        res = {}
        items = code_dixi.split(";")
        for k,v in enumerate(items):
            if k == 1:
                res["ref"] = v
            else:
                res[str(k)] = v
        print(res)

# Test #3 with Natur/Ridix QRCode (testual w/o separator)
res = re.match(gs1_regex, code_ridix)
if res or re.match(bc_regex, code_ridix):
    print("*** ERROR! Ridix code not recognized! ***")
else:
    print("Found Ridix QRCode")
    if ";" not in code_ridix:
        res = {"ref": code_ridix}
        print(res)

# Test #4 with barcode
barcode = "07630036147481"
res = re.match(bc_regex, barcode)
if not res or re.match(gs1_regex, barcode):
    print("*** ERROR! Barcode not recognized! ***")
else:
    print("Found barcode")
    res = {"barcode": barcode}
    print(res)

