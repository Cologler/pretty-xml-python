#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from prettyxml.printer import Printer
import prettyxml.xml as xml

@Printer.register(xml.Declaration)
def print_declaration(printer: Printer, obj: xml.Declaration):
    printer.cyan('<?')
    printer.lightcyan('xml').write(' ')
    attribs = ' '.join(['{}="{}"'.format(attr.name, attr.value) for attr in obj.attrib])
    printer.lightcyan(attribs)
    printer.cyan('?>').endline()


@Printer.register(xml.DocType)
def _walk_doctype(printer: Printer, obj: xml.DocType):
    printer.cyan('<!')
    printer.lightcyan('DOCTYPE').write(' ')
    attribs = ' '.join([str(attr) for attr in obj.childs])
    printer.lightcyan(attribs)
    printer.cyan('>').endline()


@Printer.register(xml.Element)
def _walk_element(printer: Printer, obj: xml.Element):
    wrap_width = 100

    printer.green('<')
    printer.lightgreen(obj.tag)

    for attr in obj.attrib:
        printer.write(' ')
        printer.lightyellow(attr.name)
        printer.white('="')
        printer.lightwhite(attr.value)
        printer.white('"')

    items = obj.items

    if items:
        printer.green('>')

        if len(items) == 1 and isinstance(items[0], xml.TextNode):
            text_node = items[0]
            if len(text_node.value) < wrap_width:
                printer.visit(text_node)
            else:
                printer.endline()
                with printer.indent() as subprinter:
                    subprinter.visit(text_node)
                printer.endline()
        else:
            printer.endline()
            with printer.indent() as subprinter:
                for item in items:
                    subprinter.visit(item)

        printer.green('</')
        printer.lightgreen(obj.tag)
        printer.green('>').endline()
    else:
        printer.green('/>').endline()


@Printer.register(xml.TextNode)
def _walk_textnode(printer: Printer, obj: xml.TextNode):
    if not obj.value.isspace():
        printer.write(obj.value)


@Printer.register(xml.XmlDoc)
def _walk_xmldoc(printer: Printer, obj: xml.XmlDoc):
    for node in obj.nodes:
        printer.visit(node)


class XmlPrettifier:
    def __init__(self, xml_text: str):
        self._xml_text = xml_text

    def print(self):
        xmldoc = xml.XmlDoc.fromstring(self._xml_text)
        Printer().visit(xmldoc)
