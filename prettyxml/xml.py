#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

class FormatError(Exception):
    pass


UNREADABLE_CHARS = {
    '\r': '\\r',
    '\t': '\\t',
    '\n': '\\n',
}

def readableify(char):
    if char is None:
        return 'end of document'
    else:
        return "'{}'".format(UNREADABLE_CHARS.get(char, char))



class WrapedStr(str):
    ''' wrap str into `"{0}"`. '''
    def __str__(self):
        return '"' + self + '"'


class CharQueue(list):
    UNREADABLE_CHARS = {
        '\r': '\\r',
        '\t': '\\t',
        '\n': '\\n',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert len(args) == 1 and isinstance(args[0], str)
        self._lines = args[0].split('\n')
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
        '''
        remove and return first char from queue, also cache it in `self.last`.
        '''
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

    def pop_until(self, callback) -> str:
        ''' pop until `callback(next_char)` return `True` or end. '''
        val = ''
        while True:
            next_char = self.peek_char()
            if next_char is None or callback(next_char):
                break
            val += self.pop_char()
        return val

    def pop_while(self, callback) -> str:
        ''' pop while `callback(next_char)` return `False` or end. '''
        val = ''
        while True:
            next_char = self.peek_char()
            if next_char is None or not callback(next_char):
                break
            val += self.pop_char()
        return val

    def pop_until_visit(self, chars: str) -> str:
        ''' pop until next char in `chars`. '''
        return self.pop_until(lambda ch: ch in chars)

    def pop_while_space(self) -> str:
        ''' pop while next char is `str.isspace()`. '''
        return self.pop_while(lambda ch: ch.isspace())

    def skip_space(self):
        while self.pop_while_space():
            pass

    def cur_info(self):
        ''' return tuple `(lineno, column)`. '''
        return (self._lineno, self._column)

    def assert_next(self, ch: str) -> None:
        ''' pop next char. if next char is not `ch`, raise ValueError. '''
        if self.pop_char() != ch:
            readable_last = readableify(self._last)
            msg = 'except `{}`, got {}.'.format(ch, readable_last)
            msg += ' (line {}, column {})'.format(self._lineno, self._column)
            if self._last is not None:
                msg += '\n'
                msg += self._lines[self._lineno - 1] + '\n'
                msg += ' ' * (self._column - 1) + '^'
            raise FormatError(msg)


class Attribute:
    def __init__(self, name, value):
        self._name = name
        self._value = value

    def __repr__(self):
        return "Attr('{}'='{}')".format(self._name, self._value)

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @classmethod
    def fromstring(cls, content: CharQueue):
        name = content.pop_until_visit('=')
        content.assert_next('=')
        content.assert_next('"')
        value = content.pop_until_visit('"')
        content.assert_next('"')
        return cls(name, value)


class Node:
    @classmethod
    def _fromstring_parse_attrs(cls, content: CharQueue):
        while content.pop_while_space():
            ch = content.peek_char()
            if ch == '/':
                break
            if ch not in ' >':
                yield Attribute.fromstring(content)

    @classmethod
    def fromstring(cls, content: CharQueue):
        name = content.pop_until(lambda ch: ch in '>' or ch.isspace())
        if name.startswith('?'):
            assert name[1:] == 'xml'
            return Declaration.fromstring(content)
        elif name.startswith('!DOCTYPE'):
            return DocType.fromstring(content)
        else:
            return Element.fromstring(content, name)


class TextNode(Node):
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return "Text('{}')".format(self._value)

    @property
    def value(self):
        return self._value


class Declaration(Node):
    ''' like `<?xml version='1.0'?>`. '''

    def __init__(self):
        self._attrib = []

    def __repr__(self):
        return "Decl('{}')".format(self._attrib)

    @property
    def attrib(self):
        return self._attrib

    @classmethod
    def fromstring(cls, content: CharQueue):
        el = cls()
        el.attrib.extend(cls._fromstring_parse_attrs(content))
        content.assert_next('?')
        content.assert_next('>')
        return el


class DocType(Node):
    ''' like `<!DOCTYPE VOTABLE SYSTEM "http://us-vo.org/xml/VOTable.dtd">`. '''

    def __init__(self):
        self._childs = []

    def __repr__(self):
        return "DocType(...)"

    @property
    def childs(self):
        return self._childs

    @classmethod
    def fromstring(cls, content: CharQueue):
        el = cls()

        while content.pop_while_space():
            value = content.pop_until_visit(' ">')

            next_char = content.peek_char()

            if next_char == ' ':
                el.childs.append(value)
                continue

            elif next_char == '>':
                el.childs.append(value)
                break

            elif next_char == '"':
                content.pop_char()
                assert not value
                inner_text = content.pop_until_visit('"')
                content.assert_next('"')
                el.childs.append(WrapedStr(inner_text))

            else:
                raise NotImplementedError

        content.assert_next('>')
        return el


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
    def fromstring(cls, content: CharQueue, name):
        el = cls(name)

        el.attrib.extend(cls._fromstring_parse_attrs(content))

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
                    end = content.pop_until_visit('>')
                    content.assert_next('>')
                    assert end == name, '{} != {}'.format(end, name)
                    break
                else: # sub
                    sub_el = Node.fromstring(content)
                    subitems.append(sub_el)
            else:
                text = TextNode(content.pop_until_visit('<'))
                subitems.append(text)

        if len(subitems) > 1:
            for tn in (x for x in subitems if isinstance(x, TextNode)):
                assert tn.value.isspace()
            subitems = [x for x in subitems if not isinstance(x, TextNode)]
        el.items.extend(subitems)
        return el


class XmlDoc:
    def __init__(self):
        self.nodes = []

    @classmethod
    def fromstring(cls, val: str):
        el = XmlDoc()
        content = CharQueue(val)
        ret = []
        while content:
            content.skip_space()
            if not content:
                break
            content.assert_next('<')
            el.nodes.append(Node.fromstring(content))
        assert not content
        return el
