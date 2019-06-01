#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Zeroincombenze® unit test library for python programs Regression Test Suite
"""

# import pdb
import os
import os.path
import sys
from zerobug import Z0BUG
import python_plus

__version__ = "0.1.0.1"



def version():
    return __version__

if __name__ == "__main__":
    exit(Z0BUG.main_file(
        Z0BUG.parseoptest(sys.argv[1:],
                          version=version()))
    )
