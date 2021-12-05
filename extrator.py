import json
import sys
from bs4 import BeautifulSoup
import requests
from unidecode import unidecode
sys.path.append(".")
from unidade import Unidade
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class Extractor:

    def __init__(self):
        #URL's base e complementos
        self.basePage = "https://uspdigital.usp.br/jupiterweb/"
        self.firstCompl = "jupColegiadoLista?tipo=T"
        self.secondCompl = "jupDisciplinaLista?"
        self.thirdCompl = "jupTurma?sgldis="
        self.fourthCompl = "jupDisciplina?sgldis="
        self.dictUnidades = dict()
        self.s = requests.Session()
        self.retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        self.s.mount('http://', HTTPAdapter(max_retries=self.retries))

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
                        code = span[0].text.strip()
                        name = span[1].text.strip()
                        curseLink = a['href']
                        self.dictUnidades[code] = Unidade(name, code, curseLink) #adiciona ao dicionario de unidades
            return self.dictUnidades

        else:
            print("[-] Pagina de unidades com problemas, verificar se esta disponivel: " + base)
            return



    #Funcao que coleta mais informacoes sobre cada uma das disciplinas oferecidas pelas unidades
    #@param:
    #   codeDiscip: Disciplina a qual a pagina sera alvo da extração
    def getDisciplinaInfo(self, codeDiscip, ref):
        page = self.s.get(self.basePage+self.fourthCompl+codeDiscip)

        if(page.status_code == 200):
            soup = BeautifulSoup(page.content, 'html.parser')
            form = soup.find("form")
            print("[+] Extraindo: "+ self.basePage+self.fourthCompl+codeDiscip)
            if(form):
                tables = form.findAll("table")
                #Caso a disciplina tenha docentes
                if(len(tables) == 10):
                    ##print("\n[+] Pagina de " + codeDiscip + " acessada com sucesso")
                    tr = tables[1].findAll("tr")
                    #trata tabela de creditos
                    for i in tr:
                        text = i.text.split(":")
                        ref.setDisciplinaDetails(codeDiscip, unidecode(text[0].strip().replace(" ", "_").lower()), text[1].strip())
                    #trata a tabela de objetivos
                    tr = tables[2].findAll("tr")
                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[0].text.strip().lower()), tr[1].text.strip())
                    #trata a tabela de docentes
                    tr = tables[3].findAll("tr")
                    type = unidecode(tr[0].text.strip().lower().split("(")[0])
                    docentes = []
                    names = tr[1].text.replace("\r", "").split("\n")
                    for i in names:
                        if(i.strip()):
                            docentes.append(ref.setDocentes(i.strip()))
                    ref.setDisciplinaDetails(codeDiscip, type, docentes)
                    #trata a tabela programa resumido e programa

                    tr = tables[5].findAll("tr")
                    #print(tr)
                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[0].text.strip().replace(" ", "_").lower()), tr[1].text.strip())
                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[3].text.strip().lower()), tr[4].text.strip())
                    #trata Metodo criterio e recuperacao
                    tr = tables[6].findAll("tr")
                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[0].text.strip().lower()), tr[1].text.strip())
                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[3].text.strip().lower()), tr[4].text.strip())
                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[6].text.strip().replace(" ", "_").lower()), tr[7].text.strip())
                    #trata bibliografia
                    tr = tables[7].findAll("tr")
                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[0].text.strip().lower()), tr[1].text.strip())

                #Caso a disciplina nao tenha docentes
                else:
                    print("[!] Disciplina sem docente")
                    tr = tables[1].findAll("tr")
                    #trata tabela de creditos
                    for i in tr:
                        text = i.text.split(":")
                        ref.setDisciplinaDetails(codeDiscip, unidecode(text[0].strip().replace(" ", "_").lower()), text[1].strip())
                    #trata a tabela de objetivos
                    tr = tables[2].findAll("tr")
                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[0].text.strip().lower()), tr[1].text.strip())
                    #trata a tabela programa resumido e programa

                    tr = tables[3].findAll("tr")

                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[0].text.strip().replace(" ", "_").lower()), tr[1].text.strip())
                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[3].text.strip().lower()), tr[4].text.strip())
                    #trata Metodo criterio e recuperacao
                    tr = tables[4].findAll("tr")
                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[0].text.strip().lower()), tr[1].text.strip())
                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[3].text.strip().lower()), tr[4].text.strip())
                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[6].text.strip().replace(" ", "_").lower()), tr[7].text.strip())
                    #trata bibliografia
                    tr = tables[5].findAll("tr")
                    ref.setDisciplinaDetails(codeDiscip, unidecode(tr[0].text.strip().lower()), tr[1].text.strip())
                    ref.discip[codeDiscip].print()


    #Metodo que extrai informacoes basicas sobre as disciplinas
    def scrapDisciplinas(self):
        for keys, values in self.dictUnidades.items():
            linkPageUnidade = values.getLinkUnidade()
            refDiscip = linkPageUnidade.split("&")[0].split("?")[1] + "&letra=A-Z&tipo=D"
            page = self.s.get(self.basePage+self.secondCompl+refDiscip)

            if(page.status_code == 200):
                soup = BeautifulSoup(page.content, 'html.parser')
                print("[+] Pagina de " + values.getNome() + " acessada com sucesso")
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
                            link = a['href']
                            values.setDisciplina(code, name, link, ativ, desativ)
                            self.getDisciplinaInfo(code, values)
                            self.toJson()
                values.print()
            else:
                print("[-] Pagina de " + values.getNome() + "com problemas")

    #Converte os dados das unidades e respectivas disciplinas exploradas recursivamente
    #cria um arquivo json com nome UnidadesDisciplinas.json no diretorio onde foi executado
    def toJson(self):
        tmp = dict()
        for key, value in self.dictUnidades.items():
            tmp[key] = value.toJson()

        with open('UnidadesDisciplinas.json', 'w') as f:
            json.dump(tmp, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    e = Extractor()
    e.scrapUnidades()
    e.scrapDisciplinas()
    e.toJson()
