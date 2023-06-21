#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

PATH = os.environ["PATH"]
NEW_PATH = []
for path in PATH.split(":"):
    if " " not in path:
        NEW_PATH.append(path)
print(":".join(NEW_PATH))
