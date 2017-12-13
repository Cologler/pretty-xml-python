#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import os
import sys
import traceback
import core

def print_help():
    print('use pipe to input xml content.')

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        if sys.stdin.isatty():
            print_help()
        else:
            xml_content = sys.stdin.read()
            core.XmlPrettifier(xml_content).print()
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    main()
