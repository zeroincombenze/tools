# flake8: noqa - pylint: skip-file
# H=HOME
# C=cwd()
# T=~/tools
# W=venv
# V=~/venv
# R=~/pypi
# L=[...]
# D='/home/odoo/devel'
##############
import pdb
pdb.set_trace()
import os,sys
o=os.path
a=o.abspath
j=o.join
d=o.dirname
b=o.basename
f=o.isfile
p=o.isdir
###############
C=os.path.dirname(__file__)
D='/home/odoo/devel'
###############
H=o.expanduser('~')
T=j(d(D), 'tools')
R=j(d(D),'pypi') if b(D)=='venv_tools' else j(D,'pypi')
W=D if b(D)=='venv_tools' else j(D,'venv')
def apl(L,P,B):
 if P:
  if p(j(P,B,B)) and p(j(P,B,B,'script')) and f(j(P,B,B,'__init__')):
   L.append(j(P,B,B))
   return 1
  elif j(P,B):
   L.append(j(P,B))
   return 1
 return 0
L=[C]
if b(C) in ('scripts','tests','travis','_travis'):
 C=a(j(C,'..'))
 L.append(C)
if b(C)==b(d(C)) and f(j(C,'..','setup.py')):
 C=a(j(C,'..','..'))
elif b(d(C))=='tools' and f(j(C,'setup.py')):
 C=a(j(C,'..'))
P=os.environ['PATH'].split(':')
V= ''
for X in sys.path:
 if not p(T) and p(j(X,'tools')):
  T=j(X,'tools')
 if not V and b(X)=='site-packages':
  V=X
for B in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):
 if p(j(C,B)) or p(j(C,b(C),B)):
  F=apl(L,C,B)
 else:
  F=0
  for X in P:
   if p(j(X,B)):
    F=apl(L,X,B)
    break
  if not F:
   F=apl(L,V,B)
  if not F:
   apl(L,T,B)
L=L+[os.getcwd()]+P
p=set()
pa=p.add
p=[x for x in L if x and x.startswith((H,D,C)) and not (x in p or pa(x))]
print(' '.join(p))
