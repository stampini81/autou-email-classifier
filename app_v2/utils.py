import os
import re
import json
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
    # Forçar 'Olá, tudo bem?' como improdutivo
    if (text or '').strip().lower() in ['olá, tudo bem?', 'ola, tudo bem?', 'olá tudo bem?', 'ola tudo bem?']:
        resposta = clean_placeholders(resposta, support_phone, support_email) if 'resposta' in locals() else ''
        return 'Improdutivo', resposta or 'Mensagem de saudação detectada. Nenhuma ação necessária.'
    # Prompt estruturado para garantir saída previsível (JSON)
    nome = os.getenv('NOME_ASSINATURA', 'Leandro da Silva Stampini')
    empresa = os.getenv('EMPRESA_ASSINATURA', 'AUTOU')
    system = (
        f"Você é um assistente para a empresa {empresa} e deverá assinar como {nome}."
        " Receba o conteúdo do e-mail e retorne **somente** um JSON com duas chaves:"
        " 'categoria' (uma palavra ou expressão breve, ex: 'Suporte', 'Vendas', 'Spam', 'Ambiguidade')"
        " e 'resposta' (texto da resposta ao cliente, assinatura inclusa)."
        " Não inclua explicações adicionais fora do JSON."
    )

    user_prompt = (
        "Receba o e-mail abaixo e gere o JSON solicitado.\n\n---EMAIL---\n" + text + "\n---FIM---"
    )
    messages = [{'role': 'system', 'content': system}, {'role': 'user', 'content': user_prompt}]

    out = call_openai_chat(messages, model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'))
    if not out:
        return 'Indefinido', 'Não foi possível gerar resposta.'

    raw = out.strip()
    print('[app_v2] saída bruta do modelo:', raw[:1000])
    try:
        parsed = json.loads(raw)
        categoria = parsed.get('categoria') or parsed.get('category') or ''
        resposta = parsed.get('resposta') or parsed.get('response') or ''
    except Exception:
        # fallback heurístico
        categoria = ''
        resposta = raw
        for line in raw.splitlines():
            if line.lower().startswith('categoria:'):
                categoria = line.split(':', 1)[1].strip()
            if line.lower().startswith('resposta:'):
                resposta = line.split(':', 1)[1].strip() + ' ' + ' '.join(l.strip() for l in raw.splitlines()[1:])
                break
    # Normalização para apenas duas categorias
    categoria_lower = categoria.lower()
    texto_lower = (text or '').lower()
    ambig_palavras = [
        'olá', 'tudo bem', 'bom dia', 'boa tarde', 'boa noite', 'oi', 'saudações', 'cumprimentos', 'como vai', 'espero que esteja bem', 'espero que estejam bem'
    ]
    # Priorizar improdutivo para evitar erro de substring
    if any(word in categoria_lower for word in ['improdutivo', 'felicita', 'obrigado', 'agradecimento', 'paraben', 'parabéns', 'sem ação', 'irrelevante', 'informativo', 'spam']):
        categoria_final = 'Improdutivo'
    elif any(word in categoria_lower for word in ['produtivo', 'suporte', 'ação', 'atualização', 'dúvida', 'tecnico', 'técnico', 'problema', 'reclamação', 'pedido', 'solicitação', 'urgente', 'resposta']):
        categoria_final = 'Produtivo'
    elif any(word in texto_lower for word in ambig_palavras):
        categoria_final = 'Improdutivo'
    else:
        # fallback: se não identificar, assume produtivo se houver perguntas ou solicitações
        if '?' in raw or 'por favor' in raw.lower() or 'poderia' in raw.lower() or 'solicito' in raw.lower():
            categoria_final = 'Produtivo'
        else:
            categoria_final = 'Improdutivo'
    resposta = clean_placeholders(resposta, support_phone, support_email)
    return categoria_final, resposta
