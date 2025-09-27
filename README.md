# AutoU Email Classifier

**Autor:** Leandro da Silva Stampini

## Descrição

Aplicação web para classificar emails como produtivos ou improdutivos e sugerir respostas automáticas, utilizando IA (Google Gemini), NLP local, extração de texto de PDF (incluindo OCR para PDFs-imagem), persistência em banco de dados e interface moderna.

---

## Tecnologias Utilizadas
- Python 3.11+
- Flask
- SQLAlchemy
- Bootstrap (frontend)
- pdfplumber (extração de texto de PDF)
- NLTK (stopwords, stemming, NLP)
- pytesseract + Tesseract OCR (extração de texto de PDFs-imagem)
- Google Generative AI (Gemini)
- HTML/CSS/JS

---

## Instalação e Execução

### 1. Clone o repositório
```bash
git clone <url-do-repo>
cd autou-email-classifier
```

### 2. Instale as dependências Python
```bash
pip install -r requirements.txt
```

### 3. Instale o Tesseract OCR (para PDFs-imagem)
- Baixe em: https://github.com/tesseract-ocr/tesseract/wiki
- Instale normalmente (Windows: tesseract-ocr-w64-setup-...)
- Adicione o caminho do executável ao PATH (ex: `C:\Program Files\Tesseract-OCR`)
- Certifique-se de que o idioma português está instalado (`por.traineddata` em `tessdata`)

### 4. Execute a aplicação
```bash
python app/main.py
```
Acesse em [http://localhost:5000](http://localhost:5000)

---

## Exemplos de Uso

- **Cole o texto do email** ou **faça upload de um arquivo** `.txt` ou `.pdf` (pesquisável ou imagem).
- Clique em "Classificar" para obter a categoria e sugestão de resposta.
- Use o botão "Limpar" para resetar o formulário.

### Tipos de Arquivos Aceitos
- `.txt` (texto simples)
- `.pdf` (texto pesquisável ou imagem escaneada)

### Pasta de Testes
- Veja a pasta `teste/` com exemplos de arquivos `.txt` e `.pdf` para validação.

---

## Imagens da Interface e Ferramentas

### Tela Principal
![Tela principal](docs/tela_principal.png)

### Exemplo de Classificação
![Exemplo classificação](docs/exemplo_classificacao.png)

### Exemplo de PDF sendo lido
![PDF lido](docs/exemplo_pdf.png)

> Substitua as imagens acima por capturas reais do seu ambiente, salve em `docs/` e ajuste os nomes se necessário.

---

## Observações e Dicas
- O sistema lê PDFs com texto e PDFs-imagem (OCR).
- Se o texto extraído for irrelevante ou o documento não for um email, a categoria será "Indefinido".
- Para melhor resultado em OCR, use PDFs com boa resolução.
- O backend exibe no terminal o texto extraído para depuração.
- A chave da API Gemini deve ser válida e estar configurada no código.

---

## Autor
Leandro da Silva Stampini

---

## Licença
MIT

---

## Contato
leandro_stampini@yahoo.com.br

---

## Créditos
- Projeto desenvolvido como desafio prático de classificação de emails com IA e NLP.
- Ferramentas open source e APIs Google Gemini.

---

## Histórico
- Suporte a PDF pesquisável e imagem (OCR)
- NLP local (stopwords, stemming)
- Interface moderna e responsiva
- Exemplos de teste incluídos

---

## Como contribuir
Pull requests são bem-vindos!
