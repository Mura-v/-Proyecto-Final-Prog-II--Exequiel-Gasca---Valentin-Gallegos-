from . import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)

    # Relación con Post, usando 'author' como nombre de la relación inversa
    posts = db.relationship('Post', backref='author', lazy=True, cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self) -> str:
        return f"<User {self.user_name}>"
    
    def check_password(self, password):
        return self.password == password
    
class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)  # Columna para la URL de la imagen

    # No es necesario definir la relación aquí, porque ya está en el modelo Users
    # La relación inversa está definida como 'author' en Users

    def __repr__(self):
        return f'<Posts {self.title}>'