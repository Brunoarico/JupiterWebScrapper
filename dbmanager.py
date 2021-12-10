import sqlite3
import hashlib

class DBManager():
    def __init__(self, name):
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()

    def create(self):
        self.cursor.execute("CREATE TABLE unidade (nomeUnidade TEXT, codigoUnidade INT PRIMARY KEY)")
        self.cursor.execute("CREATE TABLE UnidLessionaDisc (codigoUnidade INT, codigoDisciplina INT, id INTEGER PRIMARY KEY AUTOINCREMENT)")
        self.cursor.execute("CREATE TABLE disciplina (nomeDisciplina TEXT, codigoDisciplina INT PRIMARY KEY, ativacao DATE, desativacao DATE, CredAula INT, CredTrabalho INT, tipo TEXT, objetivos TEXT, programa TEXT, programaResumido TEXT, metodo TEXT, criterio TEXT, normaRecuperacao TEXT, bibliografia TEXT)")
        self.cursor.execute("CREATE TABLE docente (nomeDocente TEXT, codigo TEXT PRIMARY KEY)")
        self.cursor.execute("CREATE TABLE DocenteMinistraDisc (codigoDocente TEXT, codigoDisciplina INT, id INTEGER PRIMARY KEY AUTOINCREMENT)")
        self.cursor.execute("CREATE TABLE DiscTemRequis (id INTEGER PRIMARY KEY AUTOINCREMENT, codigoDisciplina TEXT, codigoRequisito INT, tipoReq TEXT, cursoNome TEXT, cursoID TEXT, periodoIdeal INT)")

    def dump(self):
            self.cursor.execute("SELECT * FROM unidade")
            print(self.cursor.fetchall())
            print()
            self.cursor.execute("SELECT * FROM docente")
            print(self.cursor.fetchall())
            print()
            self.cursor.execute("SELECT * FROM disciplina")
            print(self.cursor.fetchall())
            print()
            self.cursor.execute("SELECT * FROM DocenteMinistraDisc")
            print(self.cursor.fetchall())
            print()
            self.cursor.execute("SELECT * FROM DiscTemRequis")
            print(self.cursor.fetchall())

    def close(self):
        self.conn.close()

    def insertUnidade(self, nome, codigo):
        sql = ("INSERT INTO unidade(nomeUnidade, codigoUnidade) VALUES (?,?);")
        val = (nome, codigo)
        try:
            self.cursor.execute(sql, val)
            self.conn.commit()
        except:
            self.conn.rollback()

    def insertDisciplina(self, info):
        sql = "INSERT INTO disciplina (nomeDisciplina, codigoDisciplina, ativacao, desativacao, CredAula, CredTrabalho, tipo, objetivos, programa, programaResumido, metodo, criterio, normaRecuperacao, bibliografia)  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        val = (info["nome"], info["codigo"], info["ativacao"], info["desativacao"], info["creditos_aula"], info["creditos_trabalho"], info["tipo"], info["objetivos"], info["programa"], info["programa_resumido"], info["metodo"], info["criterio"], info["norma_de_recuperacao"], info["bibliografia"])
        try:
            self.cursor.execute(sql, val)
            self.conn.commit()
        except:
            self.conn.rollback()

    def insertDocente(self, nomeDocente):
        sql = "INSERT INTO docente (nomeDocente, codigo)  VALUES (?, ?);"
        hash = hashlib.md5(nomeDocente.encode()).hexdigest()
        val = (nomeDocente, hash)
        try:
            self.cursor.execute(sql, val)
            self.conn.commit()
            return hash
        except:
            self.conn.rollback()
            return

    def insertDocenteDiciplina(self, codigoDocente, codigoDisciplina):
        sql = "INSERT INTO DocenteMinistraDisc (codigoDocente, codigoDisciplina)  VALUES (?, ?);"
        val = (codigoDocente, codigoDisciplina)
        try:
            self.cursor.execute(sql, val)
            self.conn.commit()
        except:
            self.conn.rollback()

    def insereDisciplinaUnidade(codigoUnidade ,codigoDisciplina):
        sql = "INSERT INTO UnidLessionaDisc (codigoUnidade, codigoDisciplina)  VALUES (?, ?);"
        val = (codigoUnidade, codigoDisciplina)
        try:
            self.cursor.execute(sql, val)
            self.conn.commit()
        except:
            self.conn.rollback()

    def insereDisciplinaRequisito(self, codigoDisciplina ,codigoRequisito, tipoReq, cursoNome, cursoID, periodoIdeal):
        sql = "INSERT INTO DiscTemRequis (codigoDisciplina ,codigoRequisito, tipoReq, cursoNome, cursoID, periodoIdeal)  VALUES (?, ?, ?, ? , ?, ?);"
        val = (codigoDisciplina ,codigoRequisito, tipoReq, cursoNome, cursoID, periodoIdeal)

        try:
            self.cursor.execute(sql, val)
            self.conn.commit()
        except:
            self.conn.rollback()

    def insertDiciplinaUnidade(self, codigoUnidade, codigoDisciplina):
        sql = "INSERT INTO UnidLessionaDisc (codigoUnidade, codigoDisciplina)  VALUES (?, ?);"
        val = (codigoUnidade, codigoDisciplina)
        try:
            self.cursor.execute(sql, val)
            self.conn.commit()
        except:
            self.conn.rollback()
