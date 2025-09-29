import pytest
from unittest.mock import patch
from app_v2.utils import classify_email

@pytest.fixture(autouse=True)
def mock_openai():
    # Mapeamento de texto para categoria simulada
    def fake_call_openai_chat(messages, model='gpt-3.5-turbo', max_tokens=700, temperature=0.1):
        user_content = messages[-1]['content'].lower()
        if 'acesso ao sistema' in user_content or 'preciso de ajuda' in user_content or 'atualização do meu cadastro' in user_content or 'reclamação' in user_content or 'urgente' in user_content or 'relatório do mês passado' in user_content or 'solicito' in user_content or 'problemas para acessar' in user_content or 'por favor' in user_content or 'gostaria de saber' in user_content:
            return '{"categoria": "Produtivo", "resposta": "Resposta simulada produtivo."}'
        if 'feliz natal' in user_content or 'feliz aniversário' in user_content or 'obrigado' in user_content or 'boas festas' in user_content or 'prêmio' in user_content or 'ausente' in user_content or 'informamos que o sistema estará em manutenção' in user_content or 'olá, tudo bem' in user_content or 'ola, tudo bem' in user_content or 'olá tudo bem' in user_content or 'ola tudo bem' in user_content:
            return '{"categoria": "Improdutivo", "resposta": "Resposta simulada improdutivo."}'
        return '{"categoria": "Improdutivo", "resposta": "Resposta default improdutivo."}'
    with patch('app_v2.utils.call_openai_chat', side_effect=fake_call_openai_chat):
        yield
