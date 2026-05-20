def add_item(prefix, value):
    return "(%s)%s" % (prefix, value)


print("Buidl QRCcode sent to keyboard to test Inventory")
print("Date required are:")
print(" - Supplier product code")
print(" - Batch number or serial number")
print(" - Barcode")
tbl_code_name = {
    "00875-40-0208": "Blasocut 2000 (fusto)",
    "00875-40-1022": "Blasocut 2000 (cisterna)",
    "00875-40-0208": "Vasco 6000? (fusto)",
    "00875-40-1022": "Vasco 6000? (cisterna)",
    "00883-40-0208": "Blasocut Kombi (fusto)",
    "00883-40-1022": "Blasocut Kombi (cisterna)",
    "02516-01-0208": "Vascomill CSF (fusto)",
    "02516-01-1022": "Vascomill CSF (cisterna)",
    "03160-03-0208": "Blasomill 22 (fusto)",
    "03160-03-1022": "Blasomill 22 (cisterna)",
    "02860-03-0208": "Vasco 6000 (fusto)",
    "02860-03-1022": "Vasco 6000 (cisterna)",
    "29170-04-0208": "Blasoclean AF (fusto)",
    "29170-04-1022": "Blasoclean AF (cisterna)",
}
tbl_code_barcode = {
    "00875-40-0208": "07630036148137",
    "00875-40-1022": "07630036148136",
    "00875-40-0208": "07630805312652",
    "00875-40-1022": "07630805312651",
    "00883-40-0208": "07630036148563",
    "00883-40-1022": "07630036148562",
    "02516-01-0208": "07630036141234",
    "02516-01-1022": "07630036141233",
    "03160-03-0208": "07630036153598",
    "03160-03-1022": "07630036153597",
    "02860-03-0208": "07630805312670",
    "02860-03-1022": "07630805312669",
    "29170-04-0208": "07630036158913",
    "29170-04-1022": "07630036158912",
}
for k in tbl_code_name.keys():
    print("%s '%-40.40s' %s" % (k, tbl_code_name[k], tbl_code_barcode[k]))

suppl_code = batch_code = barcode = ""
while True:
    print("")
    dummy = input("Supplier code or X to exit (%s): " % suppl_code).strip()
    if dummy == "X":
        break
    if dummy:
        suppl_code = dummy
    if suppl_code in tbl_code_name:
        print("Product: %s" % tbl_code_name[suppl_code])
    dummy = input("Batch code or batch.serial (%s): " % batch_code).strip()
    if dummy:
        batch_code = dummy
    if suppl_code in tbl_code_barcode:
        barcode = tbl_code_barcode[suppl_code]
    dummy = input("Barcode....................(%s): " % barcode).strip()
    if dummy:
        barcode = dummy
    if "." in batch_code:
        batch, serial = batch_code.split(".", 1)
    else:
        batch = batch_code
        serial = ""
    qrcode = ""
    qrcode += add_item("240", suppl_code)
    qrcode += add_item("10", batch)
    qrcode += add_item("11", "251001")
    qrcode += add_item("15", "281001")
    qrcode += add_item("30", "1")
    if serial:
        qrcode += add_item("21", serial)
    qrcode += add_item("01", barcode)
    print(qrcode)

