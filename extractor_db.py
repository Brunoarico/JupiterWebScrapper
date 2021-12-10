import sys
from bs4 import BeautifulSoup
import requests
import sqlite3
from unidecode import unidecode
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dbmanager import DBManager

class Extractor:
    def __init__(self):
        #URL's base e complementos
        self.basePage = "https://uspdigital.usp.br/jupiterweb/"
        self.firstCompl = "jupColegiadoLista?tipo=T"
        self.secondCompl = "jupDisciplinaLista?"
        self.thirdCompl = "jupTurma?sgldis="
        self.fourthCompl = "jupDisciplina?sgldis="
        self.fifthCompl = "listarCursosRequisitos?coddis="
        self.dictUnidades = dict()
        self.s = requests.Session()
        self.retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        self.s.mount('http://', HTTPAdapter(max_retries=self.retries))
        self.bd = DBManager("matrusp.db")
        try:
            self.bd.create()
        except:
            print("Banco de dados ja criado")
            #self.bd.dump()

    #Metodo que realiza a analise da pagina de Unidades
    #extrai da tabela principal o nome e o codigo do unidade
    #para cada unidade cria uma entrada no dicionario de Objetos Unidade
    def scrapUnidades(self):
        page = self.s.get(self.basePage+self.firstCompl) #request para a pagina que contem a referencia para as unidades
        if(page.status_code == 200):
            print("[+] Pagina de unidades acessada com sucesso")
            soup = BeautifulSoup(page.content, 'html.parser')
            table = soup.findAll("table") #encontra as tabelas que contem os dados
            table = [table[2], table[4]] #as unicas duas tabelas com dados importantes
            #Extracao dos dados importantes das tabelas
            for i in table:
                span = i.findAll('span')
                tr = i.findAll('tr')
                for j in tr:
                    a = j.find("a")
                    if(a):
                        span = j.findAll('span')
                        codigo = span[0].text.strip()
                        nome = span[1].text.strip()
                        curseLink = a['href']
                        self.bd.insertUnidade(nome, codigo)
                        self.dictUnidades[codigo] = curseLink #adiciona ao dicionario de unidades
            return self.dictUnidades

        else:
            print("[-] Pagina de unidades com problemas, verificar se esta disponivel: " + base)
            return


    def getRequisitos(self, codeDiscip):
        page = self.s.get(self.basePage+self.fifthCompl+codeDiscip)
        if(page.status_code == 200):
            soup = BeautifulSoup(page.content, 'html.parser')
            form = soup.find("form")
            if(form):
                tables = form.findAll("table")
                if(len(tables) > 2):
                    tr = tables[3].findAll("tr")
                    for i in tr:
                        txt = " ".join(i.text.split())
                        if("Curso:" in txt):
                            textInt = txt.split(":")[1].strip()
                            curso = textInt.split(" - ")[0]
                            curso = curso.split(" ",1)
                            cursoID = curso[0]
                            cursoNome = curso[1]
                            periodoIdeal = textInt[2].strip()
                        else:
                            td = i.findAll("td")
                            if(len(td) > 1):
                                req = " ".join(td[0].text.split())
                                codeReq = req.split(" - ")[0]
                                tipoReq =  " ".join(td[1].text.split())
                                self.bd.insereDisciplinaRequisito(codeDiscip, codeReq, tipoReq, cursoNome, cursoID, periodoIdeal)

    #Funcao que coleta mais informacoes sobre cada uma das disciplinas oferecidas pelas unidades
    #@param:
    #   codeDiscip: Disciplina a qual a pagina sera alvo da extração
    def getDisciplinaInfo(self, codeDiscip, name, ativ, desativ):
        info = dict()
        info["codigo"] = codeDiscip
        info["nome"] = name
        info["ativacao"] = ativ
        info["desativacao"] = desativ
        page = self.s.get(self.basePage+self.fourthCompl+codeDiscip)

        if(page.status_code == 200):
            soup = BeautifulSoup(page.content, 'html.parser')
            form = soup.find("form")
            print("[+] Extraindo: "+self.basePage+self.fourthCompl+codeDiscip)
            self.getRequisitos(codeDiscip)

            if(form):
                tables = form.findAll("table")
                tr = tables[1].findAll("tr")

                #trata tabela de creditos
                for i in tr:
                    text = i.text.split(":")
                    info[unidecode(text[0].strip().replace(" ", "_").lower())] = text[1].strip()

                #trata a tabela de objetivos
                tr = tables[2].findAll("tr")
                info[unidecode(tr[0].text.strip().lower())] = tr[1].text.strip()

                #Caso a disciplina tenha docentes
                if(len(tables) == 10):

                    #trata a tabela de docentes
                    tr = tables[3].findAll("tr")
                    type = unidecode(tr[0].text.strip().lower().split("(")[0])
                    names = tr[1].text.replace("\r", "").split("\n")
                    for i in names:
                        if(i.strip()):
                            idDocente = self.bd.insertDocente(i.strip())
                            self.bd.insertDocenteDiciplina(idDocente, codeDiscip)

                    #trata a tabela programa resumido e programa
                    tr = tables[5].findAll("tr")
                    info[unidecode(tr[0].text.strip().replace(" ", "_").lower())] = tr[1].text.strip()
                    info[unidecode(tr[3].text.strip().lower())] = tr[4].text.strip()

                    #trata Metodo criterio e recuperacao
                    tr = tables[6].findAll("tr")
                    info[unidecode(tr[0].text.strip().lower())] = tr[1].text.strip()
                    info[unidecode(tr[3].text.strip().lower())] = tr[4].text.strip()
                    info[unidecode(tr[6].text.strip().replace(" ", "_").lower())] = tr[7].text.strip()

                    #trata bibliografia
                    tr = tables[7].findAll("tr")
                    info[unidecode(tr[0].text.strip().lower())] = tr[1].text.strip()

                #Caso a disciplina nao tenha docentes
                else:

                    #trata a tabela programa resumido e programa
                    tr = tables[3].findAll("tr")
                    info[unidecode(tr[0].text.strip().replace(" ", "_").lower())] = tr[1].text.strip()
                    info[unidecode(tr[3].text.strip().lower())] = tr[4].text.strip()

                    #trata Metodo criterio e recuperacao
                    tr = tables[4].findAll("tr")
                    info[unidecode(tr[0].text.strip().lower())] = tr[1].text.strip()
                    info[unidecode(tr[3].text.strip().lower())] = tr[4].text.strip()
                    info[unidecode(tr[6].text.strip().replace(" ", "_").lower())] = tr[7].text.strip()

                    #trata bibliografia
                    tr = tables[5].findAll("tr")
                    info[unidecode(tr[0].text.strip().lower())] = tr[1].text.strip()
                self.bd.insertDisciplina(info)
                #print(info)

    #Metodo que extrai informacoes basicas sobre as disciplinas
    def scrapDisciplinas(self):
        for keys, linkPageUnidade in self.dictUnidades.items():
            refDiscip = linkPageUnidade.split("&")[0].split("?")[1] + "&letra=A-Z&tipo=D"
            page = self.s.get(self.basePage+self.secondCompl+refDiscip)

            if(page.status_code == 200):
                soup = BeautifulSoup(page.content, 'html.parser')
                print("[+] Pagina de " + linkPageUnidade + " acessada com sucesso")
                table = soup.findAll("table")
                for k in table:
                    tr = k.findAll("tr")
                    for j in tr:
                        a = j.find("a")
                        span = j.findAll("span")
                        if(a and len(span) > 1):
                            code = span[0].text.strip()
                            name = span[1].text.strip()
                            ativ = span[2].text.strip()
                            desativ = span[3].text.strip()

                            self.getDisciplinaInfo(code, name, ativ, desativ)
            else:
                print("[-] Pagina de " + linkPageUnidade + "com problemas")
        self.bd.close()

if __name__ == "__main__":
    e = Extractor()
    e.scrapUnidades()
    e.scrapDisciplinas()
