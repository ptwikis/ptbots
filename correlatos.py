# -*- coding: utf-8 -*-

import pywikibot
import re
from pywikibot import pagegenerators

site = pywikibot.getSite()

predef = pywikibot.Page(site, u'Predefinição:Wikilivros')
gen = pagegenerators.PreloadingGenerator(predef.getReferences(onlyTemplateInclusion=True, namespaces=0))
reLivros = re.compile(ur'\{\{[Ww]ikilivros\|(?: *1 *=)? *([^|}]+)(?:\|(?: *2 *=)? *([^|}]+)[^}]*)?\}\}')

n = 0
for page in gen:
    text = page.get()
    m = reLivros.search(text)
    wp = m.group(1) + (u'/' + m.group(2) if m.group(2) else u'') if m else None
    item = pywikibot.ItemPage.fromPage(page)
    sl = item.sitelinks
    wd = sl[u'ptwikibooks'] if u'ptwikibooks' in sl else None

    #---- teste ----
    r = wp and wp == wd and u'Remover predefinição' or wp and not wd and u'Adicionar ao Wikidata' or u'?'
    print u'|-\n|[[%s]]||%s||%s||%s' % (page.title(), u'[[b:%s]]' % wp if wp else u'?', u'[[b:%s]]' % wd if wd else u'(não tem link)', r)
    n += 1
    if n == 50:
        break
