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
N= 'venv_tools'
U='setup.py'
O='tools'
H=o.expanduser('~')
T=j(d(D),O)
R=j(d(D),'pypi') if b(D) == N else j(D, 'pypi')
W=D if b(D) == N else j(D, 'venv')
S='site-packages'
X='scripts'

def isk(P):
 return P.startswith((H,D,C,W)) and p(P) and p(j(P,X)) and f(j(P,'__init__.py')) and f(j(P,'__main__.py'))
def adk(L,P):
 if P not in L:
  L.append(P)

L=[C]
for B in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):
 for P in [C]+sys.path+os.environ['PATH'].split(':')+[W,R,T]:
  P=a(P)
  if b(P) in (X,'tests','travis','_travis'):
   P=d(P)
  if b(P)==b(d(P)) and f(j(P,'..',U)):
   P=d(d(P))
  elif b(d(C))==O and f(j(P,U)):
   P=d(P)
  if B==b(P) and isk(P):
   adk(L,P)
   break
  elif isk(j(P,B,B)):
   adk(L,j(P,B,B))
   break
  elif isk(j(P,B)):
   adk(L,j(P,B))
   break
  elif isk(j(P,S,B)):
   adk(L,j(P,S,B))
   break
adk(L,os.getcwd())
print(' '.join(L))
