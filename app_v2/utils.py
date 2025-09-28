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
        # Prefer the new OpenAI client (openai>=1.0). Use it if available.
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            # resp.choices[0].message.content is the same shape as before
            return resp.choices[0].message.content
        except Exception:
            # Fallback to older openai library interface if present
            resp = openai.ChatCompletion.create(
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

    # Tentar interpretar saída JSON
    raw = out.strip()
    # Log curto para debugging (não imprime a chave)
    print('[app_v2] saída bruta do modelo:', raw[:1000])
    try:
        parsed = json.loads(raw)
        categoria = parsed.get('categoria') or parsed.get('category') or 'Indefinido'
        resposta = parsed.get('resposta') or parsed.get('response') or ''
        resposta = clean_placeholders(resposta, support_phone, support_email)
        return categoria.capitalize() if isinstance(categoria, str) else 'Indefinido', resposta
    except Exception:
        # Fallback: parsing por heurística (compatibilidade com formato antigo)
        cat = 'Indefinido'
        resp = raw
        for line in raw.splitlines():
            if line.lower().startswith('categoria:'):
                cat = line.split(':', 1)[1].strip().capitalize()
            if line.lower().startswith('resposta:'):
                resp = line.split(':', 1)[1].strip() + ' ' + ' '.join(l.strip() for l in raw.splitlines()[1:])
                break
        resp = clean_placeholders(resp, support_phone, support_email)
        return cat, resp
