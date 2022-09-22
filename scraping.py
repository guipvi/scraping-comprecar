#!/usr/bin/env python
# coding: utf-8

# In[1]:


# # Coleta de dados do site 'Compre car'


# ## Instalando e importanto bibliotecas

print('Importing librarys')
import datetime
from datetime import date
import logging
import pandas as pd
import bs4
import urllib.request as urllib_request
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from numpy.ma.core import array
print('ok')


# In[2]:


# ## Definindo funções e variáveis


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
# headers é uma variável que podemos obter pelo DevTools do Google 
# Chrome para emular que estamos acessando as páginas por um navegador


# In[ ]:


def trata_html(input):
    return " ".join(input.split()).replace('> <', '><')
# trata_html é uma função para padronizar a formatação da html,
# eliminando espaços desnecessários


def varrer_paginas(url_primeira_pagina):
    print('Collecting soups objects from the pages of the site')
    soups = []
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    pg = url_primeira_pagina
    req = Request(pg, headers = headers)
    response = urlopen(req)
    html = response.read()
    html = html.decode('utf-8')
    html = trata_html(html)
    soup = BeautifulSoup(html, 'html.parser')
    soups.append(soup)
    print('First page collected')
    # estamos defindo na função como fazer para obter um objeto soup
    # através do input de url e adicionando esses objetos na lista
    # soups. Até aqui, coletamos a primeira página do site.
    while True:
      pgn = soup.find('a', {'aria-label':'Próximo'}).get('href')
      pgn = pgn.split('page=')
      pg = pgn[0]
      n = int(pgn[1])
      # dentro do último soup obtido, estamos procurando pela referência
      # no html da setinha que nos levaria até a próxima página e adquirindo
      # 'n', o número da página
      if n > 0:
      # quando chegamos até a última página, a setinha está desabilitada, mas
      # ainda referencia uma página: a '0'. Este é o único momento em que 'n'
      # será igual a '0' e também marca o momento quando o algorítmo deverá parar.
        const = url_primeira_pagina.split(pg)
        const = const[1]
        const = const.split('&premium=0')
        const = [str(const[0] +'&page='), str('&premium=0' + const[1])]
        const = const[0]+str(n)+const[1]
        pgn = pgn[0]+const
        # até aqui, estamos tratando a url, uma vez que ela é referenciada de uma forma
        # diferente na setinha de 'próxima página' e, de fato, na próxima página em si.
        # Sendo assim, utilizamos a string da primeira página para definir 'const' e
        # corrigimos as contradições
        print('Storing the html from the ' + pgn + ' url in soups')
        req = Request(pgn, headers = headers)
        response = urlopen(req)
        html = response.read()
        html = html.decode('utf-8')
        html = trata_html(html)
        soup = BeautifulSoup(html, 'html.parser')
        soups.append(soup)
        # aplicamos o mesmo método que usamos na página '1' na página 'n'.
      else:
        print(str(len(soups))+' soups objects collected')
        logging.info(str(len(soups))+' soups objects collected')
        return soups
        break
        #definimos o que acontece quando 'n' não é maior que '0'


# ## Coletando as soups das páginas do site e armazenando em uma variável 


pg1 = 'https://www.comprecar.com.br/buscar?anode=1952&anoate=2023&premium=0&tipo%5B%5D=1'  
soups = varrer_paginas(pg1)
#aplicamos a função que definimos anteriormente


# ## Procurando por informações na lista de soups


# definindo listas e dicionários onde serão armazenadas as informações
lista_listas_links_descricoes = []
soups_paginas_carros = []
lista_listas_descricoes_complementares = []
lista_listas_link_valor = []
lista_listas_acessorios = []
lista_links_anuncios = []


# definindo páginas do site para serem trabalhadas separadamente
for i in range(len(soups)):
    
    # definindo listas e dicionários que serão armazenados dentro do loop for
    dict_link_valor = {}
    lista_link_descricao_do_carro = []
    print("Accessing page " + str(i+1) + " from the total " + str(len(soups)) + " pages")
    
    # procurando pelos anúncios dentro da página do site
    soups_anuncios = soups[i].find('div', {'class':'row vehicle-list'}).findAll('div', {'class': 'item-vehicle-list'}) 

    # defininco anúncios para serem trabalhados separadamente
    for soup_anuncio in soups_anuncios:
            
        # tentando obter o link do anúncio e acessá-lo
        try:
            link = str(soup_anuncio).split("window.open('")[1].split("'); sendGA")[0]
            if link not in lista_links_anuncios:
                lista_links_anuncios.append(link)
                req = Request(link, headers = headers)
                response = urlopen(req)
                html = response.read()
                html = html.decode('utf-8')
                html = trata_html(html)
                soup_pagina_carro = BeautifulSoup(html, 'html.parser')
                soups_paginas_carros.append(soup_pagina_carro)
                print(" collecting data from the announcement with the link " + link)
            
                # tratando html dos anuncios
                soup_anuncio = trata_html(str(soup_anuncio))
                soup_anuncio = BeautifulSoup(soup_anuncio, 'html.parser')
            
                # obtendo valores dos carros, associando com os links das páginas e armazenando os dados
                lista_link_valor = []
                link = str(soup_anuncio).split("window.open('")[1].split("'); sendGA")[0]
                lista_link_valor.append(link)
                lista_link_valor.append(soup_anuncio.find('div', {'class': 'col-4 vehicle-value'}).getText())
                lista_listas_link_valor.append(lista_link_valor)
        
                # obtendo descrições do carros, associando com os links das páginas e armazenando os dados
                descricao_do_carro_no_site = soup_anuncio.findAll('li')
                lista_link_descricao_do_carro = []
                for info in descricao_do_carro_no_site:
                    lista_link_descricao_do_carro.append(info.get_text())
                lista_link_descricao_do_carro = lista_link_descricao_do_carro
                lista_link_descricao_do_carro.append(link)
                lista_listas_links_descricoes.append(lista_link_descricao_do_carro)

            
        except Exception:
            print(' failed to accesses ' + link)
            logging.info(' failed to accesses ' + link)
            # aqui identificamos quais anúncios não conseguimos acessar
            pass
            

# ### Armazenando e tratando os dados


# armazenando as descriões gerais que estão contidas nos anúncios
links_descricoes = pd.DataFrame(lista_listas_links_descricoes)
print('storaging and treating links and car descriptions')
# Removendo duplicatas
links_descricoes.drop_duplicates(inplace=True)


# In[2]:


# Definindo index
links_descricoes.set_index([7], inplace=True)


# In[4]:


try:
    # Reparando inconsistências nas colunas
    filtro_8 = links_descricoes[8].notna()
    links_descricoes_filtro_8 = links_descricoes[filtro_8]
    for i in links_descricoes_filtro_8.index:
        links_descricoes.drop(str(i))
    links_descricoes_filtro_8.set_index([8], inplace=True)
    links_descricoes_filtro_8.index.rename('7', inplace=True)
    links_descricoes_filtro_8[6] = links_descricoes_filtro_8['3']
    try:
        links_descricoes.drop(columns = '8', inplace = True)
    except Exception:
        pass
    links_descricoes.append(links_descricoes_filtro_8)
except KeyError:
    pass
links_descricoes.drop(columns = 6, inplace = True)
links_descricoes.drop_duplicates(inplace=True)
# Renomeando colunas e index
links_descricoes.index.rename('link', inplace=True)


# In[5]:


links_descricoes.rename(columns={0:'carro', 1:'vendedor', 2:'cidade', 3:'combustivel', 4:'ano', 5:'kms'},inplace=True)


# In[6]:


# Tratando kms
kms_tratados = []
for km in links_descricoes['kms']:
    if km == '0 KM':
        km = km.split(' KM')[0]
        kms_tratados.append(km)
    else:
        km = km.split('KM ')[1]
        try:
            km = km.split('.')
            km = km[0]+km[1]+km[2]
        except IndexError:
            try:
                km = km[0]+km[1]
            except IndexError:
                km = km[0]
                pass
            try:
                kms_tratados.append(int(km))
            except Exception:
                kms_tratados.append(None)
links_descricoes['kms'] = kms_tratados
links_descricoes


# In[7]:


# armazenando valores
links_valores = pd.DataFrame(lista_listas_link_valor)
print('storaging and treating links and cars values')
# Removendo duplicatas
links_valores.drop_duplicates(inplace=True)
# Renomeando colunas e index
links_valores.rename(columns = {1:'valor', 0:'link'}, inplace = True)
links_valores.set_index('link', inplace=True)
valores_tratados = []
# Tratando valores
for valorx in links_valores['valor']:
    valor_quebrado = valorx.split('R$ ')[1].split(',')[0].split('.')
    try:
        valor = valor_quebrado[0] + valor_quebrado[1] + valor_quebrado[2]
    except IndexError:
        try:
            valor = valor_quebrado[0] + valor_quebrado[1]
        except IndexError:
            valor = valor_quebrado
    valores_tratados.append(float(valor))
links_valores['valor'] = valores_tratados
links_valores


# In[8]:


# ## Procurando por informações na lista de soups das páginas de cada carro


# definindo listas onde serão armazenadas as informações
lista_listas_acessorios = []
lista_listas_descricoes_complementares = []

print('getting more information inside the car pages')
# definindo páginas dos carros para serem trabalhadas separadamente
for i in range(len(soups_paginas_carros)):
    print('accessing car ' + str(i+1) + ' of ' + str(len(soups_paginas_carros)))
    # definindo listas que serão armazenadas dentro do loop for
    lista_acessorios = []
    lista_descricao_complementar = []
    
    # tentando obter o link da página
    try:
        link_anuncio = str(soups_paginas_carros[i]).split('property="og:title"/><meta content="')[1]
        link_anuncio = str(link_anuncio).split('" property="og:url"/><meta content="')[0]
        print(' getting data from the html collected in the url ' + link_anuncio)
    except IndexError:
        print(' not possible to retrieve the url from the soups_paginas_carros number '+str(i))
        logging.info(' not possible to retrieve the url from the soups '+str(soups_paginas_carros[i]))
        # identificando pelo index falhas em obter os links
        pass

    # tentando obter descrições complementares dos veículos nas suas respectivas páginas
    try:
        descricao_complementar = [soups_paginas_carros[i].findAll('p', {'class':None})[1].getText(),
        soups_paginas_carros[i].findAll('p', {'class':None})[2].getText(),
        soups_paginas_carros[i].findAll('p', {'class':None})[5].getText(),
        soups_paginas_carros[i].findAll('p', {'class':None})[6].getText(),
        soups_paginas_carros[i].findAll('p', {'class':None})[7].getText()]
    except IndexError:
        try:
            descricao_complementar = [soups_paginas_carros[i].findAll('p', {'class':None})[1].getText(),
            soups_paginas_carros[i].findAll('p', {'class':None})[2].getText(),
            soups_paginas_carros[i].findAll('p', {'class':None})[5].getText(),
            soups_paginas_carros[i].findAll('p', {'class':None})[6].getText()]
        except IndexError:
            try:
                descricao_complementar = [soups_paginas_carros[i].findAll('p', {'class':None})[1].getText(),
                soups_paginas_carros[i].findAll('p', {'class':None})[2].getText(),
                soups_paginas_carros[i].findAll('p', {'class':None})[5].getText()]
            except IndexError:
                try:
                    descricao_complementar = [soups_paginas_carros[i].findAll('p', {'class':None})[1].getText(),
                    soups_paginas_carros[i].findAll('p', {'class':None})[2].getText()]
                except IndexError:
                    print(' not possible to get complementar descriptions in the html from the url ' + link_anuncio)
                    logging.info(' not possible to get complementar descriptions in the html from the url ' + link_anuncio)
                    # identificando pelo link falhas em obter descrições complementares dos veículos
                    pass

    try:
        str_pagina_carro = str(soups_paginas_carros[i])
        acessorios = str_pagina_carro.split("<h5>ACESSÓRIOS</h5><div class=\"row\"><div class=\"col-4\"><p>")[1]
        acessorios = str(acessorios).split("</p></div></div></div><div class=\"vehicle-description")[0]
        acessorios = acessorios.split("</p></div><div class=\"col-4\"><p>")
        lista_acessorios.append(acessorios)
    except IndexError:
        print(' not possible to get accessories of the cars in the html from the url ' + str(i))
        logging.info(' not possible to get accessories of the cars in the html from the url ' + str(i))
        pass
    
    # armazenando informações dentro do loop for
    lista_descricao_complementar.append(link_anuncio)
    lista_descricao_complementar.append(descricao_complementar)
    lista_acessorios.append(link_anuncio)
    
    # compilando e armazenando dados obtidos
    lista_listas_descricoes_complementares.append(lista_descricao_complementar)
    lista_listas_acessorios.append(lista_acessorios)


# In[9]:


# ### Armazenando os dados complementares


# armazenando as descriões complementares que estão contidas nas páginas dos carros
print('storaging and treating complementar descriptions')
links_desccomp = pd.DataFrame(lista_listas_descricoes_complementares)
# Definindo o index
links_desccomp.set_index([0], inplace=True)
# Descompactando str em lista de itens
itens_lista=[]
for item in links_desccomp[1]:
    itens_lista.append(item)    
# Tratando links_desccomp
tratamento = pd.DataFrame(itens_lista[:], columns = ['ano_fabricacao', 'ano_modelo', 'cor', 'marca', 'portas'])
links_desccomp['ano_fabricacao'] = list(tratamento['ano_fabricacao'])
links_desccomp['ano_modelo'] = list(tratamento['ano_modelo'])
links_desccomp['cor'] = list(tratamento['cor'])
links_desccomp['marca'] = list(tratamento['marca'])
links_desccomp['portas'] = list(tratamento['portas'])
links_desccomp.drop([1], axis = 1, inplace = True)
links_desccomp.index.rename('link', inplace = True)
# removendo inconsistências
for i in range(len(links_desccomp)):
    try:
        int(links_desccomp['ano_fabricacao'][i])
        int(links_desccomp['ano_modelo'][i])
    except Exception:
        links_desccomp.drop(links_desccomp.iloc[i], axis=1, inplace=True)
        pass
# Removendo duplicatas
links_desccomp = links_desccomp[~links_desccomp.index.duplicated(keep='first')]
links_desccomp


# In[10]:


# armazenando os acessórios dos carros
print('storaging and treating accessories')
acessorios = pd.DataFrame(lista_listas_acessorios)
# Definindo a célula acessório de carros sem acessórios como null
acessorios_na = acessorios[acessorios[1].isnull()]
acessorios_na[1] = acessorios_na[0]
acessorios_na[0] = None
acessorios.dropna(inplace=True)
acessorios.append(acessorios_na)
# Definindo index
acessorios.set_index(1, inplace=True)
# Renomeando o index e colunas
acessorios.index.rename('link', inplace=True)
# Removendo duplicatas
acessorios = acessorios[~acessorios.index.duplicated(keep='first')]
acessorios.rename(columns = {0: 'acessorios'}, inplace=True)
acessorios_lista = []
for lista_acessorios in acessorios['acessorios']:
    for acessorio in lista_acessorios:
        if acessorio not in acessorios_lista:
            acessorios_lista.append(acessorio)
index_list=[]
dict_acessorios = {}
for index in list(acessorios.index):
    index_list.append(index)
    for lista_acessorios in acessorios.loc[index]:
        itens_carro = []
        for item in acessorios_lista:
            #print(item)
            if item in lista_acessorios:
                itens_carro.append(1)
            else:
                itens_carro.append(0)
        dict_acessorios.update({index:itens_carro})
columns_dict = {}
for i in range(len(acessorios_lista)):
    columns_dict.update({i:acessorios_lista[i]})
acessorios = pd.DataFrame(dict_acessorios).T.rename(columns=columns_dict)
acessorios.index.rename('link', inplace=True)
acessorios


# In[11]:


# Adquirindo str do dia de hoje
print('storaging the date')
data_atual = date.today()
data_em_texto = data_atual.strftime('%d-%m-%Y')


# Inner join dos DataFrames
print('merging DataFrames and storaging')
dados_carros = links_valores.merge(links_descricoes, on='link').merge(links_desccomp, on='link').merge(acessorios, on='link')
# removendo duplicatas
dados_carros.drop_duplicates(inplace=True)
# # removendo colunas duplicadas
dados_carros.drop(['ano'], axis = 1, inplace = True)
# # coluna data
datas = []
for i in range(len(dados_carros)):
    datas.append(data_atual)
dados_carros['checado em:'] = datas

# # salvando os dados
print('saving DataFrame dados_carros '+data_em_texto+'.csv in ./data')
dados_carros.to_csv('data/dados_carros '+data_em_texto+'.csv', sep = ';', index = False)
print('done')

