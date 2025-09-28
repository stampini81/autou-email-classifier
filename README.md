# Integração com OpenAI GPT

Agora o projeto utiliza o GPT (OpenAI) para classificar e sugerir respostas automáticas aos emails.

## Como configurar a chave da OpenAI

1. Crie um arquivo `.env` na raiz do projeto (já criado automaticamente).
2. Cole sua chave da OpenAI no formato:
	```
	OPENAI_API_KEY=sk-xxxxxx
	```
3. **Nunca compartilhe sua chave em público ou em repositórios!**

## Dependências

O projeto já inclui `openai` e `python-dotenv` no requirements.txt. Se necessário, instale manualmente:
```
pip install openai python-dotenv
```

## Observações
- O modelo padrão é o `gpt-3.5-turbo`. Para usar o GPT-4, altere o parâmetro `model` no código.
- A chave é carregada automaticamente do `.env`.
- O uso da API pode gerar custos conforme o volume de requisições.
# AutoU — Email Classifier (README de entrega)

Este README frontal foi preparado para apoiar a submissão do Case Prático AutoU. Ele descreve como executar a aplicação localmente, o que o projeto entrega e como testar os requisitos do desafio.

IMPORTANTE: este arquivo é a versão final que será utilizada para avaliação; antes de submeter, revise e remova notas de desenvolvimento se necessário.

----

Sumário rápido
- URL (local): http://localhost:5000
- Endpoints principais: `/` (UI), `/classify` (POST)
- Formatos aceitos: `.txt`, `.pdf` (pesquisável e imagens via OCR)

Requisitos atendidos
- Interface Web para upload e inserção de texto
- Extração de texto (pdfplumber + pytesseract OCR)
- NLP básico (stopwords + stemming via NLTK)
- Classificação e geração de resposta via OpenAI GPT
- Persistência (SQLite via SQLAlchemy)
- Mecanismo de disambiguamento quando usuário envia texto + arquivo

----

Pré-requisitos (local)
- Python 3.11+ (ou 3.10 compatível)
- Tesseract OCR instalado e no PATH (para OCR em PDFs)
- Conta OpenAI com chave válida (opcional: para rodar com IA)
# AutoU — Email Classifier

Aplicação Flask para classificação de e-mails em "Produtivo" ou "Improdutivo" e sugestão de resposta automática. Aceita texto, `.txt` ou `.pdf` (com OCR via Tesseract). Persistência local em SQLite. Pronto para deploy via Docker e CI automatizado.

## Sumário
- [Pré-requisitos](#pré-requisitos)
- [Instalação local](#instalação-local)
- [Configuração do ambiente](#configuração-do-ambiente)
- [Execução local](#execução-local)
- [Validação na interface web](#validação-na-interface-web)
- [Testes automatizados](#testes-automatizados)
- [Execução via Docker](#execução-via-docker)
- [CI/CD](#cicd)
- [Checklist de submissão](#checklist-de-submissão)
- [Contato](#contato)

## Pré-requisitos
- Python 3.10+
- Git
- (Para OCR) Tesseract OCR instalado (ou use Docker)
- Conta OpenAI e chave de API

## Instalação local
```powershell
git clone <URL_DO_REPO>
cd autou-email-classifier
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -c "import nltk; nltk.download('stopwords')"
```

## Configuração do ambiente
Crie um arquivo `.env` na raiz:
```
OPENAI_API_KEY=sk-...
SUPPORT_PHONE=+55 (11) 4000-0000
SUPPORT_EMAIL=suporte@autou.com.br
```
Não comite `.env`.

## Execução local
```powershell
.\.venv\Scripts\Activate.ps1
python app/main.py
# Acesse http://127.0.0.1:5000
```

## Validação na interface web
1. Cole texto ou faça upload de `.txt`/`.pdf`.
2. Clique em "Classificar".
3. Veja categoria e resposta sugerida.
4. Se enviar texto + arquivo, escolha a fonte no modal.

## Testes automatizados
```powershell
python -m pytest -q
```

## Execução via Docker
```sh
docker build -t autou-email-classifier .
docker run -p 5000:5000 --env-file .env autou-email-classifier
# Acesse http://localhost:5000
```

## CI/CD
O repositório inclui workflow GitHub Actions (`.github/workflows/ci.yml`) que instala dependências, Tesseract e executa os testes.

## Checklist de submissão
- [ ] Repositório público (GitHub)
- [ ] Vídeo demonstrativo (3-5 min)
- [ ] Link da aplicação hospedada
- [ ] Apenas `README.md` como arquivo Markdown
- [ ] Sem segredos/versionamento de `.env` ou `emails.db`

## Contato
Leandro da Silva Stampini

```powershell
python app/main.py
```

3. Abra no navegador: http://127.0.0.1:5000

Observação: se preferir rodar via environment variable FLASK_APP/FLASK_ENV, ajuste conforme seu fluxo, mas `python app/main.py` inicia a aplicação diretamente.


7) Validando na interface web (passo a passo)
--------------------------------------------
Esses passos garantem que você execute as validações exigidas pelo Case.

a) Teste básico com texto colado

1. Abra a página principal
2. No campo de texto cole o conteúdo de um e-mail (ex: assunto + corpo)
3. Clique em "Classificar"
4. Aguarde o resultado — o painel mostrará a "Categoria" e a "Resposta sugerida"

Comportamento esperado: a API retorna JSON com `categoria` e `resposta`. A UI exibe estes campos.


b) Teste com upload de arquivo `.txt`

1. Na página principal, escolha o arquivo `.txt` (ex.: `samples/exemplo_produtivo.txt`)
2. Clique em "Classificar"
3. Verifique o texto extraído e o resultado na UI


c) Teste com upload de PDF pesquisável

1. Faça upload de um PDF que contenha texto pesquisável
2. A aplicação usará `pdfplumber` para extrair o texto
3. Confira o texto e a classificação no painel de resultados


d) Teste com PDF escaneado / imagem (OCR)

1. Faça upload de um PDF composto por imagens (scan)
2. A aplicação fará fallback para `pytesseract` e tentará extrair o texto via OCR
3. Valide o texto extraído na UI e a classificação


e) Cenário de ambiguidade (texto + arquivo enviados juntos)

1. Preencha o campo de texto E carregue um arquivo ao mesmo tempo
2. O backend retornará `ambiguous: true` com "previews"
3. A UI mostrará um modal com o preview do texto e do arquivo permitindo escolher qual fonte usar
4. Ao escolher, a UI reenvia a requisição com `forceSource=file` ou `forceSource=form`

Nota: isso evita que o sistema tente fundir duas fontes diferentes sem confirmação do usuário.


8) Testes automatizados
------------------------
Os testes usam `pytest`.

Para executar os testes:

```powershell
python -m pytest -q
```

O conjunto de testes cobre casos básicos de extração de `.txt`, comportamento de fallback para tickets de suporte e o endpoint de ambiguidade.


9) Deploy (opcional)
---------------------
Recomendações rápidas:

- Para replicabilidade, criar um `Dockerfile` que instale o Tesseract e as dependências Python. Posso gerar esse `Dockerfile` para você.
- Plataformas: Render, Heroku (buildpacks para Tesseract), Replit, ou hospedar numa VM que tenha Tesseract instalado.


10) Segurança e checklist de submissão
-------------------------------------
- Verifique se não existem segredos no repositório (arquivo `.env`, `emails.db`). Se você comitou algum segredo, rotacione as chaves.
- Itens para copiar no formulário de submissão:
	- Link público do repositório (GitHub)
	- Link do vídeo demonstrativo (3-5 minutos)
	- Link da aplicação hospedada (URL pública) — se houver


11) Contato
-----------
Leandro da Silva Stampini

Notas técnicas e próximos passos
- O repositório já inclui um `Dockerfile` que instala Tesseract e as dependências Python.
- Um workflow GitHub Actions (`.github/workflows/ci.yml`) foi adicionado para executar `pytest` em pushes/PRs.
- Recomenda-se verificar e rotacionar a chave OpenAI caso tenha sido comitada anteriormente.

