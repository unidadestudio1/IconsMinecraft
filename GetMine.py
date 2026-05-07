import os
import time
import re
from curl_cffi import requests

# Configurações
PASTA_DESTINO = "assets_final"
API_URL = "https://minecraft.wiki/api.php"

# Links oficiais
URLS_JSON = [
    "https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data/pc/1.21.9/items.json",
    "https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data/pc/1.21.9/blocks.json",
    "https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data/pc/1.21.9/entities.json"
]

# LISTA MANUAL: Adicione aqui os nomes que você quer forçar a busca
NOMES_EXTRAS = [
    "Wooden", # Tentei sem as chaves, pois a Wiki raramente usa {} nos nomes de arquivos
    "Golden", # Tentei sem as chaves, pois a Wiki raramente usa {} nos nomes de arquivos
    "Iron",
    "Diamond",
    "Stone",
    "Copper",
    "Netherite",
    "Wooden Spear", # Tentei sem as chaves, pois a Wiki raramente usa {} nos nomes de arquivos
    "Golden Spear", # Tentei sem as chaves, pois a Wiki raramente usa {} nos nomes de arquivos
    "Iron Spear",
    "Diamond Spear",
    "Stone Spear",
    "Copper Spear",
    "Netherite Spear",
    "Held Stone Spear", # Tentei sem as chaves, pois a Wiki raramente usa {} nos nomes de arquivos
    "Minerito Spear",
    "Spear"
]

if not os.path.exists(PASTA_DESTINO):
    os.makedirs(PASTA_DESTINO)

def obter_nomes_da_lista():
    nomes_totais = []
    print("Coletando nomes dos links oficiais...")
    
    for url in URLS_JSON:
        try:
            response = requests.get(url, impersonate="chrome120")
            if response.status_code == 200:
                dados = response.json()
                for item in dados:
                    nome = item.get('displayName') or item.get('name')
                    if nome:
                        nomes_totais.append(nome)
        except Exception as e:
            print(f"Falha na URL {url}: {e}")
    
    # Adiciona os nomes manuais à lista final
    nomes_totais.extend(NOMES_EXTRAS)
    
    return sorted(list(set(nomes_totais)))

def baixar_da_wiki(item_name):
    # Formata nome para salvar
    nome_arquivo = item_name.lower().replace(" ", "_")
    nome_arquivo = re.sub(r'[\\/*?:"<>|]', '', nome_arquivo) + ".png"
    
    caminho_save = os.path.join(PASTA_DESTINO, nome_arquivo)
    
    if os.path.exists(caminho_save):
        return False

    # Tenta buscar com .png e sem .png no título
    buscas = [f"File:{item_name}.png", f"File:{item_name}"]

    for titulo in buscas:
        params = {
            "action": "query",
            "format": "json",
            "titles": titulo,
            "prop": "imageinfo",
            "iiprop": "url"
        }

        try:
            res = requests.get(API_URL, params=params, impersonate="chrome120")
            data = res.json()
            pages = data.get("query", {}).get("pages", {})
            
            for page_id in pages:
                info = pages[page_id].get("imageinfo", [])
                if info:
                    url_final = info[0].get("url")
                    print(f"Baixando: {nome_arquivo}")
                    img_data = requests.get(url_final, impersonate="chrome120").content
                    with open(caminho_save, 'wb') as f:
                        f.write(img_data)
                    return True
        except:
            continue
    return False

if __name__ == "__main__":
    lista = obter_nomes_da_lista()
    total = len(lista)
    print(f"Sucesso! {total} nomes na lista de busca.")
    
    for i, nome in enumerate(lista):
        sucesso = baixar_da_wiki(nome)
        if i % 10 == 0 and i > 0:
            print(f"Progresso: {i}/{total}...")
            time.sleep(0.1)

    print("\nProcesso finalizado!")