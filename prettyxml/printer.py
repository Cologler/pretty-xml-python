#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import colorama

colorama.init()

class Printer:
    _TYPED_HANDLERS = {}

    @classmethod
    def register(cls, typ):
        def _wrap(func):
            cls._TYPED_HANDLERS[typ] = func
            return func
        return _wrap

    def __init__(self, **kwargs):
        self._root_printer = kwargs.get('root_printer', self)
        self._indent_level = kwargs.get('indent_level', 0)
        self._indent = '  '
        self._newline = True

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def visit(self, node):
        self._TYPED_HANDLERS[type(node)](self, node)

    def indent(self):
        return Printer(
            indent_level=self._indent_level + 1,
            root_printer=self._root_printer
        )

    def _get_indent(self):
        return self._indent * self._indent_level

    def write(self, text):
        if '\n' in text:
            text = text.replace('\n', '\n' + self._get_indent())
        if self._newline:
            text = self._get_indent() + text
            self._newline = False
        print(text, end='')
        return self

    def endline(self):
        print()
        self._newline = True
        return self

    def coloring(self, text, color):
        return getattr(self, color)(text)

    def black(self, text):
        return self.write(colorama.Fore.BLACK + text + colorama.Fore.RESET)

    def red(self, text):
        return self.write(colorama.Fore.RED + text + colorama.Fore.RESET)

    def green(self, text):
        return self.write(colorama.Fore.GREEN + text + colorama.Fore.RESET)

    def yellow(self, text):
        return self.write(colorama.Fore.YELLOW + text + colorama.Fore.RESET)

    def blue(self, text):
        return self.write(colorama.Fore.BLUE + text + colorama.Fore.RESET)

    def magenta(self, text):
        return self.write(colorama.Fore.MAGENTA + text + colorama.Fore.RESET)

    def cyan(self, text):
        return self.write(colorama.Fore.CYAN + text + colorama.Fore.RESET)

    def white(self, text):
        return self.write(colorama.Fore.WHITE + text + colorama.Fore.RESET)

    def lightblack(self, text):
        return self.write(colorama.Fore.LIGHTBLACK_EX + text + colorama.Fore.RESET)

    def lightred(self, text):
        return self.write(colorama.Fore.LIGHTRED_EX + text + colorama.Fore.RESET)

    def lightgreen(self, text):
        return self.write(colorama.Fore.LIGHTGREEN_EX + text + colorama.Fore.RESET)

    def lightyellow(self, text):
        return self.write(colorama.Fore.LIGHTYELLOW_EX + text + colorama.Fore.RESET)

    def lightblue(self, text):
        return self.write(colorama.Fore.LIGHTBLUE_EX + text + colorama.Fore.RESET)

    def lightmagenta(self, text):
        return self.write(colorama.Fore.LIGHTMAGENTA_EX + text + colorama.Fore.RESET)

    def lightcyan(self, text):
        return self.write(colorama.Fore.LIGHTCYAN_EX + text + colorama.Fore.RESET)

    def lightwhite(self, text):
        return self.write(colorama.Fore.LIGHTWHITE_EX + text + colorama.Fore.RESET)
