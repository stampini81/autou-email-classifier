def test_classify_produtivo_solicitacao():
    texto = "Por favor, poderia liberar meu acesso ao sistema?"
    categoria, resposta = classify_email(texto)
    assert categoria == "Produtivo"
    assert isinstance(resposta, str) and resposta

def test_classify_produtivo_reclamacao():
    texto = "Estou com problemas para acessar minha conta."
    categoria, resposta = classify_email(texto)
    assert categoria == "Produtivo"
    assert isinstance(resposta, str) and resposta

def test_classify_produtivo_urgente():
    texto = "Preciso de uma resposta urgente sobre o contrato."
    categoria, resposta = classify_email(texto)
    assert categoria == "Produtivo"
    assert isinstance(resposta, str) and resposta

from app_v2.utils import classify_email


def test_classify_produtivo():
    texto = "Preciso de ajuda com meu acesso ao sistema."
    categoria, resposta = classify_email(texto)
    assert categoria == "Produtivo"
    assert isinstance(resposta, str) and resposta


def test_classify_improdutivo():
    texto = "Feliz Natal e um ótimo ano novo!"
    categoria, resposta = classify_email(texto)
    assert categoria == "Improdutivo"
    assert isinstance(resposta, str) and resposta


def test_classify_agradecimento():
    texto = "Muito obrigado pelo suporte."
    categoria, resposta = classify_email(texto)
    assert categoria == "Improdutivo"
    assert isinstance(resposta, str) and resposta


def test_classify_duvida():
    texto = "Gostaria de saber como atualizar meus dados cadastrais."
    categoria, resposta = classify_email(texto)
    assert categoria == "Produtivo"
    assert isinstance(resposta, str) and resposta
