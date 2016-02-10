import sys
import os.path

fl_tgt = sys.argv[1]
fl_hist = fl_tgt + '.tracehistory'
fl_noted = './cover/' + os.path.basename(fl_tgt) + ',cover'
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
fd_i = open(fl_tgt, 'r')
fd_o = open(fl_noted, 'w')
lineno = 0
line_chks = 0
ln = fd_i.readline()
while ln:
    lineno += 1
    if lineno in annotate:
        tag = '! '
        line_chks += 1
    elif ln.strip()[0:1] == '#' or ln.strip()[0:2] == 'fi' or ln.strip() == '':
        tag = '! '
        line_chks += 1
    else:
        tag = '  '
    ln = tag + ln
    fd_o.write(ln)
    ln = fd_i.readline()
fd_i.close()
fd_o.close()
print "%d/%d = %d%%" % (line_chks, lineno, (line_chks * 100) / lineno)
