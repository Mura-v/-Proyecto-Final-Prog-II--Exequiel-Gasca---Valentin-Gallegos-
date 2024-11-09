from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

db: SQLAlchemy = SQLAlchemy()
migrate : Migrate = Migrate()

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(obj=Config)

    db.init_app(app=app)

    from .routes import user_bp
    app.register_blueprint(blueprint=user_bp)

    return app