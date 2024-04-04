from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///advertisements.db'
db = SQLAlchemy(app)

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner = db.Column(db.String(100), nullable=False)


# Маршрут для приветственной страницы
@app.route('/')
def hello():
    return '<h1>Добро пожаловать на главную страницу приложения!</h1>'



@app.route('/advertisements', methods=['GET'])
def show_all_advertisements():
    advertisements = Advertisement.query.all()
    return render_template('advertisements.html', advertisements=advertisements)


@app.route('/advertisement', methods=['POST'])
def create_advertisement():
    data = request.json
    new_advertisement = Advertisement(title=data['title'], description=data['description'], owner=data['owner'])
    db.session.add(new_advertisement)
    db.session.commit()
    return jsonify({'message': 'New advertisement created!'}), 201

@app.route('/advertisement/<int:id>', methods=['GET'])
def get_advertisement(id):
    advertisement = Advertisement.query.get(id)
    if advertisement is None:
        return jsonify({'message': 'Advertisement not found'}), 404
    advertisement_data = {'id': advertisement.id, 'title': advertisement.title, 'description': advertisement.description, 'creation_date': advertisement.creation_date, 'owner': advertisement.owner}
    return jsonify(advertisement_data)

@app.route('/advertisement/<int:id>', methods=['DELETE'])
def delete_advertisement(id):
    advertisement = Advertisement.query.get(id)
    if advertisement is None:
        return jsonify({'message': 'Advertisement not found'}), 404
    db.session.delete(advertisement)
    db.session.commit()
    return jsonify({'message': 'Advertisement has been deleted'}), 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)