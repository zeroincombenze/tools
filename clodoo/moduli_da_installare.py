import csv

VERSIONS = ('vg7', '61', '70', '80', '90', '100')
ALIAS = {}


def new_env():
    mod2xtl = {}
    for id in VERSIONS:
        mod2xtl[id] = []
    return mod2xtl


def add_elem(mod2xtl, id, elem):
    mod2xtl[id].append(elem)


def sort_data(mod2xtl):
    for id in VERSIONS:
        sorted_list = []
        for item in sorted(mod2xtl[id]):
            if item:
                sorted_list.append(item)
        mod2xtl[id] = sorted_list
        idx = 'ix' + id
        mod2xtl[idx] = 0


def get_next(mod2xtl):
    item = '~'
    for id in VERSIONS:
        idx = 'ix' + id
        ix = mod2xtl[idx]
        if ix < len(mod2xtl[id]):
            itm = mod2xtl[id][ix]
            if itm < item:
                item = itm
    vers = []
    for id in VERSIONS:
        idx = 'ix' + id
        ix = mod2xtl[idx]
        if ix < len(mod2xtl[id]):
            itm = mod2xtl[id][ix]
            if itm == item:
                vers.append(id)
                mod2xtl[idx] += 1
    return item, vers


def get_realname(item):
    global ALIAS
    if item.strip() in ALIAS:
        return ALIAS[item.strip()]
    return item.strip()


# import pdb
# pdb.set_trace()
mod2xtl = new_env()


with open('moduli_alias.csv', 'rb') as f:
    lines = f.read().split('\n')
    for line in lines:
        pv = line.split('=')
        if len(pv) == 2 and pv[0] not in ALIAS:
            ALIAS[pv[0].strip()] = pv[1].strip()

with open('moduli_da_installare_vg7.csv', 'rb') as f:
    hdr = False
    reader = csv.reader(f)
    for row in reader:
        if not hdr:
            hdr = True
            continue
        # print row[1]
        add_elem(mod2xtl, 'vg7', get_realname(row[1]))

with open('code/z0_install_10.conf', 'rb') as f:
    lines = f.read().split('\n')
    for line in lines:
        if line.startswith('install_modules_'):
            pv = line.split('=')
            prm = pv[0]
            ver = prm[16:]
            id = ver.split('.')[0] + ver.split('.')[1]
            rows = pv[1].split(',')
            for row in rows:
                add_elem(mod2xtl, id, get_realname(row))

sort_data(mod2xtl)
print ','.join(mod2xtl['80'])
item = ''
ctrs = {}
for id in VERSIONS:
    ctrs[id] = 0
fd = open('moduli_da_installare.csv', 'w')
while item != '~':
    item, vers = get_next(mod2xtl)
    if item != '~':
        datas = []
        for id in VERSIONS:
            if id in vers:
                datas.append(id)
                ctrs[id] += 1
            else:
                datas.append('')
        print '%-60.60s %3s %3s %3s %3s %3s %3s' % (item,
                                                    datas[0],
                                                    datas[1],
                                                    datas[2],
                                                    datas[3],
                                                    datas[4],
                                                    datas[5])
        line = '"%s",%s,%s,%s,%s,%s,%s\n' % (item,
                                             datas[0],
                                             datas[1],
                                             datas[2],
                                             datas[3],
                                             datas[4],
                                             datas[5])
        fd.write(line)
line = '%-60.60s' % 'TOTALE'
for id in VERSIONS:
    line = '%s %3s' % (line, ctrs[id])
print line
line = 'TOTALE'
for id in VERSIONS:
    line = '%s,%s' % (line, ctrs[id])
fd.write(line)
fd.close()
