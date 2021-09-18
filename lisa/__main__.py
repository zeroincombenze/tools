#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from .scripts.main import main as internal_main


if __name__ == "__main__":
    sys.exit(internal_main())
