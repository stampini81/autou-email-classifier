
# Classificador de E-mails com IA para AutoU

![CI](https://github.com/<SEU_USUARIO>/<SEU_REPOSITORIO>/actions/workflows/ci.yml/badge.svg)

Este projeto é a minha submissão para o case prático do processo seletivo da AutoU. A aplicação web utiliza Inteligência Artificial para classificar e-mails como "Produtivo" ou "Improdutivo" e sugerir uma resposta automática, otimizando o fluxo de trabalho de equipes que lidam com um grande volume de mensagens.

---

## 🚀 Acesso Rápido

* **Aplicação Online:** **[LINK DA SUA APLICAÇÃO HOSPEDADA AQUI]**
* **Vídeo Demonstrativo:** **[LINK DO SEU VÍDEO NO YOUTUBE AQUI]**

---

## ✨ Funcionalidades Principais

* **Classificação com IA:** Utiliza o modelo `gpt-3.5-turbo` da OpenAI para analisar o conteúdo do e-mail e determinar sua categoria e uma resposta adequada.
* **Suporte a Múltiplos Formatos:** Aceita entrada de texto direto, upload de arquivos `.txt` e `.pdf`.
* **OCR Integrado:** Processa PDFs baseados em imagem (escaneados) utilizando Tesseract OCR para extração de texto.
* **Interface Intuitiva:** Frontend simples para facilitar o upload e a visualização dos resultados.
* **Mecanismo de Ambiguidade:** Caso o usuário envie texto e um arquivo simultaneamente, um modal é exibido para que ele escolha a fonte de dados a ser processada.
* **Persistência de Dados:** Salva o histórico de classificações em um banco de dados SQLite local.

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3.11, Flask, SQLAlchemy
* **Inteligência Artificial:** OpenAI API
* **Processamento de Arquivos:** pdfplumber (para PDFs de texto), pytesseract (para OCR)
* **Testes:** Pytest
* **Containerização:** Docker
* **CI/CD:** GitHub Actions

---

## ⚙️ Configuração e Execução Local

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos

* Python 3.10+
* Git
* [Tesseract OCR](https://github.com/tesseract-ocr/tessdoc) (necessário para processar PDFs de imagem. Se preferir, pule esta instalação e use o Docker).
* Uma chave de API válida da OpenAI.

### 1. Instalação

Clone o repositório e instale as dependências Python em um ambiente virtual.

```bash
# Clone o repositório
git clone [https://github.com/](https://github.com/)<SEU_USUARIO>/<SEU_REPOSITORIO>.git
cd <NOME_DO_DIRETORIO>

# Crie e ative o ambiente virtual
python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Baixe os pacotes necessários do NLTK
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
````

### 2\. Configuração do Ambiente

Crie um arquivo chamado `.env` na raiz do projeto e adicione suas variáveis de ambiente.

```env
# .env
OPENAI_API_KEY="sk-sua-chave-aqui"
SUPPORT_PHONE="+55 (11) 4000-0000"
SUPPORT_EMAIL="suporte@autou.com.br"
```

**Importante:** O arquivo `.env` está no `.gitignore` e nunca deve ser versionado.

### 3\. Execução

Com o ambiente virtual ativado, inicie a aplicação Flask:

```bash
python app/main.py
```

A aplicação estará disponível em **[http://127.0.0.1:5000](http://127.0.0.1:5000)**.

-----

## 🐳 Executando com Docker

Se você não quiser instalar o Tesseract e as dependências localmente, pode usar o Docker. O `Dockerfile` já cuida de toda a configuração.

```bash
# 1. Construa a imagem Docker
docker build -t autou-email-classifier .

# 2. Execute o container, passando o arquivo .env
docker run -p 5000:5000 --env-file .env autou-email-classifier
```

A aplicação estará disponível em **[http://localhost:5000](https://www.google.com/search?q=http://localhost:5000)**.

-----

## 🧪 Testes Automatizados

O projeto conta com uma suíte de testes automatizados para garantir a qualidade do código e das funcionalidades principais. Para executá-los:

```bash
python -m pytest -q
```

## 🔄 CI/CD

O repositório está configurado com um workflow de Integração Contínua usando **GitHub Actions** (`.github/workflows/ci.yml`). A cada `push` ou `pull request`, o workflow realiza as seguintes ações:

1.  Configura o ambiente Python.
2.  Instala as dependências do projeto.
3.  Instala o Tesseract OCR.
4.  Executa a suíte de testes com `pytest`.

## 👤 Contato

**Leandro da Silva Stampini**

  * **LinkedIn:** [https://www.linkedin.com/in/leandro-da-silva-stampini-07b04aa3]
  * **GitHub:** [https://github.com/stampini81]



