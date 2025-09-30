import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import openai
import logging

BASE_DIR = Path(__file__).resolve().parent.parent

db = SQLAlchemy()
logger = logging.getLogger(__name__)


def create_app():
    # carregar .env e configurar OpenAI uma única vez aqui
    load_dotenv()
    # Log para verificar se as variáveis do .env foram carregadas
    print("[DEBUG] Variáveis de ambiente carregadas:")
    print("OPENAI_API_KEY:", bool(os.getenv("OPENAI_API_KEY")))
    print("SUPPORT_PHONE:", os.getenv("SUPPORT_PHONE"))
    print("SUPPORT_EMAIL:", os.getenv("SUPPORT_EMAIL"))
    print("NOME_ASSINATURA:", os.getenv("NOME_ASSINATURA"))
    print("EMPRESA_ASSINATURA:", os.getenv("EMPRESA_ASSINATURA"))
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # debug: confirmar que a chave foi carregada (não imprimir o valor)
    key_loaded = bool(openai.api_key)
    if key_loaded:
        print('[app_v2] OPENAI_API_KEY carregada: True')
    else:
        print('[app_v2] AVISO: OPENAI_API_KEY não encontrada. Verifique .env ou variável de ambiente')


    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    db_uri = os.getenv("SQLALCHEMY_DATABASE_URI")
    if db_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR / 'emails.db'}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # logs de inicialização (sem expor chaves)
    try:
        key_loaded = bool(os.getenv('OPENAI_API_KEY'))
        logger.info(f"[app_v2] OPENAI_API_KEY carregada: {key_loaded}")
        logger.info(f"[app_v2] SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    except Exception:
        # evitar falha de inicialização por logs
        pass

    # registrar modelos e rotas
    from app_v2 import models, routes  # noqa: F401
    routes.init_routes(app)

    return app
