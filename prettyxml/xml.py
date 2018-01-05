#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

class FormatError(Exception):
    pass

class CharQueue(list):
    UNREADABLE_CHARS = {
        '\r': '\\r',
        '\t': '\\t',
        '\n': '\\n',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last = None
        self._lineno = 1
        self._column = 1

    def __repr__(self):
        return ''.join(self)

    @property
    def last(self):
        ''' the last poped char. '''
        return self._last

    def pop_char(self):
        ''' remove and return first char from queue, also cache it in `self.last`.'''
        self._last = self.pop(0)
        if self._last == '\n':
            self._lineno += 1
            self._column = 1
        else:
            self._column += 1
        return self._last

    def peek_char(self) -> str:
        ''' return the first char from queue. '''
        return self[0] if self else None

    def pop_until(self, chs: str) -> str:
        ''' pop until next char in `chs`. '''
        val = ''
        while not self.peek_char() in chs:
            val += self.pop_char()
        return val

    def cur_info(self):
        ''' return tuple `(lineno, column)`. '''
        return (self._lineno, self._column)

    def assert_next(self, ch: str) -> None:
        ''' pop next char. if next char is not `ch`, raise ValueError. '''
        if self.pop_char() != ch:
            readable_last = self.UNREADABLE_CHARS.get(self._last, self._last)
            msg = 'except `{}`, got `{}`'.format(ch, readable_last)
            msg += ' (line {}, column {})'.format(self._lineno, self._column)
            raise FormatError(msg)

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
        content.assert_next('=')
        content.assert_next('"')
        value = content.pop_until('"')
        content.assert_next('"')
        return cls(name, value)

class TextNode(Node):
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return "TextNode('{}')".format(self._value)

    @property
    def value(self):
        return self._value


class Element(Node):
    def __init__(self, tag):
        self._tag = tag
        self._attrib = []
        self._items = []

    def __repr__(self):
        return "Element(tag='{}', '{}')".format(self._tag, self._items)

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

        while content.peek_char() in ' \r\n':
            ch = content.pop_char()
            ch = content.peek_char()
            if ch == '/':
                break
            if ch not in ' >':
                el.attrib.append(Attribute.fromstring(content))

        if cls == Declaration:
            content.assert_next('?')
            content.assert_next('>')
            return el

        if content.peek_char() == '/': # end tag
            content.assert_next('/')
            content.assert_next('>')
            return el
        else:
            content.assert_next('>')

        subitems = []
        while content:
            if content.peek_char() == '<':
                content.pop_char()
                if content.peek_char() == '/': # end tag
                    content.assert_next('/')
                    end = content.pop_until('>')
                    content.assert_next('>')
                    assert end == name, '{} != {}'.format(end, name)
                    break
                else: # sub
                    sub_el = Element.fromstring(content)
                    subitems.append(sub_el)
            else:
                text = TextNode(content.pop_until('<'))
                subitems.append(text)

        if len(subitems) > 1:
            for tn in (x for x in subitems if isinstance(x, TextNode)):
                assert tn.value.isspace()
            subitems = [x for x in subitems if not isinstance(x, TextNode)]
        el.items.extend(subitems)
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
