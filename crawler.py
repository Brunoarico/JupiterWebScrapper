from bs4 import BeautifulSoup
import requests

basePage = "https://uspdigital.usp.br/jupiterweb/"
firstCompl = "jupColegiadoLista?tipo=T"
secondCompl = "jupDisciplinaLista?"

#retorna um set de links
def GetCursos():
    page = requests.get(basePage+firstCompl)
    if(page.status_code == 200):
        print("[+] Pagina de cursos acessada com sucesso")
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.findAll("table")
        table = [table[2], table[4]] #as unicas duas tabelas com dados importantes
        links = set()
        for i in table:
            span = i.findAll('span')
            tr = i.findAll('tr')
            for j in tr:
                a = j.find("a")
                if(a):
                    span = j.findAll('span')
                    l = (span[0].text.strip(), span[1].text.strip(),a['href'])
                    links.add(l)
        return links
    else:
        print("[-] Pagina de cursos com problemas, verificar se esta disponivel: " + base)
        return set()

def getDisciplinas(cursos):
    dic = dict()
    for i in cursos:
        print(i[1])
        refCurso = i[2].split("&")[0].split("?")[1] + "&tipo=T"
        page = requests.get(basePage+secondCompl+refCurso)
        print(basePage+secondCompl+refCurso)
        if(page.status_code == 200):
            soup = BeautifulSoup(page.content, 'html.parser')
            print("[+] Pagina com sublink " + refCurso + "acessada com sucesso")
            table = soup.findAll("table")
            links = set()
            for k in table:
                span = k.findAll("span")
                tr = k.findAll("tr")
                for j in tr:
                    a = j.find("a")
                    span = j.findAll("span")
                    if(a and len(span) > 1):
                        l = (i[1],span[0].text.strip(), span[1].text.strip(),a['href'])
                        links.add(l)
                        dic[i[0]] = links

        else:
            print("[+] Pagina com sublink " + refCurso + "com problemas")

    return links

linksCursos = GetCursos()
linkDiscip = getDisciplinas(linksCursos)
