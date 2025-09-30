"""Script de verificação rápido para rodar classify_email sobre os exemplos em teste/.
Imprime o nome do arquivo, conteúdo (resumido), categoria prevista (pelo nome do arquivo) e categoria obtida.
"""
import os
import sys
# Garantir que o diretório do projeto esteja no sys.path para permitir import de app_v2
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from app_v2.utils import classify_email
import pdfplumber

TEST_DIR = os.path.join(os.path.dirname(__file__), '..', 'teste')

def expected_from_name(name):
    n = name.lower()
    # verificar 'improdutivo' antes de 'produtivo' porque a substring 'produtivo'
    # também aparece em 'improdutivo'
    if 'improdutivo' in n:
        return 'Improdutivo'
    if 'produtivo' in n:
        return 'Produtivo'
    return 'Desconhecido'


def read_file(path):
    # Se PDF, tentar extrair texto simples procurando por '%%EOF' como heurística
    with open(path, 'rb') as f:
        data = f.read()
    # se PDF, usar pdfplumber para extração mais precisa
    if path.lower().endswith('.pdf'):
        try:
            with pdfplumber.open(path) as pdf:
                pages = [p.extract_text() or '' for p in pdf.pages]
            return '\n'.join(pages)
        except Exception:
            try:
                text = data.decode('latin-1', errors='ignore')
                return ' '.join([l.strip() for l in text.splitlines() if len(l.strip()) > 20])
            except Exception:
                return ''
    try:
        return data.decode('utf-8')
    except Exception:
        return data.decode('latin-1', errors='ignore')


if __name__ == '__main__':
    files = [f for f in os.listdir(TEST_DIR) if not f.startswith('.')]
    for fn in files:
        path = os.path.join(TEST_DIR, fn)
        txt = read_file(path)
        txt_short = txt.strip().replace('\n', ' ')[:200]
        exp = expected_from_name(fn)
        cat, resp = classify_email(txt)
        print(f"File: {fn}\nExpected: {exp} | Got: {cat}\nText: {txt_short}\nResponse (short): {resp[:120]}\n{'-'*60}")
