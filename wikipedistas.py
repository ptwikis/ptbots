#!/usr/bin/python
# -*- coding: utf8 -*-

import oursql, os
import pywikibot
from datetime import date

def main():
  def tempo(t):
    delta = date.today() - date(int(t[0:4]), int(t[4:6]), int(t[6:8]))
    meses = delta.days / 30
    return meses < 12 and (meses == 0 and '0' or meses == 1 and u'1 mês' or str(meses) + ' meses') or \
           delta.days / 730 and str(delta.days / 365) + ' anos' or '1 ano'
  grupos = [('sysop', u'A'), ('bureaucrat', u'B'), ('oversight', u'S'), ('checkuser', u'V'), ('eliminator', u'E'), ('rollbacker', u'R'), ('autoreviewer', u'a')]
  connection = oursql.connect(db='ptwiki_p', host='ptwiki.labsdb', read_default_file=os.path.expanduser('~/replica.my.cnf'))
  c = connection.cursor()
  c.execute(u'''SELECT
 USUÁRIO,
 GROUP_CONCAT(ug_group SEPARATOR '|') AS GRUPOS,
 EDIÇÕES,
 PRIMEIRA,
 ÚLTIMA,
 CRIADOS
 FROM
  (SELECT
   rev_user,
   rev_user_text AS USUÁRIO,
   COUNT(*) AS EDIÇÕES,
   SUM(CASE WHEN rev_parent_id = 0 AND page_is_redirect = 0 THEN 1 ELSE 0 END) AS CRIADOS,
   MIN(rev_timestamp) AS PRIMEIRA,
   MAX(rev_timestamp) AS ÚLTIMA
   FROM revision_userindex LEFT JOIN page ON rev_page = page_id
   WHERE rev_user != 0 AND page_namespace = 0
   GROUP BY USUÁRIO
   HAVING EDIÇÕES > 2000
  ) u
 LEFT JOIN user_groups ON rev_user = ug_user
 GROUP BY USUÁRIO
 HAVING GRUPOS != 'bot'
 ORDER BY USUÁRIO''')
  lista = c.fetchall()
  print len(lista), 'linhas'
  texto = u"""Lista dos wikipedistas com mais de 2000 edições no domínio principal. Última atualização em {{subst:#time:j "de" F "de" Y}}.

* '''Grupos:''' grupos a que o usuário pertence: administrador (A), burocrata(B), eliminador (E), reversor (R), autorrevisor (a), verificador (V), supervisor (S).
* '''Edições:''' número de edições no domínio principal.
* '''Primeira:''' há quantos meses ou anos foi a primeira edição no domínio principal.
* '''Última:''' há quantos meses ou anos foi a última edição no domínio principal, 0 (zero) indica que foi nos últimos 30 dias.
* '''Criados:''' Artigos criados no domínio principal, desconsiderando os redirecionamentos.

"""
  tabela = u'{|class="wikitable sortable"\n|-\n!Wikipedista||Grupos||Edições||Primeira||Última||Criados'
  for l in lista:
    tabela += u'\n|-\n|{{{{u|{}}}}}||{}||{}||{}||{}||{}'.format(l[0].decode('utf-8'), u''.join(g[1] for g in grupos if g[0] in l[1]), l[2], tempo(l[3]), tempo(l[4]), l[5])
  tabela += u'\n|}'
  pywikibot.Page(pywikibot.getSite(), u'Usuário:Danilo.mac/Wikipedistas com mais de 2000 edições').put(texto + tabela, comment=u'Bot: Atualizando', minorEdit=False)

if __name__ == '__main__':
  main()
