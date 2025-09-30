import os
from dotenv import load_dotenv
import re
import json
import unicodedata
import tempfile
import uuid
import hashlib
import openai
import pdfplumber
import pytesseract
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import TreebankWordTokenizer
import nltk

# garantir recursos nltk
for r in ["tokenizers/punkt", "corpora/stopwords"]:
    try:
        nltk.data.find(r)
    except LookupError:
        nltk.download(r.split('/')[-1])

# Carregar .env se estiver disponível (garante que testes locais/venv vejam as variáveis)
try:
    load_dotenv()
except Exception:
    pass


def extract_text(file_storage):
    if not file_storage:
        return None
    filename = file_storage.filename.lower()
    if filename.endswith('.txt'):
        data = file_storage.read()
        return data if isinstance(data, str) else data.decode('utf-8', errors='ignore')
    if filename.endswith('.pdf'):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        try:
            try:
                if hasattr(file_storage, 'stream'):
                    file_storage.stream.seek(0)
            except Exception:
                pass
            file_storage.save(tmp.name)
            tmp.close()
            pages = []
            with pdfplumber.open(tmp.name) as pdf:
                for p in pdf.pages:
                    txt = p.extract_text()
                    if not txt or not txt.strip():
                        img = p.to_image(resolution=300).original
                        txt = pytesseract.image_to_string(img, lang='por')
                    pages.append((txt or '').strip())
            return '\n'.join(pages)
        finally:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass
    return ''


def clean_placeholders(text, support_phone=None, support_email=None):
    if not text:
        return text
    result = text
    phone_patterns = [r"\(?inserir(?:\s|-)?(?:o\s)?(?:n[uú]mero|telefone|tel)\)?", r"\[inserir(?:\s|-)?(?:n[uú]mero|telefone)\]"]
    email_patterns = [r"\(?inserir(?:\s|-)?e-?mail\)?", r"\[inserir(?:\s|-)?e-?mail\]"]
    for p in phone_patterns:
        if support_phone:
            result = re.sub(p, support_phone, result, flags=re.IGNORECASE)
        else:
            result = re.sub(p, 'nosso suporte', result, flags=re.IGNORECASE)
    for p in email_patterns:
        if support_email:
            result = re.sub(p, support_email, result, flags=re.IGNORECASE)
        else:
            result = re.sub(p, 'nosso e-mail de suporte', result, flags=re.IGNORECASE)
    result = re.sub(r'\s{2,}', ' ', result).strip()
    return result


def call_openai_chat(messages, model='gpt-3.5-turbo', max_tokens=700, temperature=0.1):
    try:
        from openai import OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print('[OpenAI v2] Erro: OPENAI_API_KEY não está definido no ambiente.')
            return None
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return resp.choices[0].message.content
    except Exception:
        import traceback
        print('[OpenAI v2] Erro detalhado:\n', traceback.format_exc())
        return None


def classify_email(text, support_phone=None, support_email=None):

    # Saudações simples: resposta curta e simpática

    saudacoes_simples = [
        'bom dia', 'boa tarde', 'boa noite', 'olá', 'ola', 'oi'
    ]
    # agradecimentos_simples removido: IA sempre gera resposta
    texto_limpo = (text or '').strip().lower()
    if texto_limpo in ['olá, tudo bem?', 'ola, tudo bem?', 'olá tudo bem?', 'ola tudo bem?']:
        return 'Improdutivo', 'Olá! Agradecemos sua mensagem. Tenha um excelente dia. ' + os.getenv('NOME_ASSINATURA', 'Leandro da Silva Stampini')
    if any(texto_limpo == s or texto_limpo.startswith(s + ' ') or texto_limpo.endswith(' ' + s) or texto_limpo == s for s in saudacoes_simples):
        return 'Improdutivo', 'Olá! Agradecemos sua mensagem. Tenha um excelente dia. ' + os.getenv('NOME_ASSINATURA', 'Leandro da Silva Stampini')

    # Regra: agradecimento puro é improdutivo, mas se houver solicitação/problema junto, é produtivo
    agradecimentos = [
        'obrigado', 'obrigada', 'muito obrigado', 'muito obrigada'
    ]
    texto_limpo_sem_pontuacao = re.sub(r'[.!?,;:]', '', texto_limpo)
    contem_agradecimento = any(agr in texto_limpo_sem_pontuacao for agr in agradecimentos)
    # Palavras-chave que indicam solicitação, dúvida ou problema (exceto palavras neutras como 'suporte', 'ajuda', 'atendimento')
    palavras_produtivas = [
        'preciso', 'solicito', 'poderia', 'gostaria', 'necessito', 'aguardo', 'favor', 'por favor', 'problema', 'erro', 'dúvida', 'duvida', 'acesso', 'atualização', 'atualizacao', 'relatório', 'relatorio', 'parecer', 'urgente', 'resposta', 'encaminho', 'envio', 'anexo', 'documento', 'reclamação', 'reclamacao', 'dificuldade', 'instabilidade', 'não consigo', 'nao consigo', 'não acessa', 'nao acessa', 'não abre', 'nao abre', 'não carrega', 'nao carrega', 'sistema', 'ticket', 'chamado', 'acessar', 'acessando', 'acessaram', 'acessou', 'acessarei', 'acessaria'
    ]
    contem_produtivo = any(p in texto_limpo_sem_pontuacao for p in palavras_produtivas)
    # Se for agradecimento puro ou agradecimento + menção a suporte/ajuda/atendimento, mas sem solicitação explícita, é improdutivo
    palavras_neutras = ['suporte', 'ajuda', 'atendimento']
    contem_neutro = any(n in texto_limpo_sem_pontuacao for n in palavras_neutras)
    if contem_agradecimento and (not contem_produtivo) and (not contem_neutro or contem_neutro):
        return 'Improdutivo', 'Olá! Agradecemos sua mensagem. Tenha um excelente dia. ' + os.getenv('NOME_ASSINATURA', 'Leandro da Silva Stampini')

    nome = os.getenv('NOME_ASSINATURA', 'Leandro da Silva Stampini')
    empresa = os.getenv('EMPRESA_ASSINATURA', 'AUTOU')

    # Normalização para apenas duas categorias (remoção de acentos para comparações)
    def _strip_accents(s):
        if not s:
            return ''
        return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))

    texto_lower = _strip_accents((text or '').lower())
    ambig_palavras = [
        'olá', 'tudo bem', 'bom dia', 'boa tarde', 'boa noite', 'oi', 'saudações', 'cumprimentos', 'como vai', 'espero que esteja bem', 'espero que estejam bem'
    ]
    improdutivo_keywords = [
        'improdutivo', 'felicita', 'felicitação', 'felicitações', 'feliz aniversário', 'feliz natal', 'boas festas',
        'obrigado', 'obrigada', 'agradecimento', 'agradecimentos', 'agradecer', 'paraben', 'parabéns', 'sem ação', 'irrelevante',
        'informativo', 'spam', 'saudação', 'saudações', 'cumprimentos', 'bom dia', 'boa tarde', 'boa noite',
        'tudo bem', 'como vai', 'espero que esteja bem', 'espero que estejam bem', 'mensagem social', 'mensagem pessoal'
    ]
    produtivo_keywords = [
        'produtivo', 'suporte', 'ação', 'atualização', 'dúvida', 'tecnico', 'técnico', 'problema', 'reclamação',
        'pedido', 'solicitação', 'solicito', 'urgente', 'resposta', 'relatório', 'análise', 'parecer técnico', 'documento',
        'em anexo', 'segue em anexo', 'envio', 'encaminho', 'aguardo retorno', 'aguardo parecer', 'aguardo resposta',
        'retorno', 'parecer', 'verificar', 'orientação', 'dificuldade', 'acesso', 'instabilidade', 'suporte técnico',
        'problemas', 'acessar', 'acessando', 'acessaram', 'acessou', 'acessando', 'acessarei', 'acessaria',
        # Adicionados para tratar casos mencionados pelo usuário
        'sistema parado', 'preciso de suporte', 'ajuda com lentidão', 'sistema', 'lentidão', 'parado', 'erro no sistema',
        'sistema fora', 'sistema caiu', 'sistema não funciona', 'sistema travado', 'sistema instável', 'sistema lento',
        'problema no sistema', 'problemas no sistema', 'não consigo acessar', 'não acessa', 'não abre', 'não carrega',
        'preciso de ajuda', 'preciso de atendimento', 'preciso de suporte', 'ajuda', 'atendimento', 'suporte', 'parou', 'parada'
    ]

    # Normalizar listas de palavras-chave (remover acentos)
    improdutivo_norm = [_strip_accents(w.lower()) for w in improdutivo_keywords]
    produtivo_norm = [_strip_accents(w.lower()) for w in produtivo_keywords]

    # função utilitária para checar palavra inteira (evita colisões como 'produtivo' em 'improdutivo')
    def _contains_word(s, w):
        try:
            return re.search(r"\b" + re.escape(w) + r"\b", s) is not None
        except Exception:
            return w in s

    # Use heuristic for classification (count matches)
    count_prod = sum(1 for p in produtivo_norm if _contains_word(texto_lower, p))
    count_imp = sum(1 for p in improdutivo_norm if _contains_word(texto_lower, p))
    if count_prod > count_imp:
        categoria_final = 'Produtivo'
    elif count_imp > count_prod:
        categoria_final = 'Improdutivo'
    elif any(word in texto_lower for word in ambig_palavras):
        categoria_final = 'Improdutivo'
    else:
        # fallback: assume produtivo se houver perguntas ou solicitações
        if '?' in text or 'por favor' in texto_lower or 'poderia' in texto_lower or 'solicito' in texto_lower or 'aguardo' in texto_lower or 'anexo' in texto_lower or 'relatório' in texto_lower or 'parecer' in texto_lower or 'gostaria' in texto_lower or 'como' in texto_lower:
            categoria_final = 'Produtivo'
        else:
            categoria_final = 'Improdutivo'

    # Use AI for response generation based on categoria_final
    system = (
        f"Você é um assistente para a empresa {empresa} e deverá assinar como {nome}."
        f" O email foi classificado como '{categoria_final}'. Gere uma resposta adequada."
        " Aqui estão exemplos de respostas adequadas:\n\n"
        "Para emails Produtivos (que exigem ação):\n"
        "- 'Olá! Recebemos sua solicitação sobre o problema de acesso à plataforma. Um ticket de suporte (#TICKET-2023-XYZ) foi aberto e nossa equipe técnica já está investigando o ocorrido. Entraremos em contato com uma atualização em até 60 minutos. Agradecemos a sua paciência.'\n"
        "- 'Olá. Agradecemos o seu contato. Estamos verificando o status atual da sua transferência internacional (protocolo 456789) junto ao nosso time de operações. Um de nossos especialistas enviará uma atualização detalhada sobre o processo em breve. Obrigado por aguardar.'\n"
        "- 'Prezado, recebemos sua dúvida sobre o informe de rendimentos do fundo. Sua pergunta foi encaminhada para um de nossos especialistas em tributação de investimentos. Ele irá analisar sua questão e responderá diretamente a este e-mail com todos os esclarecimentos necessários. Agradecemos o contato.'\n\n"
        "Para emails Improdutivos (sociais ou informativos):\n"
        "- 'Olá! Ficamos muito felizes em saber que sua experiência foi positiva e que conseguimos ajudar. Seu feedback é muito importante para nós! Agradecemos o seu contato e desejamos um excelente dia.'\n"
        "- 'Olá! Agradecemos imensamente seus votos. Nós também desejamos a você um excelente Natal e um Ano Novo próspero e cheio de alegrias. Boas festas!'\n"
        "- 'Olá. Agradecemos o seu contato. No entanto, informamos que este canal é dedicado exclusivamente para suporte e dúvidas sobre nossos produtos e serviços financeiros. Para outras solicitações, por favor, utilize nossos canais de comunicação alternativos. Tenha um bom dia.'\n\n"
        " Retorne **somente** o texto da resposta, com assinatura inclusa."
    )
    user_prompt = "Gere a resposta para o email: " + text

    out_resp = call_openai_chat([{'role': 'system', 'content': system}, {'role': 'user', 'content': user_prompt}], model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'))
    if out_resp:
        resposta = out_resp.strip()
    else:
        resposta = "Não foi possível gerar resposta."
    resposta = clean_placeholders(resposta, support_phone, support_email)
    return categoria_final, resposta
