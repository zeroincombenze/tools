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
C=a(os.path.dirname(__file__))
D='/home/odoo/devel'
###############
H=o.expanduser('~')
T=j(d(D),'tools')
R=j(d(D),'pypi') if b(D)=='venv_tools' else j(D,'pypi')
W=D if b(D)=='venv_tools' else j(D,'venv')
S='site-packages'
X='scripts'

def isk(P):
 return P.startswith((H,D,C,W)) and p(P) and p(j(P,X)) and f(j(P,'__init__.py')) and f(j(P,'__main__.py'))

L=[C,os.getcwd()]
for B in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):
 for P in [C]+sys.path+os.environ['PATH'].split(':')+[W,R,T,os.getcwd()]:
  P=a(P)
#  if b(P)=='tests' and isk(P):
#   L.append(P)
  if b(P) in (X,'tests','travis','_travis'):
   P=d(P)
  if b(P)==b(d(P)) and f(j(P,'..','setup.py')):
   P=d(d(P))
  elif b(d(C))=='tools' and f(j(P,'setup.py')):
   P=d(P)
  if B==b(P) and isk(P):
   if P not in L:
    L.append(P)
   break
  elif isk(j(P,B,B)):
   if j(P,B,B) not in L:
    L.append(j(P,B,B))
   break
  elif isk(j(P,B)):
   if j(P,B) not in L:
    L.append(j(P,B))
   break
  elif isk(j(P,S,B)):
   if j(P,S,B) not in L:
    L.append(j(P,S,B))
   break
# if os.getcwd() not in L:
#  L.append(os.getcwd())
print(' '.join(L))
