#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import colorama
from colorama import Fore, Style, Back

import prettyxml.xml as xml

colorama.init()

class XmlPrettifier:
    def __init__(self, xml_text: str):
        self._indent = 0
        self._xml_text = xml_text

        self.color_tag_open = Fore.LIGHTGREEN_EX
        self.color_tag_close = Fore.LIGHTGREEN_EX
        self.wrap_width = 100

    def _println(self, val):
        dt = ' ' * 2 * self._indent + val
        print(dt)

    def _walk(self):
        for el in xml.fromstring(self._xml_text):
            if isinstance(el, xml.Declaration):
                self._walk_declaration(el)
            else:
                self._walk_element(el)

    def _walk_declaration(self, obj: xml.Declaration):
        text = Fore.LIGHTCYAN_EX
        text += '<?{}'.format(obj.tag)
        for attr in obj.attrib:
            text += ' {}="{}"'.format(attr.name, attr.value)
        text += '?>' + Fore.RESET
        self._println(text)

    def _walk_element(self, obj: xml.Element):
        text = self.color_tag_open
        text += '<{}'.format(obj.tag)
        text += Fore.RESET

        for attr in obj.attrib:
            text += ' '
            text += Fore.LIGHTYELLOW_EX + attr.name
            text += Fore.WHITE + '="'
            text += Fore.LIGHTWHITE_EX + attr.value
            text += Fore.WHITE + '"' + Fore.RESET

        items = obj.items

        if items:
            text += Fore.LIGHTGREEN_EX + '>' + Fore.RESET
            if len(items) == 1 and isinstance(items[0], xml.TextNode):
                text_node = items[0]
                if len(text_node.value) < self.wrap_width:
                    text += text_node.value + self.color_tag_close + '</{}>'.format(obj.tag) + Fore.RESET
                    self._println(text)
                    return
                else:
                    self._println(text)
                    self._indent += 1
                    self._walk_text_node(text_node)
                    self._indent -= 1
            else:
                self._println(text)
                self._indent += 1
                for item in items:
                    self._walk_element(item)
                self._indent -= 1
        else:
            text += Fore.LIGHTGREEN_EX + '/>' + Fore.RESET
            self._println(text)
            return
        self._println(self.color_tag_close + '</{}>'.format(obj.tag) + Fore.RESET)

    def _walk_text_node(self, obj):
        self._println(obj.value)

    def print(self):
        self._walk()


