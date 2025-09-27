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
import google.generativeai as genai
GEMINI_API_KEY = "AIzaSyDxT-OSlacY24S9lzW8MO9KUHbYCG8anfI"
genai.configure(api_key=GEMINI_API_KEY)

# Listar modelos disponíveis ao iniciar
if __name__ == "__main__":
    print("Modelos disponíveis na API Gemini para sua chave:")
    try:
        models = genai.list_models()
        for m in models:
            print(f"- {m.name} | {m.supported_generation_methods}")
    except Exception as e:
        print("Erro ao listar modelos:", e)

# Troque o nome do modelo abaixo conforme o disponível na sua conta
gemini_model = genai.GenerativeModel('models/gemini-pro-latest')

def extract_text(file_storage):
    filename = file_storage.filename.lower()
    if filename.endswith('.txt'):
        return file_storage.read().decode('utf-8', errors='ignore')
    elif filename.endswith('.pdf'):
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            text = None
            try:
                file_storage.save(tmp.name)
                tmp.close()  # Fecha o arquivo antes de abrir com pdfplumber
                text = ""
                try:
                    with pdfplumber.open(tmp.name) as pdf:
                        text = "\n".join(page.extract_text() or '' for page in pdf.pages)
                except Exception as e:
                    print(f"Erro ao extrair texto do PDF: {e}")
                    text = ""
                # Se texto extraído estiver vazio, tenta OCR
                if not text or not text.strip():
                    print("[OCR] Tentando OCR nas páginas do PDF...")
                    try:
                        with pdfplumber.open(tmp.name) as pdf:
                            ocr_text = []
                            for i, page in enumerate(pdf.pages):
                                print(f"[OCR] Processando página {i+1}...")
                                try:
                                    img = page.to_image(resolution=300).original
                                    ocr_result = pytesseract.image_to_string(img, lang='por')
                                    print(f"[OCR] Texto extraído da página {i+1}: {repr(ocr_result[:200])}")
                                    ocr_text.append(ocr_result)
                                except Exception as e:
                                    print(f"[OCR] Erro ao processar página {i+1}: {e}")
                            text = "\n".join(ocr_text)
                    except Exception as e:
                        print(f"[OCR] Erro ao tentar OCR: {e}")
                        text = ""
                if not text or not text.strip():
                    return None  # Indica que não foi possível extrair texto
                return text
            finally:
                try:
                    os.unlink(tmp.name)
                except Exception as e:
                    print(f"Erro ao remover arquivo temporário: {e}")
    return ''

    # Não faz mais pré-processamento, apenas retorna o texto original
    return text

def classify_email(text):
    # Prompt para Gemini: pede classificação e resposta automática
    prompt = f"""
Classifique o email abaixo como 'Produtivo' ou 'Improdutivo' e sugira uma resposta automática adequada.

Email:
{text}

Retorne no formato:
Categoria: [Produtivo/Improdutivo]
Resposta: [resposta sugerida]
"""
    response = gemini_model.generate_content(prompt)
    output = response.text
    # Extrair categoria e resposta do output
    categoria = ""
    resposta = ""
    for line in output.splitlines():
        if line.lower().startswith("categoria:"):
            categoria = line.split(":",1)[1].strip()
        if line.lower().startswith("resposta:"):
            resposta = line.split(":",1)[1].strip()
    if not categoria:
        categoria = "Indefinido"
    if not resposta:
        resposta = "Não foi possível gerar uma resposta automática."
    return categoria, resposta

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    text = request.form.get('emailText', '').strip()
    file = request.files.get('emailFile')
    if file and file.filename:
        text = extract_text(file)
        print("Texto extraído do PDF:", repr(text))
        if text is None:
            return jsonify({'categoria': 'Erro', 'resposta': 'Não foi possível extrair texto do PDF. Envie um arquivo PDF pesquisável (não imagem).'}), 400
    if not text:
        return jsonify({'categoria': 'Erro', 'resposta': 'Nenhum texto fornecido.'})
    # Pré-processamento NLP: stopwords e stemming
    preprocessed = preprocess_text(text)
    # Limitar tamanho do texto enviado para a IA (ex: 2000 caracteres)
    preprocessed = preprocessed[:2000]
    categoria, resposta = classify_email(preprocessed)
    # Salvar no banco de dados
    email = Email(conteudo=text, categoria=categoria, resposta=resposta)
    db.session.add(email)
    db.session.commit()
    return jsonify({'categoria': categoria, 'resposta': resposta})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
