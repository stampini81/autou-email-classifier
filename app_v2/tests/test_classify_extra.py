def test_classify_improdutivo_spam():
    texto = "Você ganhou um prêmio! Clique aqui para resgatar."
    categoria, resposta = classify_email(texto)
    assert categoria == "Improdutivo"
    assert isinstance(resposta, str) and resposta

def test_classify_improdutivo_boas_festas():
    texto = "Boas festas e um próspero ano novo!"
    categoria, resposta = classify_email(texto)
    assert categoria == "Improdutivo"
    assert isinstance(resposta, str) and resposta

def test_classify_improdutivo_sem_acao():
    texto = "Apenas informando que estarei ausente amanhã."
    categoria, resposta = classify_email(texto)
    assert categoria == "Improdutivo"
    assert isinstance(resposta, str) and resposta

from app_v2.utils import classify_email


def test_classify_ambiguidade():
    texto = "Olá, tudo bem?"
    categoria, resposta = classify_email(texto)
    # Ambiguidade deve cair em improdutivo por padrão
    assert categoria == "Improdutivo"
    assert isinstance(resposta, str) and resposta


def test_classify_informativo():
    texto = "Apenas informando que estarei ausente amanhã."
    categoria, resposta = classify_email(texto)
    assert categoria == "Improdutivo"
    assert isinstance(resposta, str) and resposta


def test_classify_pedido_claro():
    texto = "Solicito atualização do meu cadastro."
    categoria, resposta = classify_email(texto)
    assert categoria == "Produtivo"
    assert isinstance(resposta, str) and resposta


def test_classify_pergunta():
    texto = "Vocês poderiam me enviar o relatório do mês passado?"
    categoria, resposta = classify_email(texto)
    assert categoria == "Produtivo"
    assert isinstance(resposta, str) and resposta
