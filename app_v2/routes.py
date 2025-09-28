from flask import render_template, request, jsonify
from app_v2.utils import extract_text, classify_email
from app_v2.models import Email
from app_v2 import db


def init_routes(app):
    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/classify', methods=['POST'])
    def classify():
        form_text = (request.form.get('emailText', '') or '').strip()
        file = request.files.get('emailFile')
        file_text = extract_text(file) if file and file.filename else None

        if form_text and file_text and file_text.strip():
            # default to form unless forceSource specified
            force_source = (request.form.get('forceSource') or request.args.get('forceSource') or '').strip().lower()
            if not force_source:
                # fornecer pré-visualizações para o frontend (truncadas)
                def preview(s, n=800):
                    if not s:
                        return ''
                    s2 = ' '.join(str(s).splitlines())
                    return (s2[:n] + '...') if len(s2) > n else s2

                return jsonify({
                    'ambiguous': True,
                    'message': 'Escolha entre texto ou upload para classificação.',
                    'form_preview': preview(form_text),
                    'file_preview': preview(file_text)
                })
            if force_source == 'file':
                selected = file_text
            else:
                selected = form_text
        else:
            selected = file_text if (file_text and (not form_text)) else form_text

        if not selected or not selected.strip():
            return jsonify({'categoria': 'Erro', 'resposta': 'Nenhum texto fornecido.'})

        categoria, resposta = classify_email(selected)

        email = Email(conteudo=selected, categoria=categoria, resposta=resposta)
        db.session.add(email)
        db.session.commit()

        return jsonify({'categoria': categoria, 'resposta': resposta})
