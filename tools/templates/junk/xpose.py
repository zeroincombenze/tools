with open("xpose.log", "r") as fd:
    content = fd.read().split("\n")
import pdb; pdb.set_trace()
for line in content:
    items = [x.strip() for x in line.split("|")]
    if items[0].startswith("-"):
        continue
    if not items[0].isdigit():
        continue
    if items[1] == "ready":
        continue
    print("psql -Uodoo10 forpress -c \"update account_invoice set fatturapa_state='%s' where id=%s\"" % (items[1], int(items[0])))

