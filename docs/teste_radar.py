import urllib.request
import json

def test_radar():
    # 1. Testar OpenAlex pelo ORCID de Aramys Silva dos Reis (0000-0003-4999-6382)
    orcid = "https://orcid.org/0000-0003-4999-6382"
    url = f"https://api.openalex.org/works?filter=author.orcid:{orcid}&per_page=10"
    req = urllib.request.Request(url, headers={'User-Agent': 'LattesFacil/1.0 (mailto:suporte@lattesfacil.com.br)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            total = data.get('meta', {}).get('count', 0)
            print(f"OpenAlex Works pelo ORCID: {total}")
            for w in data.get('results', [])[:5]:
                title = w.get('title')
                year = w.get('publication_year')
                doi = w.get('doi')
                print(f"  * [{year}] {title} (DOI: {doi})")
    except Exception as e:
        print("Erro OpenAlex:", e)

    # 2. Testar CrossRef por nome
    author_query = "Aramys+Silva+dos+Reis"
    url_cr = f"https://api.crossref.org/works?query.author={author_query}&rows=5"
    req_cr = urllib.request.Request(url_cr, headers={'User-Agent': 'LattesFacil/1.0 (mailto:suporte@lattesfacil.com.br)'})
    try:
        with urllib.request.urlopen(req_cr, timeout=10) as response:
            data_cr = json.loads(response.read().decode('utf-8'))
            total_cr = data_cr.get('message', {}).get('total-results', 0)
            print(f"\nCrossRef Works pelo Nome: {total_cr}")
            for item in data_cr.get('message', {}).get('items', [])[:5]:
                t = item.get('title', [''])[0]
                d = item.get('DOI', '')
                print(f"  * {t} (DOI: {d})")
    except Exception as e:
        print("Erro CrossRef:", e)

if __name__ == '__main__':
    test_radar()
