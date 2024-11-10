from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, session
from typing import Tuple, Any
from . import db
from .models import Users, Post
from .schemas import UserCreateSchema, PostCreateSchema

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/')
def index():
    user_id = session.get('user_id')
    if user_id:
        user = Users.query.get(user_id)  # Obtén los detalles del usuario desde la base de datos
        posts = Post.query.filter_by(user_id=user_id).all()  # Recuperar todos los posts del usuario logueado
        return render_template('index.html', user=user, posts=posts)  # Pasa el usuario y los posts al template
    else:
        return redirect(url_for('user_bp.login'))

@user_bp.route('/users/new')
def new_user_form() -> str:
    return render_template('register.html')

@user_bp.route('/users', methods=['POST'])
def create_user() -> str:
    data = request.form
    try:
        validated_user = UserCreateSchema(
            user_name=data['user_name'],
            password=data['password'],
            email=data['email'],
            image_url=str(data.get('image_url', ''))
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    new_user = Users(
        user_name=validated_user.user_name,
        password=validated_user.password,
        email=validated_user.email,
        image_url=validated_user.image_url
    )
    
    db.session.add(new_user)
    db.session.commit()

    return render_template('my_profile.html', user=new_user)

@user_bp.route('/users/<int:user_id>/edit')
def edit_user_form(user_id: int) -> str:
    user = Users.query.get_or_404(user_id)
    return render_template('my_profile.html', user=user)

@user_bp.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id: int) -> str:
    if request.form.get('_method') == 'DELETE':
        user = Users.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('user_bp.index'))
    return redirect(url_for('user_bp.profile'))

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user_name = request.form['user_name']
            user = Users.query.filter_by(user_name=user_name).first()
            
            if user and user.password == request.form['password']:
                session['user_id'] = user.id
                return redirect(url_for('user_bp.profile'))
            else:
                return "Invalid credentials", 401
        except KeyError:
            return "Missing field in the form", 400

    return render_template('login.html')

@user_bp.route('/profile', methods=['POST', 'GET'])
def profile() -> str:
    if 'user_id' not in session:
        return redirect(url_for('user_bp.login'))  # Si no está logueado, redirigir al login

    user_id = session.get('user_id')
    user = Users.query.get(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()  # Recuperar todos los posts del usuario logueado

    return render_template('my_profile.html', user=user, posts=posts)



@user_bp.route('/create_post', methods=['POST'])
def create_post():
    title = request.form['title']
    content = request.form['content']
    user_id = session.get('user_id')
    try:
        post_data = PostCreateSchema(title=title, content=content)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if user_id:
        post = Post(title=post_data.title, content=post_data.content, user_id=user_id)
        db.session.add(post)
        db.session.commit()
    return redirect(url_for('user_bp.profile'))

@user_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('user_bp.login'))

@user_bp.before_request
def handle_method_override():
    if request.method == 'POST' and '_method' in request.form:
        request.environ['REQUEST_METHOD'] = request.form['_method'].upper()
