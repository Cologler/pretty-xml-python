#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

class CharQueue(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read_char(self):
        return self.pop(0)

    def view_char(self) -> str:
        return self[0] if self else None

    def read_until(self, ch) -> str:
        val = ''
        try:
            while not self.view_char() in ch:
                val += self.read_char()
        except BaseException:
            print(val)
            raise
        return val


class Node:
    pass

class Attribute:
    def __init__(self, name, value):
        self._name = name
        self._value = value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @classmethod
    def fromstring(cls, content: CharQueue):
        name = content.read_until('=')
        assert content.read_char() == '='
        assert content.read_char() == '"'
        value = content.read_until('"')
        assert content.read_char() == '"'
        return cls(name, value)

class TextNode(Node):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value


class Element(Node):
    def __init__(self, tag):
        self._tag = tag
        self._attrib = []
        self._items = []

    @property
    def tag(self):
        return self._tag

    @property
    def attrib(self):
        return self._attrib

    @property
    def items(self):
        return self._items

    @classmethod
    def fromstring(cls, content: CharQueue):
        name = content.read_until((' ', '>'))
        if name[0] == '?':
            cls = Declaration
            name = name[1:]
        el = cls(name)

        while content.view_char() == ' ':
            ch = content.read_char()
            ch = content.view_char()
            if ch == '/':
                content.read_char()
                assert content.read_char() == '>'
                return el
            if ch not in ' >':
                el.attrib.append(Attribute.fromstring(content))

        if cls == Declaration:
            assert content.read_char() == '?'
        assert content.read_char() == '>'
        if cls == Declaration:
            return el

        while content:
            if content.view_char() == '<':
                content.read_char()
                if content.view_char() == '/': # end tag
                    assert content.read_char() == '/'
                    end = content.read_until('>')
                    assert content.read_char() == '>'
                    assert end == name
                    break
                else: # sub
                    sub_el = Element.fromstring(content)
                    el.items.append(sub_el)
            else:
                text = TextNode(content.read_until('<'))
                el.items.append(text)

        return el


class Declaration(Element):
    pass


def fromstring(val: str):
    content = CharQueue(val)
    ret = []
    while content:
        ch = content.read_char()
        if ch == '<':
            ret.append(Element.fromstring(content))
        elif ch.isspace():
            continue
        else:
            raise ValueError(ch)
    assert not content
    return ret
