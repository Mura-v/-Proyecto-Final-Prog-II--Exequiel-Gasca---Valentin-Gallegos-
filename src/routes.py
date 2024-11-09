from flask import Blueprint, render_template,redirect, url_for, request, jsonify
from typing import List,Tuple, Any
from . import db
from .models import Users
from .schemas import UserCreateSchema

user_bp = Blueprint('user_bp', __name__)

@user_bp.route("/")
def index() -> str:
    users: List[Tuple[Any]] = Users.query.all()
    
    return render_template('index.html', users=users)

@user_bp.route('/users/new')
def new_user_form() -> str:
    return render_template('register.html')

@user_bp.route('/users', methods=['POST'])
def create_user() -> str:
    data = Tuple[Any] = request.form
    try:
        UserCreateSchema(user_name=data['user_name'],
                                     password=data['password'],
                                     email=data['email'],
                                     image_url=data['image_url'])
    except ValueError as e:
        return jsonify({"error": e}), 400
    
    new_user: Users =  Users(user_name=data['user_name'],
                                     password=data['password'],
                                     email=data['email'],
                                     image_url=data['image_url'])
    
    db.session.add(new_user)
    db.session.commit

    return render_template('register.html', user = new_user)