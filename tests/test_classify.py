import io
import os
import pytest
from app.main import app, db, extract_text, classify_email

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_extract_txt():
    # Simulate a file-like object for a txt file
    data = io.BytesIO(b"Este e um teste de arquivo txt.\nlinha 2")
    data.filename = 'teste.txt'
    text = extract_text(data)
    assert 'teste de arquivo' in text.lower()

def test_support_fallback():
    text = 'Estou com dificuldades para acessar o sistema, aparece erro 500.'
    cat, resp = classify_email(text)
    assert cat.lower() == 'produtivo'
    assert 'recebemos sua solicitação' in resp.lower()

def test_classify_endpoint_ambiguous(client):
    # Submit both form text and a file to trigger ambiguous
    data = {
        'emailText': 'vai chover?'
    }
    # construct a simple in-memory file
    file_data = (io.BytesIO(b"curriculo\nExperiencia: ..."), 'curriculo.txt')
    resp = client.post('/classify', data={**data, 'emailFile': file_data}, content_type='multipart/form-data')
    assert resp.status_code == 400
    j = resp.get_json()
    assert j is not None and j.get('ambiguous') is True
