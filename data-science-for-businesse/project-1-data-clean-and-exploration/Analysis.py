
# coding: utf-8

# In[1]:


import xml.etree.cElementTree as ET
import re
import csv
import operator

from cleaningData import cleaning, vizualization


# <h1>Os dados coletados, são da cidade do Rio de Janeiro no Brasil</h1>
# <br />
# <p>Links:</p>
# <ul>
#     <li>https://mapzen.com/data/metro-extracts/metro/rio-de-janeiro_brazil/</li>
# </ul>
# <p>O Rio de Janeiro, mais conhecido como a cidade maravillhosa, onde se localza o Cristo Redentor uma das 7 maravilhas do mundo, foi minha escolha para analisar os dados, por que eu admiro aquela cidade, apesar de toda a criminalidade e favelas que lá existem. Lá foi a segunda capital do Brasil, e a cidade em que a família real morou, além de possuir vários pontos turísticos como o Bondinho, Pão de Açucar e Arcos da Lapa</p>
# <p>As primeiras seções do código são para extração dos dados e converter para um dicionário em python</p>
# <h2>Principais Inconsistências</h2>
# <ul>
#     <li>Uso de abreviações para: ruas, rodovias, avenidas ...</li>
#     <li>Digitação inconsitente dos CEPs</li> 
#     <li>Uso de portugues e inglês para o valor de 'key' nas node_tags e way_tags</li>
# </ul>

# In[2]:


#Initializing xmlTree
xml = ET.parse("data")
root = xml.getroot()


# In[3]:


# Parsing Xml to dictionary
tags = {
    'nodes' : [],
    'ways' : []
}
for element in root:
    if element.tag == 'node':
        tag, element_type = cleaning.process_nodes(element)
        tags['nodes'].append(tag)
    if element.tag == 'way':
        tag, element_type = cleaning.process_ways(element)
        tags['ways'].append(tag)


# <h2>Abreviações</h2>
# <p>No bancod e dados, para o valor de value nas node_tags e way_tags, podemos perceber um grande uso de abreviações para nomenclatura de vias. Por exemplo:
# <ul>
#     <li>R ou R. para Rua</li>
#     <li>Ave ou Av para Avenida</li>
#     <li>Rod. para Rodovia</li>
# </ul>
# Também foram encontrados palavras digitadas fora do padrão como RUA, para Rua.</p>
# <p>Para isto utilizei o regex abaixo e iterei sobre as tags, corrigindo e padronizando os valores para as vias</p>

# In[4]:


# Updating wrong words
expected = ['Rua', 'Avenida', 'Rodovia', 'Via', 'Estrada', 'Praia', 'Praça', 'Alameda']
    
# Regex to match abreviations, and variations of expected
regex_dict = {
    'Rua' : [re.compile(r'\b(rua)\b', re.IGNORECASE), re.compile(r'\b(r(\.)?)\b', re.IGNORECASE)],
    'Avenida' : [re.compile (r'\b(avenida)\b', re.IGNORECASE), re.compile(r'\b(ave(\.)?)\b', re.IGNORECASE), re.compile(r'\b(av(\.)?)\b', re.IGNORECASE)],
    'Rodovia' : [re.compile(r'\b(rodovia)\b'), re.compile (r'\b(rod(\.)?)\b')],
    'Via' : [re.compile (r'\b(via)\b', re.IGNORECASE), re.compile(r'\b(v(\.)?)\b', re.IGNORECASE)],
    'Estrada' : [re.compile(r'\b(estrada)\b', re.IGNORECASE), re.compile(r'\b(est(\.)?)\b', re.IGNORECASE)],
    'Praia' : [re.compile(r'\b(praia)\b', re.IGNORECASE)],
    'Praça' : [re.compile(r'\b(praça)\b', re.IGNORECASE), re.compile(r'\b(pça(\.)?)\b', re.IGNORECASE)],
    'Alameda' : [re.compile(r'\b(alameda)\b', re.IGNORECASE), re.compile(r'\b(al(\.)?)\b', re.IGNORECASE)]
}

for node in tags ['nodes']:
    for tag in node['node_tags']:
        cleaning.update_misstyping_and_abreviations(tag, expected, regex_dict)
for node in tags ['ways']:
    for tag in node['way_tags']:
        cleaning.update_misstyping_and_abreviations(tag, expected, regex_dict)


# <h2>Inconsistência nos valores de 'key'</h2>
# <p>Nesta parte foi verificado que alguns dos valores de keys, estavam em português outros em inglês o que pode trazer problemas no momento de explorar o banco de dados</p>
# <p>As principais chaves com incositência eram os telefones e bairros, para isto utilizei do código abaixo que altera o valor de key</p>

# In[5]:


# Updating inconsistent tag key
for node in tags['nodes']:
    for tag in node['node_tags']:
        if tag['key'] == 'BAIRRO':
            tag['key'] = 'suburb'
        if tag['key'] == 'TELEFONES':
            tag['key'] = 'phone'
            
for way in tags['ways']:
    for tag in way['way_tags']:
        if tag['key'] == 'BAIRRO':
            tag['key'] = 'suburb'
        if tag['key'] == 'TELEFONES':
            tag['key'] = 'phone'


# <h2>Inconsistência nos valores de CEP, e CEPs inválidos</h2>
# <p>Os valores encontrados para o CEP em geral estavam corretos no formato xxxxx-xxx onde x é um número decimal,
# porém alguns valores saíam do padrão:</p>
#     <ul>
#         <li>xxxxx não contendo os útlimo três digitos para especificação do identificação individual de Localidades, Logradouros, Códigos Especiais ou Unidades dos Correios, estes valores foram mantidos como estão sem os últimos três dígitos</li>
#         <li>xxxxx xxx não contendo o hífen, estes valores foram corrigidos inserindo os hífens</li>
#         <li>E haviam tabém valores de cep que não possuíam nem 8 nem 5 dígitos, estes valores foram apagados</li>
#     <ul>

# In[6]:


# Updating inconsistent cep values
non_decimal = re.compile(r'[^\d]+')
for node in tags['nodes']:
    node['node_tags'] = cleaning.update_cep(node['node_tags'], non_decimal)
for way in tags['ways']:
    way['way_tags'] = cleaning.update_cep(way['way_tags'], non_decimal)


# <h2>Convertendo para csv</h2>

# In[7]:


"""
Takes a list of lists as parameter, and return a single list containing elements of all lists
"""
def extract_list_from_lists(root_list):
    aux = []
    for tag_list in root_list:
        for tag in tag_list:
            aux.append(tag)
    return aux
"""
Takes a dictinary as parameter and writtes as csv file
"""
def export_to_csv(keys, values, fname):

    keys = list(keys)

    with open(fname, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(values)


# In[8]:


nodes_attributes = []
nodes_tags = []

ways_attributes = []
ways_nodes = []
ways_tags = []

# Separating dictionary to lists and writting csv files
for node in tags['nodes']:
    for key, value in node.items():
        if key == 'node':
            nodes_attributes.append(value)
        if key == 'node_tags':
            nodes_tags.append(value)  

for way in tags['ways']:
    for key, value in way.items():
        if key == 'way':
            ways_attributes.append(value)
        if key == 'way_nodes':
            ways_nodes.append(value)
        if key == 'way_tags':
            ways_tags.append(value)

nodes_tags = extract_list_from_lists(nodes_tags)
ways_nodes = extract_list_from_lists(ways_nodes)
ways_tags = extract_list_from_lists(ways_tags)

export_to_csv(nodes_attributes[0].keys(), nodes_attributes, "nodes_attributes.csv")
export_to_csv(nodes_tags[0].keys(), nodes_tags, "nodes_tags.csv")
export_to_csv(ways_attributes[0].keys(), ways_attributes, "ways_attributes.csv")
export_to_csv(ways_nodes[0].keys(), ways_nodes, "ways_nodes.csv")
export_to_csv(ways_tags[0].keys(), ways_tags, "ways_tags.csv")


# <h1>Inspecionando o banco de dados com SQL</h1> 
# <h2>Analisando os CEPs</h2>
# <p>Para inspecionar os valores dos CEPs eu optei por ignorar os dígitos mais específios da localidado após o hífen, e contei os valores agrupados. A query realizada é a seguinte:</p>
# <p>SELECT SUBSTR(value, 0, 5), COUNT(*) FROM (SELECT * FROM ways_tags UNION ALL SELECT * FROM nodes_tags) WHERE key='postcode' GROUP BY SUBSTR(value, 0, 5) ORDER BY count(value) DESC LIMIT 10;</p>
# <p>Os 10 CEPs com a maior contagem são:</p>
# <ul>
#     <li>2272|409</li>
#     <li>2023|232</li>
#     <li>2222|231</li>
#     <li>2221|186</li>
#     <li>2247|127</li>
#     <li>2223|107</li>
#     <li>2225|97</li>
#     <li>2279|76</li>
#     <li>2224|65</li>
#     <li>2245|65</li>
# </ul>
# <p>Porém durante a busca pelos CEPs, também encontrei dois valores estranhos: 3595 (completo 35953-060) e 5264 (completo 52645-100), que aparecereram uma única vez cada um. Estes valores de CEP são inválidos para o Rio de Janeiro, que deve possuir o dígito inicial igual a 2. O inicial 3 pertence a Minas Gerais e o inicial 5 pertence à Pernambuco, Paraiba, Rio Grande do Norte e Alagoas.</p>
# <p>Fonte dos Estados e CEPs: https://www.correios.com.br/para-voce/precisa-de-ajuda/o-que-e-cep-e-por-que-usa-lo/estrutura-do-cep</p>
# 
# <h3>Inspecionando o CEPs invaĺidos</h3>
# <p>Meu primeiro passo foi buscar a linha completa do CEP</p>
# <p>SELECT * FROM (SELECT * FROM ways_tags UNION ALL SELECT * FROM nodes_tags) WHERE key='postcode' and (value='35953-060' or value='52645-100');</p>
# <ul>
#     <li>254405944|52645-100|addr|postcode</li>
#     <li>2887457280|35953-060|addr|postcode</li>
# </ul>
# <p>Após encontrar os IDs das tags, eu busquei as outras tags relacionadas a estes IDs e Nodes Root destas tags. Seguem os valores:</p>
# 
# <p>Para a tag de id 2887457280 obtemos:</p>
# <ul>
#     <li>2887457280|erickdeoliveiraleal|463504|2|-22.4108637|-42.9671754|2014-07-13T17:53:03Z|24125762</li>
#     <ul>
#         <li>2887457280|Maria Torta Café|regular|name</li>
#         <li>2887457280|cafe|regular|amenity</li>
#         <li>2887457280|cafe|regular|amenity</li>
#         <li>2887457280|Restaurante_especializado_em café da manhã e brunch|regular|cuisine</li>
#         <li>2887457280|Teresópolis|addr|city</li>
#         <li>2887457280|Rua Manuel Madruga|addr|street</li>
#         <li>2887457280|35953-060|addr|postcode</li>
#         <li>2887457280|10:00-20:00|regular|opening_hours</li>
#         <li>2887457280|8|addr|housenumber</li>
#      </ul>
# </ul>
# <p>Query para o Node Root:</p>
# <p>SELECT * FROM nodes WHERE id='2887457280';</p>
# <p>Query para tags relacionadas:</p>
# <p>SELECT * FROM nodes_tags WHERE id='2887457280';</p>
# 
# <p>Para a tag de id 254405944 obtemos:</p>
# <ul>
#     <li>254405944|Blubberbernd|1405221|1|2013-12-30T21:37:47Z|19723204</li>
#     <ul>
#         <li>254405944|Dogs 'n' Cats|regular|name</li>
#         <li>254405944|house|regular|building</li>
#         <li>254405944|Petrópolis|addr|city</li>
#         <li>254405944|Presidente Tancredo Neves|addr|street</li>
#         <li>254405944|52645-100|addr|postcode</li>
#         <li>254405944|2|building|levels</li>
#         <li>254405944|206|addr|housenumber</li>
#      </ul>
# </ul>
# <p>Query para o Way Root:</p>
# <p>SELECT * FROM ways WHERE id='254405944';</p>
# <p>Query para tags relacionadas:</p>
# <p>SELECT * FROM ways_tags WHERE id='254405944';</p>
# <p>Apesar dos CEPs pertencerem à outros estados, as cidades que o vemos nas tags associadas a cada Node, pertencem ao Rio de Janeiro</p>

# <h2>Inspecionando os Dados</h2>
# <p>Vou agora explorar um pouco os dados por curiosidade, alguns dados que fiquei curioso para descobrir após inspecionar um pouco o banco de dados, foi:</p>
# <ul>
#     <li>Religião mais populares</li>
#     <li>Numero de tags por cidade</li>
#     <li>Cozinhas mais populares</li>
#     <li>Datas que mais inseriram dados no banco</li>
# </ul>
# <h3>Top 10 Cidades</h3>
# <p>Aqui tivemos uma surpresa ao olhar os dados como um todo, a má formatação dos dados pode causar um erro na contagem das cidade, podemos encontrar para a cidade do Rio de Janeiro, ela escrita como rio de janeiro e Rio de Janeiro, e o SQL agrupa os dados separadamente, mas como o valor de cidades escrito da forma errada é irrelevante em relação ao todo, ignoramos este fato.</p>
# <p>Query: select value, count(value) from (select * from nodes_tags union all select * from ways_tags) where key ='city' group by value order by count(value) desc limit 10;</p>
# <ul>
#     <li>Rio de Janeiro|3820</li>
#     <li>Niterói|320</li>
#     <li>São Gonçalo|100</li>
#     <li>Itaboraí|68</li>
#     <li>Duque de Caxias|62</li>
#     <li>São João de Meriti|46</li>
#     <li>Nova Iguaçu|42</li>
#     <li>Teresópolis|37</li>
#     <li>Monsenhor Magaldi|22</li>
#     <li>Itaguaí|19</li>
# </ul>
# <h3>Top 10 Datas que mais tiveram inserção de dados</h3>
# <p>Vemos que a maior concentração de inserção de dados está em 2014</p>
# <p>Query: select Substr(timestamp, 0, 8), count(Substr(timestamp, 0, 8)) from (select timestamp from nodes union all select timestamp from ways) group by Substr(timestamp, 0, 8) order by count(Substr(timestamp, 0, 8)) desc limit 10;</p>
# <ul>
#     <li>2016-07|241330</li>
#     <li>2014-09|102450</li>
#     <li>2014-07|77771</li>
#     <li>2014-06|66111</li>
#     <li>2014-08|64946</li>
#     <li>2016-06|50504</li>
#     <li>2015-09|48062</li>
#     <li>2010-11|46641</li>
#     <li>2012-10|44096</li>
#     <li>2017-09|43198</li>
# </ul>

# <h2>Estatísticas dos Dados</h2>
# <p>Tamnho dos arquivos</p>
# <ul>
#     <li>data.osm - 381.6 MB</li>
#     <li>Project.db - 270.5 MB</li>
#     <li>nodes_attributes.csv - 149,4 MB</li>
#     <li>nodes_tags.csv - 5,9 MB</li>
#     <li>ways_attributes - 12,9 MB</li>
#     <li>ways_nodes - 52,4 MB</li>
#     <li>ways_tags - 17,9 MB</li>
# </ul>
# <h2>Numero de Nodes</h2>
# <p>Query: select count(*) from nodes;</p>
# <p>1742846</p>
# <h2>Numero de Ways</h2>
# <p>Query: select count(*) from ways;</p>
# <p>211137</p>
# <h2>Numero de usuários únicos</h2>
# <p>Query: select count(distinct(user)) from (select user from nodes union all select user from ways);</p>
# <p>1864</p>
# <h2>Top 10 contribuintes</h2>
# <p>Query: select user, count(user) from (select user from nodes union all select user from ways) group by user order by count(user) desc limit 10;</p>
# <ul>
#     <li>Alexandrecw|370372</li>
#     <li>smaprs_import|183985</li>
#     <li>ThiagoPv|178328</li>
#     <li>AlNo|151867</li>
#     <li>Import Rio|84299</li>
#     <li>Geaquinto|68614</li>
#     <li>Nighto|66245</li>
#     <li>petropouli|59842</li>
#     <li>Ricardo Mitidieri|59136</li>
#     <li>Thundercel|53608</li>
# </ul>
# 
# 

# <h1>Idéias Adicionais</h1>
# <p>O Bando de Dados do OpenStreetMap tem vários dados inconsistentes, como alguns apontados anteriormente, CEPs escritos de formas diferentes, uso de mais de uma lingua para os valores de keys, dentre outras falhas no banco.</p>
# <h2>Uso de Regex</h2>
# <p>Uma forma que eu pensei para ajudar na inserção de dados consistentes, é inserir regex para inserção de valores da forma esperada, por exemplo CEPs e Telefones, podemos fazer um regex e validar os valores antes de serem inseridos. Até mesmo com nomes de cidades para evitar erros como Rio de Janeiro e rio de janeiro, se o valor da tag a ser inserida é um nome, validamos o valor dela com um regex para letras maiúsculas no início da palavra. Isto irá ajudar na padronização dos dados.</p>
# <p>Porém a inserção de regex na validação dos dados torna mais burocrático o processo de adicionar valores ao OpenStreetMap, e sabemos que a comunidade contribui para o projeto sem esperar um retorno, ou seja são voluntários. E caso comecemos a inserir muitas regras no processo eles podem ficar desmotivados, por que terão de reescrever seus scripts além de aprender os novos padrões dos dados.</p>
# <p>Esta medida pode ter impactos positivos ou negativos e deve-se talvez conversar previamente com a comunidade antes de atualizar o sistema de inserção</p>
# <h2>Uso de Dados Públicos</h2>
# <p>Durantes a análise dos dados, em específico durante a verificação dos CEPs inválidos nos conjuntos, eu utilizei de outros dados públicos para verificar a validade dos dados. Esta pode ser outra forma de verificação dos dados inseridos nos bancos de dados, a verificação de CEPs por exemplo pode ser realizada comparando a latitude e longitude e ver a qual estado o endereço pertence, e então verificar se o CEP realmente pode pertencer à aquela localidade. Isto pode ser aplicado além do CEPs mas também aos telefones, bairros e cidades. Verificando se faz sentido aquela cidade pertencer à aquele estado, ou o bairro pertencer à aquela cidade</p>
# <p>A wikipedia por exemplo possui dados dos bairros do Rio de Janeiro, que podem ser usados como um comparativo com os dados dos nossos dados</p>
# <p>Apesar desta medida também ser uma burocracia a mais para inserção de dados, que pode desmotivar os usuários. Ela é essencial, pois impede que os valores inseridos estejam errado, algo que imagino que a comunidade também queira, então provavelmente os usuários aceitariam que houvesse esta verificação a mais dos dados</p>
# <p>Mas uma das principais dificuldades para esta implementação é acessar os dados públicos para então realizar a verificação dos dados do OpenStreetMap, muitos dos dados do governo não são de fácil acesso, e estão espalhados por vários sites, pdfs em diferentes formatos o que torna difícil a implementação deste sistema de verficação</p>

# <h1>Conclusão</h1>
# <p>Após uma limpeza parcial dos dados, de tal forma que podemos analisar os dados que desejamos. Podemos ver que nos dados do OpenStreetMap temos várias inconsistências, muitas delas devido a inserção de dados por seres humanos, que podem ter um padrão de escrita de dados diferte, por exemplo os telefones, abreviações ou escrita por extenso, e isso nos trás vários problemas como vamos analisar dados de forma programática, e exige que usemos dos padrões dos dados para podermos analisá-los. E em alguns momentos para a inserção de dados, podemos automatizar algumas tarefas com GPS, ou verificar a inserção de dados previamente, como citado anteriormente. Contribuindo para que possuamos um banco padronizado que podemos gastar mais tempo na análise do que limpando os dados</p>
# <p>Apesar de tudo, o projeto do OpenStreetMap, é muito interessante por ser aberto e construido apartir de voluntários ao redor do mundo que inserem dados e contribuem para termos mais informações sobre o mundo</p>

# <h1>Links Externos</h1>
# <p>Para a limpeza e análise eu usei os seguintes links</p>
# <ul>
#     <li>https://www.correios.com.br/para-voce/precisa-de-ajuda/o-que-e-cep-e-por-que-usa-lo/estrutura-do-cep</li>
#      <li>https://pt.wikipedia.org/wiki/Lista_de_bairros_do_Rio_de_Janeiro_(cidade)</li>
# </ul>
