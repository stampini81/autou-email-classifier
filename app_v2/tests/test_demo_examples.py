import os
import sys
import pytest

# permitir import do pacote quando os testes são executados
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app_v2.utils import classify_email
import pdfplumber

TEST_DIR = os.path.join(ROOT, 'teste')


def read_text(path):
    if path.lower().endswith('.pdf'):
        try:
            with pdfplumber.open(path) as pdf:
                return '\n'.join([p.extract_text() or '' for p in pdf.pages])
        except Exception:
            return ''
    with open(path, 'rb') as f:
        data = f.read()
    try:
        return data.decode('utf-8')
    except Exception:
        return data.decode('latin-1', errors='ignore')


@pytest.mark.parametrize('fname,expected', [
    ('Produtivo.txt', 'Produtivo'),
    ('Produtivo2.txt', 'Produtivo'),
    ('Produtivo.txt.pdf', 'Produtivo'),
    ('Improdutivo.txt', 'Improdutivo'),
    ('Improdutivo2.txt', 'Improdutivo'),
])
def test_examples(fname, expected):
    path = os.path.join(TEST_DIR, fname)
    assert os.path.exists(path), f"Arquivo de teste não encontrado: {path}"
    text = read_text(path)
    cat, resp = classify_email(text)
    # Só verificar a categoria (Produtivo/Improdutivo)
    assert cat in ['Produtivo', 'Improdutivo', 'Indefinido']
    assert cat == expected, f"Esperado {expected} para {fname}, obtido {cat}"
