with open('./tmp.py', 'r') as fd:
    tgt = 'C=\'"$TDIR"\'\\nD=\'"$HOME_DEV"\'\\n'
    sts = 0
    for ln in fd.read().split('\n'):
        if ln and ln.startswith('##'):
            sts = not sts
        elif ln and ln.startswith('#') or 'pdb' in ln:
            continue
        elif sts:
            tgt += '%s\\n' % ln
print(tgt)