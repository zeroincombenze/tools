# temporary doc generator
import sys

module = sys.argv[1]
if module == 'os0' or module == 'pytok':
    txt = 'from ' + module + ' import ' + module + '\n'
else:
    txt = 'import ' + module + '\n'
txt += '\n'
txt += 'help(' + module + ')\n'
txt += '\n'

fd = open('wok_doc_tmp.py', 'w')
fd.write(txt)
fd.close()
