from __future__ import print_function

import sys
import os.path
import os
# import pdb

# pdb.set_trace()
fl_tgt = sys.argv[1]
if len(sys.argv) > 2:
    opt_cont = sys.argv[2]
else:
    opt_cont = ""
fl_hist = fl_tgt + '.tracehistory'
fl_noted = './cover/' + os.path.basename(fl_tgt) + ',cover'
fl_noted_tmp = './cover/' + os.path.basename(fl_tgt) + ',cover.tmp'
fd_i = open(fl_hist, 'r')
res = fd_i.read().split('\n')
fd_i.close()
annotate = {}
max_lines = 0
for ln in res:
    if ln:
        i = ln.find('[', 4)
        j = ln.find(']', 6)
        lineno = int(ln[i+1:j]) - 1
        if lineno > max_lines:
            max_lines = lineno
        annotate[lineno] = ln[j+1:].strip()
if opt_cont:
    try:
        fd_i = open(fl_noted, 'r')
    except BaseException:
        opt_cont = ''
        fd_i = open(fl_tgt, 'r')
else:
    fd_i = open(fl_tgt, 'r')
fd_o = open(fl_noted_tmp, 'w')
lineno = 0
line_chks = 0
ctr_if = 0
ctr_do = 0
stack_if = {}
stack_do = {}
ln = fd_i.readline()
while ln:
    lineno += 1
    if opt_cont:
        tag = ln[0:2]
        ln = ln[2:]
    else:
        tag = '  '
    if lineno in annotate:
        tag = '! '
    if ln.strip()[0:1] == '#' or ln.strip() == '':
        tag = '! '
    elif ln.strip()[0:5] == 'else ' or ln.strip() == 'else':
        if stack_if[ctr_if]:
            tag = '! '
    elif ln.strip()[0:5] == 'elif ' or ln.strip() == 'elif':
        if stack_if[ctr_if]:
            tag = '! '
    elif ln.strip()[0:3] == 'fi ' or ln.strip() == 'fi':
        if stack_if[ctr_if]:
            tag = '! '
        if ctr_if > 0:
            ctr_if -= 1
    elif ln.strip()[0:5] == 'done ' or ln.strip() == 'done':
        if stack_do[ctr_do]:
            tag = '! '
        if ctr_do > 0:
            ctr_do -= 1
    if tag == '! ':
        line_chks += 1
    if ln.strip()[0:3] == 'if ':
        ctr_if += 1
        if tag == '! ':
            stack_if[ctr_if] = True
        else:
            stack_if[ctr_if] = False
    elif ln.strip()[0:4] == 'for ' or ln.strip()[0:6] == 'while ':
        ctr_do += 1
        if tag == '! ':
            stack_do[ctr_do] = True
        else:
            stack_do[ctr_do] = False
    ln = tag + ln
    fd_o.write(ln)
    ln = fd_i.readline()
fd_i.close()
fd_o.close()
try:
    os.remove(fl_noted)
except BaseException:
    pass
os.rename(fl_noted_tmp, fl_noted)
print("%s: %d/%d = %d%%" % (fl_tgt,
                            line_chks,
                            lineno,
                            (line_chks * 100) / lineno))
