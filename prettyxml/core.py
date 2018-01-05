#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from colorama import Fore

from prettyxml.printer import Printer
import prettyxml.xml as xml

@Printer.register(xml.Declaration)
def print_declaration(printer: Printer, obj: xml.Declaration):
    attribs = ' '.join(['{}="{}"'.format(attr.name, attr.value) for attr in obj.attrib])
    text = '<?{} {}?>'.format('xml', attribs)
    printer.lightcyan(text).endline()


@Printer.register(xml.DocType)
def _walk_doctype(printer: Printer, obj: xml.DocType):
    attribs = ' '.join([str(attr) for attr in obj.childs])
    text = '<!DOCTYPE {}>'.format(attribs)
    printer.lightcyan(text).endline()


@Printer.register(xml.Element)
def _walk_element(printer: Printer, obj: xml.Element):
    wrap_width = 100

    text = Fore.LIGHTGREEN_EX
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
            if len(text_node.value) < wrap_width:
                text += text_node.value + Fore.LIGHTGREEN_EX + '</{}>'.format(obj.tag) + Fore.RESET
                printer.write(text).endline()
                return
            else:
                printer.write(text).endline()
                with printer.indent() as subprinter:
                    subprinter.visit(text_node)
        else:
            printer.write(text).endline()
            with printer.indent() as subprinter:
                for item in items:
                    subprinter.visit(item)
    else:
        printer.write(text)
        printer.lightgreen('/>').endline()
        return

    printer.lightgreen('</{}>'.format(obj.tag)).endline()


@Printer.register(xml.TextNode)
def _walk_textnode(printer: Printer, obj: xml.TextNode):
    printer.write(obj.value).endline()


class XmlPrettifier:
    def __init__(self, xml_text: str):
        self._printer = Printer()
        self._xml_text = xml_text

    def print(self):
        for node in xml.fromstring(self._xml_text):
            self._printer.visit(node)
