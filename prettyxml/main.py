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

def trim_header(content):
    headers = [
        chr(38168) + chr(56511), # utf8 bom on encoding GBK when using `type` command.
    ]
    for header in headers:
        if content.startswith(header):
            content = content[len(header):]
            return content
    return content

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        if sys.stdin.isatty():
            print_help()
        else:
            xml_content = trim_header(sys.stdin.read())
            core.XmlPrettifier(xml_content).print()
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    main()
