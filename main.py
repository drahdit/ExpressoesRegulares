import requests
import re
from pathlib import Path
import sqlite3

url = "https://eventos.ifgoiano.edu.br/integra2026/"

resposta = requests.get(url)

if resposta.status_code == 200:
    with open("pagina.txt", "w", encoding="utf-8") as arquivo:
        arquivo.write(resposta.text)
        print("Download do HTML realizado com sucesso!")
else:
    print(f"Erro ao acessar a página: {resposta.status_code}")
    exit()

conexao = sqlite3.connect("event.db")
cursor = conexao.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS speaker (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(255) NOT NULL,
        work VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        image VARCHAR(255) NOT NULL
    )
''')

texto = "O contato é suporte@email.com e vendas.com"

caminho_arquivo = Path(__file__).parent / "pagina.txt"

padrao = r'(?<=<p class="card-text" style="color: black;">)[\w\W]+?(?=<\/p)'
conteudo = caminho_arquivo.read_text(encoding="utf-8")
resultadosnome = re.findall(padrao, conteudo)
print(resultadosnome)

padrao = '(?<=<h6>)[\w\W]+?(?=<\/h6)'
resultadoslocal = re.findall(padrao, conteudo)
print(resultadoslocal)

padrao = '(?<=<p>)[\w\W].*@[\w\W]+?(?=<\/p)'
resultadoscontato = re.findall(padrao, conteudo)
print(resultadoscontato)

padrao_img = r'(?<=src=")/media/static/palestrantes/[^"]+(?=")'
resultadosimg = re.findall(padrao_img, conteudo)

pasta_download = Path(__file__).parent / "download"
pasta_download.mkdir(exist_ok=True)

imagens_salvas = []
base_url = "https://eventos.ifgoiano.edu.br"

print("Baixando imagens...")
for caminho_img in resultadosimg:
    nome_arquivo = caminho_img.split("/")[-1] 
    caminho_completo_img = pasta_download / nome_arquivo
    
    if not caminho_completo_img.exists():
        img_url = base_url + caminho_img
        img_resposta = requests.get(img_url)
        if img_resposta.status_code == 200:
            caminho_completo_img.write_bytes(img_resposta.content)
            
    imagens_salvas.append(nome_arquivo)

print(f"{len(imagens_salvas)} imagens processadas/baixadas com sucesso!")

dados_para_inserir = []
for i in range(len(resultadosnome)):
    linha = (resultadosnome[i].strip(),
              resultadoslocal[i].strip(), 
              resultadoscontato[i].strip(),
              imagens_salvas[i].strip())
    dados_para_inserir.append(linha)

cursor.executemany('''
    INSERT INTO speaker (name, work, email, image) VALUES (?, ?, ?, ?)
''', dados_para_inserir)

conexao.commit()
conexao.close()
print(f"{len(dados_para_inserir)} registros foram salvos no banco de dados com sucesso!")