import pytesseract
from PIL import Image
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt/portuguese.pickle')
except LookupError:
    nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
# Baixar recursos do NLTK se necessário
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
def preprocess_text(text):
    # Minúsculas, remoção de stopwords, stemming
    stop_words = set(stopwords.words('portuguese')) | set(stopwords.words('english'))
    stemmer = SnowballStemmer('portuguese')
    from nltk.tokenize import TreebankWordTokenizer
    tokenizer = TreebankWordTokenizer()
    tokens = tokenizer.tokenize(text.lower())
    filtered = [stemmer.stem(w) for w in tokens if w.isalpha() and w not in stop_words]
    return ' '.join(filtered)

# ...existing code...
# ...existing code...
# ...existing code...
from flask import Flask, render_template, request, jsonify
import os
import tempfile
import pdfplumber
## import nltk
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import hashlib



# Caminho absoluto para a pasta templates
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'
app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(BASE_DIR / 'emails.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Email
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(20), nullable=False)
    resposta = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)


# Integração Gemini (Google Generative AI)
import openai
import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
SUPPORT_PHONE = os.getenv("SUPPORT_PHONE")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL")

def extract_text(file_storage):
    # Garantir que o ponteiro do arquivo está no início (quando enviado pelo browser)
    try:
        if hasattr(file_storage, 'stream'):
            file_storage.stream.seek(0)
    except Exception:
        pass
    filename = file_storage.filename.lower()
    if filename.endswith('.txt'):
        # Ler texto em bytes e decodificar, garantindo que o ponteiro esteja no início
        try:
            data = file_storage.read()
            # Se veio como string (alguns testes), normalize
            if isinstance(data, str):
                return data
            return data.decode('utf-8', errors='ignore')
        finally:
            try:
                if hasattr(file_storage, 'stream'):
                    file_storage.stream.seek(0)
            except Exception:
                pass

    elif filename.endswith('.pdf'):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        text = None
        try:
            # garantir ponteiro no início antes de salvar
            try:
                if hasattr(file_storage, 'stream'):
                    file_storage.stream.seek(0)
            except Exception:
                pass
            file_storage.save(tmp.name)
            tmp.close()  # Fecha o arquivo antes de abrir com pdfplumber
            try:
                import pdfplumber
                ocr_text = []
                with pdfplumber.open(tmp.name) as pdf:
                    for i, page in enumerate(pdf.pages):
                        try:
                            page_text = page.extract_text()
                            if not page_text or not page_text.strip():
                                # Fallback para OCR
                                from PIL import Image
                                import pytesseract
                                img = page.to_image(resolution=300).original
                                page_text = pytesseract.image_to_string(img, lang='por')
                            ocr_text.append(page_text.strip())
                        except Exception as e:
                            print(f"[OCR] Erro ao processar página {i+1}: {e}")
                text = "\n".join(ocr_text)
            except Exception as e:
                print(f"[OCR] Erro ao tentar OCR: {e}")
            if not text or not text.strip():
                return None  # Indica que não foi possível extrair texto
            return text
        finally:
            try:
                os.unlink(tmp.name)
            except Exception as e:
                print(f"Erro ao remover arquivo temporário: {e}")
    return ''


def classify_email(text, request_id=None, input_hash=None):
    # Prompt reforçado para garantir respostas completas e úteis
    # Inclui os contatos de suporte configurados (se houver) e instrui explicitamente o modelo
    phone_info = SUPPORT_PHONE if SUPPORT_PHONE else 'não disponível'
    email_info = SUPPORT_EMAIL if SUPPORT_EMAIL else 'não disponível'
    # tag de requisição para forçar distinção entre chamadas (ajuda a evitar respostas repetidas por cache/contexto)
    req_tag = f"[REQUEST_ID: {request_id}]" if request_id else ""
    hash_tag = f"[INPUT_HASH: {input_hash}]" if input_hash else ""
    # Usar uma mensagem de sistema separada (rules) e enviar o conteúdo do e-mail como mensagem do usuário.
    system_rules = f"""
{req_tag} {hash_tag}
Você é um assistente de e-mails corporativos. Siga as regras abaixo para classificar e responder.

Regras críticas (faça exatamente isto):
1) Primeiro, IDENTIFIQUE O TIPO DE CONTEÚDO do e-mail verificando evidências literais no texto.
   - Se o texto contém palavras/trechos como 'currículo', 'resumo profissional', 'formação acadêmica', 'experiência profissional', 'LinkedIn', 'CV' ou listas extensas de experiências/habilidades, TRATE como CURRÍCULO/INSCRIÇÃO e responda com agradecimento e confirmação de recebimento (modelo de resposta para currículo).
   - Caso contrário, NÃO assuma que é um currículo. Não invente que é um candidato ou que recebeu um CV se não houver evidência clara.
2) NUNCA INVENTE nomes, cargos, datas ou detalhes que não estejam no e-mail original. Se o e-mail não contiver o nome do remetente, não inclua nomes específicos.
3) GERE UMA CLASSIFICAÇÃO entre: 'Produtivo' (requer ação/resposta) ou 'Improdutivo' (não requer ação). Baseie-se somente no texto do e-mail.
4) GERE UMA RESPOSTA adequada ao tipo detectado. A resposta deve: saudação, corpo com instruções ou próximos passos (se aplicável), e encerramento cordial. Pelo menos 3 frases.
5) NÃO use placeholders como '(inserir número)' ou '(inserir e-mail)'. Use os contatos configurados quando apropriado ou as expressões 'nosso suporte' / 'nosso e-mail de suporte'.
6) Seja conciso, profissional e específico.

Formate a saída EXATAMENTE assim (sem texto adicional):
Categoria: [Produtivo/Improdutivo]
Resposta: [resposta sugerida]
"""
    # A mensagem do usuário conterá apenas o e-mail original (sem regras) para evitar confusão de contexto.
    # Heurística rápida para detectar CVs e anotar o sistema (reduz chances de inventar que é um currículo)
    cv_keywords = ['currículo', 'resumo profissional', 'formação acadêmica', 'experiência profissional', 'linkedin', 'cv']
    is_cv = any(k in (text or '').lower() for k in cv_keywords)
    # Heurística para detectar pedidos de suporte/erro técnico
    support_keywords = ['dificuldade', 'dificuldades', 'acessar', 'instabilidade', 'erro', 'problema', 'não consigo', 'não consigo acessar', 'lentidão']
    is_support = any(k in (text or '').lower() for k in support_keywords)
    # Deterministic fallback: if content looks like a support/ticket request,
    # return a safe, rule-based response to avoid hallucinations by the model.
    if is_support:
        print(f"[INFO][REQ {request_id}] suporte detectado via heurística; usando fallback determinístico")
        # Build contact lines
        phone_line = f"Telefone: {SUPPORT_PHONE}." if SUPPORT_PHONE else ''
        email_line = f"E-mail: {SUPPORT_EMAIL}." if SUPPORT_EMAIL else ''
        contact_line = ' '.join(p for p in [phone_line, email_line] if p)
        if not contact_line:
            contact_line = 'Por favor, entre em contato com nosso suporte.'
        # Templated response (at least 3 sentences)
        resposta_fallback = (
            "Olá,\n\nRecebemos sua solicitação de suporte e nossa equipe já está analisando o problema. "
            "Para agilizar o atendimento, por favor envie prints, o horário aproximado em que ocorreu o erro e o nome do sistema/versão. "
            f"Entraremos em contato assim que tivermos uma atualização. {contact_line}"
        )
        return 'Produtivo', resposta_fallback
    if is_support:
        system_rules += "\n\n[AUTONOTE] Heurística identificou o conteúdo como PEDIDO DE SUPORTE/TICKET. Priorize ação e instruções passo a passo."
    if is_cv:
        system_rules += "\n\n[AUTONOTE] Heurística identificou o conteúdo como CURRÍCULO/INSCRIÇÃO. Trate-o como tal (agradeça e confirme recebimento)."
    else:
        system_rules += "\n\n[AUTONOTE] Heurística indica que o conteúdo NÃO é currículo. NÃO trate-o como tal."

    # Debug: mostrar preview do texto e das regras (não exibir chaves/segredos)
    try:
        print(f"[DEBUG][REQ {request_id}] is_cv={is_cv} preview={repr((text or '')[:300])}")
        print(f"[DEBUG][REQ {request_id}] system_rules_preview={repr(system_rules[:400])}")
    except Exception:
        pass
    # A mensagem do usuário conterá apenas o e-mail original (sem regras) para evitar confusão de contexto.
    def call_model(messages, max_tokens=700, temperature=0.1):
        try:
            completion = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"[OpenAI] Erro: {e}")
            return None

    # montar mensagens: system (rules) + user (email text)
    messages = [
        {"role": "system", "content": system_rules},
        {"role": "user", "content": text}
    ]
    # Debug: mostrar as mensagens que serão enviadas (sem exibir chaves)
    try:
        print(f"[DEBUG][REQ {request_id}] messages_sent=(system {len(system_rules)} chars, user {len(text or '')} chars)")
    except Exception:
        pass
    output = call_model(messages, max_tokens=700, temperature=0.1)
    # Mostrar saída bruta do modelo para diagnóstico
    try:
        print(f"[DEBUG][REQ {request_id}] raw_output_preview={repr((output or '')[:600])}")
    except Exception:
        pass
    if not output:
        output = "Categoria: Indefinido\nResposta: Não foi possível gerar uma resposta automática."

    def parse_output(output_text):
        categoria = ""
        resposta = ""
        lines = [l.rstrip() for l in output_text.splitlines()]
        # find category
        for i, line in enumerate(lines):
            if line.lower().startswith('categoria:'):
                categoria = line.split(':', 1)[1].strip().capitalize()
            if line.lower().startswith('resposta:'):
                part = line.split(':', 1)[1].strip()
                if part:
                    resposta = part
                    # append following lines
                    if i+1 < len(lines):
                        resposta = resposta + ' ' + ' '.join(l.strip() for l in lines[i+1:]).strip()
                else:
                    resposta = ' '.join(l.strip() for l in lines[i+1:]).strip()
                break
        return categoria, resposta

    categoria, resposta = parse_output(output)

    # Re-try logic: se a resposta for muito curta, peça expansão (até 2 tentativas)
    def is_short(resp: str):
        if not resp:
            return True
        # count sentences
        import re
        sentences = re.split(r'[\.!?]\s+', resp)
        num_sentences = sum(1 for s in sentences if s.strip())
        if num_sentences < 2 or len(resp.strip()) < 80:
            return True
        return False

    max_retries = 2
    tries = 0
    while is_short(resposta) and tries < max_retries:
        tries += 1
        expand_prompt = f"O texto de resposta abaixo está muito curto ou incompleto. Expanda a resposta para que seja cordial, específica ao email, com pelo menos 3 frases, incluindo saudação, corpo explicativo com próximos passos ou informações úteis, e encerramento cordial. Não inclua explicações sobre este passo.\n\nEmail original:\n{text}\n\nResposta atual:\n{resposta}\n\nForneça apenas o texto final da resposta (começando pela saudação)."
        # reforçar a instrução para não usar placeholders quando expandir
        expand_prompt = expand_prompt + "\n\nIMPORTANTE: não gere placeholders como '(inserir número)' ou '(inserir e-mail)'; use os contatos configurados quando disponíveis ou as expressões genéricas 'nosso suporte' / 'nosso e-mail de suporte'."
        new_output = call_model([
            {"role": "user", "content": expand_prompt}
        ], max_tokens=500, temperature=0.2)
        if not new_output:
            break
        # The model may return only the response (no 'Categoria:'). Keep categoria if present.
        # Try to parse; if parsing fails, assume categoria unchanged and use new_output as resposta
        new_cat, new_resp = parse_output(new_output)
        if new_resp:
            resposta = new_resp
        else:
            # If model returned raw reply (no label), take entire new_output
            resposta = new_output.strip()

    if not categoria:
        # tentar extrair 'categoria' em qualquer parte do texto
        import re
        m = re.search(r'categoria\s*:\s*(produtivo|improdutivo)', output, re.IGNORECASE)
        if m:
            categoria = m.group(1).capitalize()
    if not resposta:
        # tentativa final: tudo após 'resposta:'
        idx = output.lower().find('resposta:')
        if idx != -1:
            resposta = output[idx+len('resposta:'):].strip()

    if not categoria:
        categoria = 'Indefinido'
    if not resposta:
        resposta = 'Não foi possível gerar uma resposta automática.'

    # Pós-processamento: substituir ou remover placeholders como "(inserir número)" ou "(inserir e-mail)"
    def clean_placeholders(text):
        import re
        if not text:
            return text
        result = text
        # padrões comuns que modelos colocam como placeholders
        phone_patterns = [
            r"\(?inserir(?:\s|-)?(?:o\s)?(?:n[uú]mero|telefone|tel)\)?",
            r"\[inserir(?:\s|-)?(?:n[uú]mero|telefone)\]",
            r"<inserir(?:\s|-)?(?:n[uú]mero|telefone)>",
            r"\(insira(?:\s)?(?:o\s)?(?:n[uú]mero|telefone)\)",
        ]
        email_patterns = [
            r"\(?inserir(?:\s|-)?e-?mail\)?",
            r"\[inserir(?:\s|-)?e-?mail\]",
            r"<inserir(?:\s|-)?e-?mail>",
            r"\(insira(?:\s)?(?:o\s)?e-?mail\)",
        ]
        for p in phone_patterns:
            if SUPPORT_PHONE:
                result = re.sub(p, SUPPORT_PHONE, result, flags=re.IGNORECASE)
            else:
                # substitui por uma referência genérica ao suporte
                result = re.sub(p, 'nosso suporte', result, flags=re.IGNORECASE)
        for p in email_patterns:
            if SUPPORT_EMAIL:
                result = re.sub(p, SUPPORT_EMAIL, result, flags=re.IGNORECASE)
            else:
                result = re.sub(p, 'nosso e-mail de suporte', result, flags=re.IGNORECASE)

        # Remover quaisquer placeholders remanescentes entre parênteses/colchetes
        result = re.sub(r'\(.*?inserir.*?\)', '', result, flags=re.IGNORECASE)
        result = re.sub(r'\[.*?inserir.*?\]', '', result, flags=re.IGNORECASE)
        # Normalizar espaços
        result = re.sub(r'\s{2,}', ' ', result).strip()
        return result

    resposta = clean_placeholders(resposta)

    return categoria, resposta

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    # Recebe texto do campo e/ou arquivo. Vamos extrair ambos e decidir qual utilizar.
    form_text = (request.form.get('emailText', '') or '').strip()
    file = request.files.get('emailFile')
    file_text = None
    if file and file.filename:
        try:
            file_text = extract_text(file)
        except Exception as e:
            print(f"[ERROR] Falha ao extrair arquivo {getattr(file, 'filename', '')}: {e}")
            return jsonify({'categoria': 'Erro', 'resposta': 'Erro ao processar o arquivo enviado.'}), 400
        print(f"[DEBUG] Fonte: arquivo enviado ({file.filename})")
        print("[DEBUG] Texto extraído do arquivo:", repr(file_text))

    # Se o usuário enviou os dois (texto + arquivo) precisamos evitar ambiguidade.
    # Permitimos um override explícito com o campo form 'forceSource' (valores: 'file' ou 'form').
    force_source = (request.form.get('forceSource') or request.args.get('forceSource') or '').strip().lower()

    # Se ambos preenchidos e nenhum override, retornar aviso de ambiguidade para o cliente escolher.
    if form_text and file_text and file_text.strip() and not force_source:
        return jsonify({
            'ambiguous': True,
            'message': 'Escolha o método para seguir com a classificação: texto ou upload.',
            'choices': ['form', 'file'],
            'choices_display': ['texto', 'upload'],
            'hint': "Reenvie o formulário com o campo oculto 'forceSource' definido como 'form' (texto) ou 'file' (upload).",
            'form_preview': form_text[:300],
            'file_preview': (file_text or '')[:300]
        }), 400

    # Decisão de preferência quando ambos forem fornecidos ou quando um override foi fornecido
    source = 'form'
    raw_text = form_text
    if force_source == 'file':
        if not file_text or not isinstance(file_text, str) or not file_text.strip():
            return jsonify({'categoria': 'Erro', 'resposta': 'forceSource=file solicitado, mas o arquivo não contém texto extraível.'}), 400
        source = 'file'
        raw_text = file_text.strip()
    elif force_source == 'form':
        if not form_text:
            return jsonify({'categoria': 'Erro', 'resposta': 'forceSource=form solicitado, mas o campo de texto está vazio.'}), 400
        source = 'form'
        raw_text = form_text
    else:
        # sem override: aplicar heurística automática
        if file_text and isinstance(file_text, str) and file_text.strip():
            if not form_text:
                source = 'file'
                raw_text = file_text.strip()
            else:
                # se forem significativamente diferentes, priorizar o arquivo
                if file_text.strip() != form_text.strip() and len(file_text.strip()) > 20:
                    source = 'file'
                    raw_text = file_text.strip()
                else:
                    source = 'form'
                    raw_text = form_text

    raw_text = (raw_text or '').strip()
    if not raw_text:
        return jsonify({'categoria': 'Erro', 'resposta': 'Nenhum texto fornecido.'})

    print(f"[INFO] Input source: {source}; length: {len(raw_text)} characters")

    # NÃO enviar a versão stemmed/preprocessed para a IA — enviar o texto original, possivelmente truncado para caber no prompt
    ai_input = raw_text if len(raw_text) <= 4000 else raw_text[:4000]
    # gerar identificador e hash por requisição
    req_id = uuid.uuid4().hex
    input_hash = hashlib.sha256(ai_input.encode('utf-8')).hexdigest()
    print(f"[REQ] id={req_id} hash={input_hash[:12]}.. source={source} len={len(ai_input)}")
    categoria, resposta = classify_email(ai_input, request_id=req_id, input_hash=input_hash)

    # Salvar no banco de dados: armazenar o conteúdo original completo, não o truncado
    email = Email(conteudo=raw_text, categoria=categoria, resposta=resposta)
    db.session.add(email)
    db.session.commit()
    return jsonify({'categoria': categoria, 'resposta': resposta, 'source': source})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
