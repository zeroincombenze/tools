#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import pdb
import sys

if __name__ == "__main__":
    if sys.argv[1] == "-V":
        print("0.2.0")
    elif sys.argv[1] == "-v":
        print("0.2.1")
    elif sys.argv[1] == "--version":
        print("0.2.2")
