import json
import hashlib

#Classe que implemente um objeto que representa disciplinas
class Disciplina:
    def __init__(self, name, code, linkDisciplina, ativ, desativ):
        self.datum = dict()
        self.datum["nome"] = name
        self.datum["codigo"] = code
        self.datum["ativacao"] = ativ
        self.datum["desativacao"] = desativ
        self.linkDisciplina = linkDisciplina

    #Retorna o nome de uma disciplina
    def getNome(self):
        return self.datum["nome"]

    #Retorna o codigo de uma disciplina
    def getCode(self):
        return self.datum["codigo"]

    #Retorna a data de ativacao de uma disciplina
    def getAtivacao(self):
        return self.datum["ativacao"]

    #Retorna a data de desativacao de uma disciplina
    def getDesativacao(self):
        return self.datum["desativacao"]

    #Retorna o link para uma disciplina
    def getLinkDisciplina(self):
        return self.linkDisciplina

    #Representa na tela uma disciplina
    def print(self):
        for key, value in self.datum.items():
            print(key, ":", value)

    #Retorna como dicionario
    def toDict(self):
        return self.datum


class Unidade():
    def __init__(self, name, code, linkUnidade):
        self.name = name
        self.code = code
        self.linkUnidade = linkUnidade
        self.discip = dict()
        self.docentes = dict()

    #Retorna o nome de uma unidade
    def getNome(self):
        return self.name

    #Retorna o codigo de uma unidade
    def getCode(self):
        return self.code

    #Retorna o link para uma unidade
    def getLinkUnidade(self):
        return self.linkUnidade

    #Adiciona a lista da unidade uma disciplina
    #@param:
    #   code: codigo da disciplina
    #   name: nome da disciplina
    #   linkDisciplina: o link de uma disciplina
    #   ativ: a data de ativacao de uma disciplina
    #   desativ: a data de desativacao de uma disciplina
    def setDisciplina(self, code, name, linkDisciplina, ativ, desativ):
        self.discip[code] = Disciplina(name, code, linkDisciplina, ativ, desativ)

    def setDocentes(self, name):
        hash_object = hashlib.md5(name.encode()).hexdigest()
        self.docentes[hash_object] = name
        return hash_object

    #Adiciona parametros extras a uma determinada disciplina
    #   code: codigo da disciplina
    #   type: chave do parametro
    #   value: valor do parametro
    def setDisciplinaDetails(self, code, type, value):
        self.discip[code].datum[type] = value

    #Representa na tela um unidade
    def print(self):
        print("Nome: %s, Codigo: %s" % (self.name, self.code))
        print("Disciplinas:", len(self.discip.keys()))
        for key, value in self.discip.items():
            value.print("\t")
            print("------")

    #Converte para Json os dados da unidade e suas respctivas disciplinas
    def toJson(self):
        tmp = dict()
        for key, value in self.discip.items():
            tmp[key] = value.toDict()
        return {"nome": self.getNome(), "code": self.getCode(), "disciplinas": tmp, "docentes": self.docentes}
