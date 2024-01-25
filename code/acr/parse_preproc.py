#!/usr/bin/python3
# -*- coding: utf-8 -*-

# <legal>
# 'Redemption' Automated Code Repair Tool
#
# Copyright 2023, 2024 Carnegie Mellon University.
#
# NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING
# INSTITUTE MATERIAL IS FURNISHED ON AN 'AS-IS' BASIS. CARNEGIE MELLON
# UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
# AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR
# PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF
# THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY
# KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT
# INFRINGEMENT.
#
# Licensed under a MIT (SEI)-style license, please see License.txt or
# contact permission@sei.cmu.edu for full terms.
#
# [DISTRIBUTION STATEMENT A] This material has been approved for public
# release and unlimited distribution.  Please see Copyright notice for
# non-US Government use and distribution.
#
# This Software includes and/or makes use of Third-Party Software each
# subject to its own license.
#
# DM23-2165
# </legal>

##############################################################################
# This file's purpose is to provide source-code locations (of things such as
# preprocessor conditional-compilation directives) that we need but aren't
# provided in Clang's JSON AST.
##############################################################################

import pprint
import copy
import sys
import os
import pdb
import re
from collections import namedtuple

stop = pdb.set_trace

def flatten_list_rec(L):
    def aux_flatten(L):
        for item in L:
            if isinstance(item, list):
                for subitem in aux_flatten(item):
                    yield subitem
            else:
                yield item
    return list(aux_flatten(L))

Blob = "Blob"
IdToken = namedtuple("IdToken", ['text', 'start', 'end'])
PuncToken = namedtuple("PuncToken", ['text', 'start'])
CommentToken = namedtuple("CommentToken", ['text', 'start', 'end'])
NewlineToken = namedtuple("NewlineToken", ['start'])
#ParenExpr = namedtuple("ParenExpr", ['subexprs', 'start', 'end'])
#MacroArg = namedtuple("MacroArg", ['subexprs', 'start', 'end'])
#MacroCall = namedtuple("MacroCall", ['name', 'args', 'start', 'end', 'in_parens'])

def get_punc_text(tok):
    if not isinstance(tok, PuncToken):
        return None
    else:
        return tok.text

class MacroParser(object):
    def __init__(self, text):
        self.i = 0
        self.text = text
        self.len_text = len(text)
        self.cur_tok = None
        self.peekahead_tok = None

    def init_token_reader(self):
        self.advance_token()
        self.advance_token()

    def advance_token(self):
        self.cur_tok = self.peekahead_tok
        allow_blob = (self.peekahead_tok != Blob)
        while self.i < self.len_text:
            ret = self.try_advance_token()
            if not(ret is None) and (allow_blob or not(ret is Blob)):
                self.peekahead_tok = ret
                return
        self.peekahead_tok = None
        return None

    def try_advance_token(self):
        start = self.i
        text = self.text
        if text[self.i:self.i+2] == b"//":
            try:
                prev_char = None
                while True:
                    if not(self.i < self.len_text):
                        return None
                    cur_char = text[self.i:self.i+1]
                    if cur_char == b'\n' and prev_char != b'\\':
                        break
                    self.i += 1
                    prev_char = cur_char
            except IndexError:
                pass
            return CommentToken(text[start:self.i], start, self.i)
        if text[self.i:self.i+2] == b"/*":
            self.i += 2
            while text[self.i:self.i+2] != b'*/':
                if not(self.i < self.len_text):
                    return None
                self.i += 1
            self.i += 2
            return CommentToken(self.text[start : self.i], start, self.i)
            return None
        m = re.compile(b"[A-Za-z0-9_]+").match(text, self.i)
        if m:
            assert(m.start() == self.i)
            self.i = m.end()
            return IdToken(m.group(), start, self.i)
        if text[self.i:self.i+1] in [b'"', b"'"]:
            quot = text[self.i : self.i+1]
            self.i += 1
            while not(text[self.i : self.i+1] == quot and text[self.i - 1 : self.i] != b'\\'):
                if not(self.i < self.len_text):
                    return None
                self.i += 1
            self.i += 1
            return Blob
        if text[self.i : self.i+1] in [b'\n']:
            self.i += 1
            return NewlineToken(start)
        if text[self.i : self.i+1] in [b' ', b'\t', b'\r']:
            self.i += 1
            return None
        if text[self.i : self.i+1] in [b',', b'(', b')', b'#']:
            self.i += 1
            return PuncToken(text[start : start+1], start)
        self.i += 1
        return Blob

    def parse_toplevel(self):
        assert(self.cur_tok == None)
        self.init_token_reader()
        directives = []
        comments = []
        newlines = []
        while (self.cur_tok != None):
            if get_punc_text(self.cur_tok) == b"#":
                start = self.cur_tok.start
                self.advance_token()
                if isinstance(self.cur_tok, IdToken):
                    tok_text = b"#" + self.cur_tok.text
                    if sys.version_info.major >= 3:
                        tok_text = tok_text.decode("utf-8")
                    directives.append(start)
            elif isinstance(self.cur_tok, CommentToken):
                #print(self.cur_tok)
                comments.append(self.cur_tok[1:3])
            elif isinstance(self.cur_tok, NewlineToken):
                newlines.append(self.cur_tok.start)
            self.advance_token()
        return {"directives": directives, "comments": comments, "newlines": newlines}


def read_whole_file(filename):
    with open(filename, 'rb') as content_file:
        return content_file.read()

def parse_file(filename):
    file_contents = read_whole_file(filename)
    macparser = MacroParser(file_contents)
    return macparser.parse_toplevel()

def main():
    filename = sys.argv[1]
    pprint.pprint(parse_file(filename))

if __name__ == "__main__":
    main()

