from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, session, current_app
from typing import Tuple, Any
import os
from . import db
from .models import Users, Post
from .schemas import UserCreateSchema, PostCreateSchema

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/')
def index():
    user_id = session.get('user_id')
    if user_id:
        user = Users.query.get(user_id)  
        posts = Post.query.filter_by(user_id=user_id).all()
        return render_template('index.html', user=user, posts=posts)
    else:
        return redirect(url_for('user_bp.login'))
    
@user_bp.route('/contact')
def contact():
    user_id = session.get('user_id')
    if user_id:
        user = Users.query.get(user_id)
        return render_template('contact.html', user=user)
    else:
        return render_template('contact.html')
    
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

@user_bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Users.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('user_bp.profile'))
        else:
            return render_template('login.html', error="Credenciales incorrectas")

    return render_template('login.html')

@user_bp.route('/profile', methods=['POST', 'GET'])
def profile():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('user_bp.login'))

    user = Users.query.get(user_id)

    if not user:
        return redirect(url_for('user_bp.login'))

    posts = Post.query.filter_by(user_id=user.id).all()

    return render_template('my_profile.html', user=user, posts=posts)


@user_bp.route('/create_post', methods=['POST'])
def create_post():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('user_bp.login'))

    
    title = request.form.get('title')
    content = request.form.get('content')
    post_image = request.files.get('postImage')

    if not title or not content:
        flash('El título y el contenido son obligatorios', 'error')
        return redirect(url_for('user_bp.profile'))

    
    image_url = None
    if post_image:
        
        filename = post_image.filename
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')

        
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file_path = os.path.join(upload_folder, filename)
        
        
        post_image.save(file_path)
        
        
        image_url = f'uploads/{filename}'

    
    post = Post(title=title, content=content, user_id=user_id, image_url=image_url)
    db.session.add(post)
    db.session.commit()

    
    flash('Publicación creada exitosamente', 'success')
    return redirect(url_for('user_bp.profile'))

@user_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id: int):
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_bp.login'))

    
    post = Post.query.get_or_404(post_id)

    
    if post.user_id != user_id:
        flash('No tienes permiso para eliminar esta publicación.', 'error')
        return redirect(url_for('user_bp.profile'))

    
    db.session.delete(post)
    db.session.commit()

    flash('Publicación eliminada correctamente', 'success')
    return redirect(url_for('user_bp.profile'))

@user_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('user_bp.login'))

@user_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    print(f"Buscando: {query}")
    if query:
        posts = Post.query.filter(Post.title.ilike(f'%{query}%')).all()
    else:
        posts = Post.query.all()

    return render_template('index.html', posts=posts, query=query)

@user_bp.before_request
def handle_method_override():
    if request.method == 'POST' and '_method' in request.form:
        request.environ['REQUEST_METHOD'] = request.form['_method'].upper()
