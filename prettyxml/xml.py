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
        self._last = None

    @property
    def last(self):
        ''' the lase poped char. '''
        return self._last

    def pop_char(self):
        ''' remove first char from queue, also cache it in `self.last`.'''
        self._ = self.pop(0)
        return self._

    def peek_char(self) -> str:
        return self[0] if self else None

    def pop_until(self, chs: str) -> str:
        ''' pop until next char in `chs`. '''
        val = ''
        while not self.peek_char() in chs:
            val += self.pop_char()
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
        name = content.pop_until('=')
        assert content.pop_char() == '='
        assert content.pop_char() == '"'
        value = content.pop_until('"')
        assert content.pop_char() == '"'
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
        name = content.pop_until(' >')
        if name[0] == '?':
            cls = Declaration
            name = name[1:]
        el = cls(name)

        while content.peek_char() == ' ':
            ch = content.pop_char()
            ch = content.peek_char()
            if ch == '/':
                content.pop_char()
                assert content.pop_char() == '>'
                return el
            if ch not in ' >':
                el.attrib.append(Attribute.fromstring(content))

        if cls == Declaration:
            assert content.pop_char() == '?'
            assert content.pop_char() == '>'
            return el

        content.pop_char()
        if content.last == '/': # end tag
            assert content.pop_char() == '>'
            return el

        while content:
            if content.peek_char() == '<':
                content.pop_char()
                if content.peek_char() == '/': # end tag
                    assert content.pop_char() == '/'
                    end = content.pop_until('>')
                    assert content.pop_char() == '>'
                    assert end == name
                    break
                else: # sub
                    sub_el = Element.fromstring(content)
                    el.items.append(sub_el)
            else:
                text = TextNode(content.pop_until('<'))
                el.items.append(text)

        return el


class Declaration(Element):
    pass


def fromstring(val: str):
    content = CharQueue(val)
    ret = []
    while content:
        ch = content.pop_char()
        if ch == '<':
            ret.append(Element.fromstring(content))
        elif ch.isspace():
            continue
        else:
            raise ValueError(ch)
    assert not content
    return ret
