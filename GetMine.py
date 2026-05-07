import os
import time
import re
from curl_cffi import requests

# Configurações
PASTA_DESTINO = "assets_final"
API_URL = "https://minecraft.wiki/api.php"

# Links baseados no que você encontrou (Usando o formato RAW para o Python conseguir ler)
URLS_JSON = [
    "https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data/bedrock/1.20.0/items.json",
    "https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data/bedrock/1.20.0/blocks.json"
]

if not os.path.exists(PASTA_DESTINO):
    os.makedirs(PASTA_DESTINO)

def obter_nomes_da_lista():
    nomes_totais = []
    print("Coletando nomes dos links que você encontrou...")
    
    for url in URLS_JSON:
        try:
            response = requests.get(url, impersonate="chrome120")
            if response.status_code == 200:
                dados = response.json()
                for item in dados:
                    # Tenta displayName primeiro (ex: "Oak Planks"), se não tiver, usa o name técnico
                    nome = item.get('displayName') or item.get('name')
                    if nome:
                        nomes_totais.append(nome)
            else:
                print(f"Erro ao acessar {url}: Status {response.status_code}")
        except Exception as e:
            print(f"Falha na URL {url}: {e}")
    
    return sorted(list(set(nomes_totais)))

def baixar_da_wiki(item_name):
    # Formata nome para salvar (ex: "Oak Planks" -> "oak_planks.png")
    nome_arquivo = item_name.lower().replace(" ", "_")
    nome_arquivo = re.sub(r'[\\/*?:"<>|]', '', nome_arquivo) + ".png"
    
    caminho_save = os.path.join(PASTA_DESTINO, nome_arquivo)
    
    if os.path.exists(caminho_save):
        return

    params = {
        "action": "query",
        "format": "json",
        "titles": f"File:{item_name}.png",
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
        pass
    return False

if __name__ == "__main__":
    lista = obter_nomes_da_lista()
    total = len(lista)
    print(f"Sucesso! {total} itens/blocos prontos para busca.")
    
    for i, nome in enumerate(lista):
        baixar_da_wiki(nome)
        if i % 10 == 0 and i > 0:
            print(f"Progresso: {i}/{total}...")
            time.sleep(0.3)

    print("\nProcesso finalizado!")