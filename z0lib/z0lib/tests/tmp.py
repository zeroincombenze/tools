#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
U='setup.py'
H=o.expanduser('~')
R=j(D,'pypi')
W=j(D,'venv')
S='site-packages'
X='scripts'
Y=[x for x in sys.path if b(x)==S]
Y=Y[0] if Y else C

def isk(P):
 return P.startswith((H,D,C,W)) and p(P) and p(j(P,X)) and f(j(P,'__init__.py')) and f(j(P,'__main__.py'))
def adk(L,P):
 if p(j(P,X)) and j(P,X) not in L:
  L.append(j(P,X))
 if P not in L:
  L.append(P)

L=[C]
for B in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):
 for P in [C]+os.environ['PATH'].split(':')+[W,R]:
  P=a(P)
  if b(P) in (X,'tests','travis','_travis'):
   P=d(P)
  if b(P)==b(d(P)) and f(j(P,'..',U)):
   P=d(d(P))
  if B==b(P) and isk(P):
   adk(L,P)
   break
  elif isk(j(P,B,B)):
   adk(L,j(P,B,B))
   break
  elif isk(j(P,B)):
   adk(L,j(P,B))
   break
  else:
   adk(L, j(Y,B))
adk(L,os.getcwd())
print(' '.join(L))
