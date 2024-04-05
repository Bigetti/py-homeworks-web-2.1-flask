#app.py


from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///advertisements.db'
app.config['SECRET_KEY'] = 'abrakagabra'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

    

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('advertisements', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'creation_date': self.creation_date.isoformat(),
           }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
def hello():
    return '<h1>Добро пожаловать на главную страницу приложения!</h1>'

@app.route('/advertisements', methods=['GET'])
def show_all_advertisements():
    advertisements = Advertisement.query.all()
  #  return render_template('advertisements.html', advertisements=advertisements)
# Преобразуем объявления в список словарей, которые можно преобразовать в JSON
    advertisement_list = [advertisement.to_dict() for advertisement in advertisements]
    return jsonify(advertisement_list)

@app.route('/advertisement', methods=['POST'])
@login_required
def create_advertisement():
    data = request.json
    new_advertisement = Advertisement(title=data['title'], description=data['description'], owner_id=current_user.id)
    db.session.add(new_advertisement)
    db.session.commit()
    return jsonify({'message': 'New advertisement created!'}), 201

@app.route('/advertisement/<int:id>', methods=['GET'])
def get_advertisement(id):
    advertisement = Advertisement.query.get(id)
    if advertisement is None:
        return jsonify({'message': 'Advertisement not found'}), 404
    advertisement_data = {'id': advertisement.id, 'title': advertisement.title, 'description': advertisement.description, 'creation_date': advertisement.creation_date}
    return jsonify(advertisement_data)

@app.route('/advertisement/<int:id>', methods=['DELETE'])
@login_required
def delete_advertisement(id):
    advertisement = Advertisement.query.get(id)
    if advertisement is None:
        return jsonify({'message': 'Advertisement not found'}), 404
    if advertisement.owner_id != current_user.id:
        return jsonify({'message': 'You do not have permission to delete this advertisement'}), 403
    db.session.delete(advertisement)
    db.session.commit()
    return jsonify({'message': 'Advertisement has been deleted'}), 200


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User(username=data['username'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({'message': 'Logged in successfully!'}), 200
    return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully!'}), 200

with app.app_context():
    db.create_all()

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)