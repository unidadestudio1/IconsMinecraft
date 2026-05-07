import os
import time
import re
import json  # Importante para gerar o arquivo final
from curl_cffi import requests

# Configurações
PASTA_DESTINO = "assets_final"
API_URL = "https://minecraft.wiki/api.php"
GITHUB_BASE_URL = "https://raw.githubusercontent.com/unidadestudio1/IconsMinecraft/main/assets_final/"

URLS_JSON = [
    "https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data/pc/1.21.9/items.json",
    "https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data/pc/1.21.9/blocks.json",
    "https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data/pc/1.21.9/entities.json"
]

NOMES_EXTRAS = [
    "Wooden", "Golden", "Iron", "Diamond", "Stone", "Copper", "Netherite",
    "Wooden Spear", "Golden Spear", "Iron Spear", "Diamond Spear", 
    "Stone Spear", "Copper Spear", "Netherite Spear", "Held Stone Spear", 
    "Minerito Spear", "Spear"
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
    nomes_totais.extend(NOMES_EXTRAS)
    return sorted(list(set(nomes_totais)))

def baixar_da_wiki(item_name):
    # Formata nome para o arquivo (ex: "Wooden Sword" -> "wooden_sword.png")
    nome_limpo = re.sub(r'[\\/*?:"<>|]', '', item_name)
    nome_arquivo = nome_limpo.lower().replace(" ", "_") + ".png"
    caminho_save = os.path.join(PASTA_DESTINO, nome_arquivo)
    
    # Se já existir, apenas retornamos o nome para o JSON
    if os.path.exists(caminho_save):
        return nome_arquivo

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
                    return nome_arquivo
        except:
            continue
    return None

if __name__ == "__main__":
    lista_nomes = obter_nomes_da_lista()
    total = len(lista_nomes)
    assets_json = []  # Lista que guardará os dados para o JSON

    print(f"Sucesso! {total} nomes na lista de busca.")
    
    for i, nome in enumerate(lista_nomes):
        nome_arquivo_gerado = baixar_da_wiki(nome)
        
        # Se conseguimos a imagem (baixando agora ou se já existia)
        if nome_arquivo_gerado:
            assets_json.append({
                "name": nome,
                "icon": GITHUB_BASE_URL + nome_arquivo_gerado
            })

        if i % 20 == 0 and i > 0:
            print(f"Progresso: {i}/{total}...")
            time.sleep(0.1)

    # Salva o arquivo JSON final
    with open("minecraft_assets.json", "w", encoding="utf-8") as f:
        json.dump(assets_json, f, indent=2, ensure_ascii=False)

    print(f"\nProcesso finalizado! O arquivo 'minecraft_assets.json' foi criado com {len(assets_json)} itens.")