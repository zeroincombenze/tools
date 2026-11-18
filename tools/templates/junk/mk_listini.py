import csv, openpyxl
XLSX = '/home/antoniov/Documenti/Zeroincombenze srls/Ridix/Listini 1,2,3 x Federica - EXCEL (estrazione 16-11-2026).xlsx'
ALIAS = {'NOME_LISTINO': 'NRLISTINO', 'PREZZO CHF': 'PREZZO'}
wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
for n in (1, 2, 3):
    src = '/mnt/ridix_odoo/RIGHE_LISTINO%d_1-20261007_1200.csv' % n
    dst = '/mnt/ridix_odoo/RIGHE_LISTINO%d-20261118_1115.csv' % n
    with open(src, encoding='utf-8') as f:
        header = next(csv.reader(f, delimiter='|'))
    rows = wb['Listino_%d' % n].iter_rows(values_only=True)
    xhdr = next(rows)
    pos = {}
    for i, h in enumerate(xhdr):
        pos.setdefault(h, i)          # first DESCRIZIONE = article description
    idx = [pos.get(ALIAS.get(h, h)) for h in header]
    missing = [h for h, i in zip(header, idx) if i is None]
    cnt = 0
    with open(dst, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='|', quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')
        w.writerow(header)
        for r in rows:
            if r[pos['CODART']] in (None, ''):
                continue
            out = []
            for i in idx:
                v = None if i is None else r[i]
                if v is None:
                    v = ''
                elif isinstance(v, float) and v.is_integer():
                    v = int(v)
                out.append(v)
            w.writerow(out)
            cnt += 1
    print(dst, cnt, 'rows; empty cols:', missing)
