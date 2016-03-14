#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
@ Autor: [[Usuário:Danilo.mac]]
@ Licença: GNU General Public License 2.0 (GPLv2)
"""

import pywikibot, css, re, time, codecs

# Ao ativar o modo testar a configuração é lida de arquivar.css na mesma pasta e as
# edições que seriam feitas salvas em teste.txt, nenhuma edição é feita na Wikipédia.
testar = False

site = pywikibot.Site()
reDate = re.compile(ur'min de (\d\d?) de (\S+) de (20\d\d) \(UTC\)')
months = {u'janeiro': '01', u'fevereiro': '02', u'março': '03', u'abril': '04', u'maio': '05', u'junho': '06',
         u'julho': '07', u'agosto': '08', u'setembro': '09', u'outubro': '10', u'novembro': '11', u'dezembro': '12'}
fdate = {'%Y': lambda d: d[0:4], '%y': lambda d: d[2:4], '%m': lambda d: d[4:6],
  '%M': lambda d: [m[0][0:3] for m in months.items() if m[1] == d[4:6]][0],
  '%F': lambda d: [m[0] for m in months.items() if m[1] == d[4:6]][0]}
if testar:
  test = u'# Teste de arquivo.py #\n'

# Lê a configuração
if not testar:
  config = pywikibot.Page(site, u'Usuário:ArquivoBot/arquivar.css').get()
else:
  with codecs.open('arquivar.css', 'r', 'utf-8') as f:
    config = f.read()
config = dict((page, conf) for page, conf in css.iteritems(config) if 'dias' in conf and 'arquivo' in conf)

# Processamento
for title in config:
  if testar:
    test += u'### {} # arquivo: {} # dias: {} ###\n'.format(title, config[title]['arquivo'], config[title]['dias'])
  page = pywikibot.Page(site, title)
  permonth = bool(re.search(ur'%[mMF]', config[title]['arquivo']))
  if page.namespace().id not in (4, 5): # Apenas domínio Wikipédia
    continue
  archiveTime = int(time.strftime('%Y%m%d', time.localtime(time.time() - int(config[title]['dias']) * 86400)))
  header = u'cabeçalho' in config[title] and config[title][u'cabeçalho'] or u''
  archive = {}
  try:
    text = page.get()
  except pywikibot.NoPage:
    continue
  top = re.search(ur'(?s)^.*?(?=\n==)', text)
  page.text = top and top.group(0) or u''

  # Verifica a última data encontrada em cada seção e define se arquiva ou não
  for section in re.findall(ur'(?s)\n==.*?(?=\n==|$)', text):
    dates = reDate.findall(section)
    if not dates or int(dates[-1][2] + months[dates[-1][1]] + u'{:0>2}'.format(dates[-1][0])) > archiveTime:
      page.text += section
      continue
    month = dates[-1][2] + (permonth and months[dates[-1][1]] or '')
    if month in archive:
      archive[month] += section
    else:
      archive[month] = section

  # Salva a página após remover as seções a arquivar
  if testar:
    test += u'\n###### {} ({}) ######\n'.format(page.title(), u'Bot: arquivando {} com mais de {} dias sem comentários'.format(u':Pedidos' in title and u'pedidos' or u'tópicos', config[title]['dias'])) + page.text
  else:
    page.save(u'Bot: arquivando {} com mais de {} dias sem comentários'.format(u':Pedidos' in title and u'pedidos' or u'tópicos', config[title]['dias']))
  revid =  page.latestRevision()

  # Salva as seções a arquivar nas páginas de arquivo
  for month in archive:
    page = pywikibot.Page(site, re.sub(ur'%[YymMF]', lambda m: fdate[m.group(0)](month), config[title]['arquivo']))
    try:
      page.text = page.get()
    except pywikibot.NoPage:
      page.text = header
    page.text += archive[month]
    page.text = re.sub(ur'\{\{([Bb]loqueiorespondido|[Rr]espondido)\|', ur'{{subst:\1|', page.text)
    if testar:
      test += u'\n###### {} ({}) ######\n'.format(page.title(), u'arquivando [[{}]] ([[Especial:Diff/{}|dif]])'.format(title, revid)) + page.text
    else:
      page.save(u'Bot: arquivando [[{}]] ([[Especial:Diff/{}|dif]])'.format(title, revid))

if testar:
  with codecs.open('teste.txt', 'w', 'utf-8') as f:
    f.write(test)
