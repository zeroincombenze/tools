from datetime import date
from random import randint

def add_item(prefix, value):
    return "(%s)%s" % (prefix, value)


print("Buidl QRCcode sent to keyboard to test Inventory")
print("Date required are:")
print(" - Supplier product code")
print(" - Batch number or serial number")
print(" - Barcode")
tbl_code_name = {
    "00870-40-0208": "Blasocut 2000 universal (fusto)",
    "00870-40-1022": "Blasocut 2000 universal (cisterna)",
    "00875-40-0208": "Blasocut 2000 (fusto)",
    "00875-40-1022": "Blasocut 2000 (cisterna)",
    "00883-40-0208": "Blasocut Kombi (fusto)",
    "00883-40-1022": "Blasocut Kombi (cisterna)",
    "02830-03-0208": "Vasco 3000 (fusto)",
    "02830-03-1022": "Vasco 3000 (cisterna)",
    "02860-04-0208": "Vasco 6000 (fusto)",
    "02860-04-1022": "Vasco 6000 (cisterna)",
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

for k, v in tbl_code_name.items():
    print("%s '%-40.40s' %s" % (k, v, tbl_code_barcode.get(k, "")))

today = date.today()
date_from = "%02d%02d%02d" % (today.year % 100, today.month, 1)
date_to = "%02d%02d%02d" % ((today.year + 2) % 100, today.month, 1)

suppl_code = batch_code = barcode = ""
while True:
    print("")
    old_suppl_code = suppl_code
    dummy = input("Supplier code or X to exit (%s): " % suppl_code).strip()
    if dummy == "X":
        break
    if dummy:
        suppl_code = str(dummy)
    if suppl_code in tbl_code_name:
        print("Product: %s" % tbl_code_name[suppl_code])
    else:
        for k in tbl_code_name.keys():
            if suppl_code in k:
                suppl_code = k
                break
    if suppl_code != old_suppl_code:
        batch_code = ""
        barcode = ""
    dummy = input("Batch code or batch.serial (%s): " % batch_code).strip()
    if dummy:
        batch_code = str(dummy)
    if not batch_code:
        batch_code = str(randint(10000000, 99999999))
    if suppl_code in tbl_code_barcode:
        barcode = tbl_code_barcode[suppl_code]
    else:
        barcode = str(randint(0, 99999999999999))
    dummy = input("Barcode....................(%s): " % barcode).strip()
    if dummy:
        barcode = str(dummy)
    if "." in batch_code:
        batch, serial = batch_code.split(".", 1)
        if not batch:
            batch = batch_code
        serial = serial or str(randint(0, 99))
    else:
        batch = batch_code
        serial = "0"
    ctr = input("# of serial....................: ").strip()
    ctr = int(ctr) if ctr else 0
    while ctr:
        qrcode = ""
        qrcode += add_item("240", suppl_code)
        qrcode += add_item("10", batch)
        qrcode += add_item("11", date_from)
        qrcode += add_item("15", date_to)
        qrcode += add_item("30", "1")
        serial = str(int(serial) + 1)
        qrcode += add_item("21", serial)
        batch_code = batch + "." + serial
        ctr -= 1
        qrcode += add_item("01", barcode)
        print(qrcode)
