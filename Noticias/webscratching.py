import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import time
import random

# Configuración de sitios y categorías
SITIOS = {
    "El Mundo": {
        "base_url": "https://www.elmundo.es",
        "categorias": {
            "Salud": "/ciencia-y-salud/salud",
            "Economía": "/economia",
            "Motor": "/motor",
            "Deportes": "/deportes",
            "Religión": "/t/re/religion.html",
            "Política": "/t/po/politica.html",
            "Ocio": "/cultura.html",
            "Moda": "/tendencias.html",
            "Informática": "/tecnologia.html",
            "Astronomía": "/ciencia-y-salud/ciencia/astronomia.html",
            "Alimentación": "/vida-sana/alimentacion.html",
            "Militar": "/internacional/ejercito.html",
        }
    },
    "El País": {
        "base_url": "https://elpais.com",
        "categorias": {
            "Salud": "/salud-y-bienestar/",
            "Economía": "/economia/",
            "Motor": "https://motor.elpais.com/",
            "Deportes": "/deportes/",
            "Religión": "/sociedad/",
            "Política": "/internacional/",
            "Ocio": "/cultura",
            "Moda": "/smoda/",
            "Informática": "/tecnologia",
            "Astronomía": "/ciencia",
            "Alimentación": "/gastronomia/",
            "Militar": "/internacional/defensa/",
        }
    },
    "ABC": {
        "base_url": "https://www.abc.es",
        "categorias": {
            "Salud": "/salud/",
            "Economía": "/economia",
            "Motor": "/summum/motor/",
            "Deportes": "/deportes",
            "Religión": "/sociedad/",
            "Política": "/internacional/",
            "Ocio": "/cultura",
            "Moda": "/summum/estilo/",
            "Informática": "/tecnologia",
            "Astronomía": "/ciencia",
            "Alimentación": "/gastronomia",
            "Militar": "/internacional/defensa/",
        }
    },
    "La Razón": {
        "base_url": "https://www.larazon.es",
        "categorias": {
            "Salud": "/salud/",
            "Economía": "/economia/",
            "Motor": "/motor/",
            "Deportes": "/deportes/",
            "Religión": "/religion/",
            "Política": "/espana/politica/",
            "Ocio": "/cultura/",
            "Moda": "/lifestyle/moda-belleza/",
            "Informática": "/tecnologia/",
            "Astronomía": "/ciencia/",
            "Alimentación": "/gastronomia/",
            "Militar": "/internacional/defensa/",
        }
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9"
}

def obtener_primer_parrafo(url):
    """Extrae el primer párrafo de un artículo asegurando que es contenido real."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ No se pudo acceder a {url} (Código: {response.status_code})")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        parrafos = soup.select("article p") or soup.select("div p")
        
        for parrafo in parrafos:
            texto = parrafo.get_text(strip=True)
            if len(texto) > 50:  # Evita párrafos demasiado cortos o irrelevantes
                return texto
        
        return None
    except Exception as e:
        print(f"❌ Error al obtener el párrafo de {url}: {e}")
        return None

def scrapear_sitio(sitio, nombre_categoria, base_url, categoria_url, target, max_pages, contador):
    """Extrae noticias de un sitio web específico."""
    noticias = []
    visited_urls = set()
    full_url = categoria_url if categoria_url.startswith("http") else urljoin(base_url, categoria_url)
    paginas_sin_resultados = 0
    
    for current_page in range(1, max_pages + 1):
        if len(noticias) >= target:
            break
        
        url_actual = full_url if current_page == 1 else f"{full_url}/pag{current_page}"
        print(f"📄 Explorando: {url_actual} (Página {current_page}) - {nombre_categoria} en {sitio}")

        try:
            response = requests.get(url_actual, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                paginas_sin_resultados += 1
                if paginas_sin_resultados >= 5:
                    break
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            articulos = soup.select("article") or soup.select("div")
            if not articulos:
                paginas_sin_resultados += 1
                if paginas_sin_resultados >= 5:
                    break
                continue
            else:
                paginas_sin_resultados = 0

            for articulo in articulos:
                if len(noticias) >= target:
                    return noticias, contador
                enlace = articulo.find('a', href=True)
                if enlace:
                    url_completa = urljoin(full_url, enlace['href'])
                    if url_completa in visited_urls:
                        continue
                    visited_urls.add(url_completa)
                    parrafo = obtener_primer_parrafo(url_completa)
                    if parrafo:
                        noticias.append({"categoria": nombre_categoria, "parrafo": parrafo})
                        print(f"✅ {contador}. {parrafo[:80]}...")
                        contador += 1
                    time.sleep(random.uniform(0.2, 0.8))
        except Exception as e:
            print(f"❌ Error en {url_actual}: {e}")
            break
    
    return noticias, contador

def scrapear_categoria(nombre_categoria, target=150, max_pages=50):
    """Extrae hasta 150 noticias combinando todos los sitios web."""
    noticias_categoria = []
    contador = 1
    
    for sitio, datos in SITIOS.items():
        if nombre_categoria in datos["categorias"]:
            url = datos["categorias"][nombre_categoria]
            noticias, contador = scrapear_sitio(sitio, nombre_categoria, datos["base_url"], url, target-len(noticias_categoria), max_pages, contador)
            noticias_categoria.extend(noticias)
            if len(noticias_categoria) >= target:
                break  # Si alcanzamos las 150 noticias, detenemos la búsqueda
    
    return noticias_categoria

# Ejecutar scraping por categoría y guardar en archivos de texto
for categoria in SITIOS["El Mundo"]["categorias"].keys():
    noticias = scrapear_categoria(categoria, target=150, max_pages=50)
    
    # Guardar en archivo de texto
    if noticias:
        file_path = fr"C:\Users\jjavi\Downloads\RedNeuronal\Noticias\{categoria}.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("\n\n".join([n["parrafo"] for n in noticias]))
        print(f"📂 Archivo guardado: {file_path}")  # Ahora la indentación es correcta


# Lista global de noticias
TODAS_NOTICIAS = []
contador_global = 1

# Ejecutar el scraping
for categoria in SITIOS["El Mundo"]["categorias"].keys():
    noticias_categoria_total = []
    for sitio, datos in SITIOS.items():
        if categoria in datos["categorias"]:
            url = datos["categorias"][categoria]
            print(f"\n=== Scrapeando: {categoria} en {sitio} ===")
            noticias_categoria = scrapear_categoria(categoria, target=150, max_pages=50)
            noticias_categoria_total.extend(noticias_categoria)

    TODAS_NOTICIAS.extend(noticias_categoria_total)
    print(
        f"✅ Total de noticias obtenidas para {categoria}: {len(noticias_categoria_total)}"
    )

# Guardar datos en CSV
if TODAS_NOTICIAS:
    with open("noticias_multisitio.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Número", "Sitio", "Categoría", "Fuente", "Título", "Primer Párrafo"]
        )
        for noticia in TODAS_NOTICIAS:
            writer.writerow(
                [
                    noticia["numero"],
                    noticia["sitio"],
                    noticia["categoria"],
                    noticia["fuente"],
                    noticia["titulo"],
                    noticia["parrafo"],
                ]
            )
    print(f"\n🎉 ¡Scraping finalizado! Total de noticias: {len(TODAS_NOTICIAS)}.")
else:
    print(
        "❌ No se encontraron noticias. Verifica las URLs y la estructura de los sitios web."
    )