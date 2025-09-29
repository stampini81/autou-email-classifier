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


## ⚙️ Como Executar o Projeto

### Execução Local (SQLite)

1. **Pré-requisitos:**
    - Python 3.11+
    - Git
    - [Tesseract OCR](https://github.com/tesseract-ocr/tessdoc) (opcional se usar Docker)
    - Chave da OpenAI


2. **Instalação e Ambiente Virtual:**

    > **Recomendado:** Sempre use um ambiente virtual para isolar as dependências do projeto.

    ```powershell
    # Clone o repositório
    git clone https://github.com/<SEU_USUARIO>/<SEU_REPOSITORIO>.git
    cd <NOME_DO_DIRETORIO>

    # Crie o ambiente virtual
    python -m venv .venv

    # Ative o ambiente virtual (Windows)
    .\.venv\Scripts\Activate.ps1

    # Instale as dependências
    pip install -r requirements.txt

    # Baixe os pacotes necessários do NLTK
    python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
    ```

3. **Configuração:**
    - Copie `.env.example` para `.env` e preencha sua chave OpenAI e outras variáveis.

4. **Inicialize o banco (opcional, SQLite):**
    ```powershell
    python scripts/create_db.py
    ```

5. **Execute a aplicação:**
    ```powershell
    python run_v2.py
    # Acesse http://localhost:5001
    ```

### Execução com Docker Compose (PostgreSQL)

1. **Pré-requisitos:**
    - Docker e Docker Compose

2. **Configuração:**
    - Copie `.env.example` para `.env` e preencha sua chave OpenAI e outras variáveis.

3. **Suba os containers:**
    ```powershell
    docker-compose up --build
    # Acesse http://localhost:5001
    ```
    - O banco de dados será criado automaticamente.
    - O app usará PostgreSQL no container e SQLite localmente.

#### Portas
- A aplicação roda sempre na porta **5001** (local e Docker).
- O banco PostgreSQL roda na porta **5432** (apenas no Docker).

#### Variáveis de ambiente
- Use o arquivo `.env` para definir `OPENAI_API_KEY` e outras variáveis.
- O Docker Compose já carrega automaticamente o `.env`.


### Testes Automatizados

#### Rodar testes localmente
```powershell
python -m pytest app_v2/tests/
```

#### Rodar testes no container (Docker Compose)
```powershell
docker-compose run --rm app pytest app_v2/tests/
```
Substitua `app` pelo nome do serviço se for diferente no seu docker-compose.yml.

### CI/CD
O projeto utiliza GitHub Actions para rodar testes e análise de código a cada push/pull request.

---



## 👤 Contato

**Leandro da Silva Stampini**

  * **LinkedIn:** [https://www.linkedin.com/in/leandro-da-silva-stampini-07b04aa3]
  * **GitHub:** [https://github.com/stampini81]

---





