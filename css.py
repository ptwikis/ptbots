# -*- coding: utf-8 -*-
"""
@ Autor: [[Usuário:Danilo.mac]]
@ Licença: GNU General Public License 2.0 (GPLv2)

Script para ler configurações escritas em formato .css
"""
import re

def iteritems(text):
    """
    Analisador léxico baseado em regex
    """
    reTokens = re.compile(ur'''\s*
        (?:
           (?P<quote>["'])|
           (?P<open>\{)|
           (?P<close>\})|
           (?P<escape>\\)|
           (?P<colon>:)|
           (?P<comma>,)|
           (?P<comment>/\*)|
           (?P<word>[\w\d]+|\S)
        )''', re.X)
    reEndCom = re.compile(ur'\*/')

    def fword(w):
        w = w.strip()
        return w[0] + w[-1] in ('""', "''") and w[1:-1] or w

    quote, escape, word, key = (None,
     False,
     u'',
     u'')
    name, item = u'', {}
    c = 0
    m = reTokens.match(text)
    while True:
        c += 1
        if not m or c > 50000:
            break
        if not quote and m.lastgroup == 'comment':
            e = reEndCom.search(text, m.end())
            if not e:
                break
            m = reTokens.match(text, e.end())
            c += 1
            if c > 2:
                return
        if escape:
            escape = False
        if m.lastgroup == 'quote':
            if not quote:
                quote = m.group('quote')
            elif not escape and quote == m.group('quote'):
                quote = None
        elif m.lastgroup == 'escape':
            escape = True
        if m.lastgroup in ('word', 'quote', 'escape') or quote or not name and m.lastgroup != 'open':
            word += word and m.group(0) or m.group(m.lastgroup)
            if quote:
                m = reTokens.match(text, m.end())
                continue
        elif not name and m.lastgroup == 'open':
            name, word = fword(word), u''
        elif name and m.lastgroup == 'colon':
            key, word = fword(word), u''
        elif name and m.lastgroup in ('comma', 'close'):
            if key and word:
                item[key] = fword(word)
                key, word = (u'', u'')
            if m.lastgroup == 'close':
                yield (name, item)
                name, item = u'', {}
        else:
            print u'um tokem não foi corretamente processado:', m.lastgroup
        m = reTokens.match(text, m.end())


def items(text):
    return dict(((name, item) for name, item in iteritems(text)))
