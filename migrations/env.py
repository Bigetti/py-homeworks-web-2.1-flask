from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask
from app import db, User, Advertisement  # Импорт ваших моделей
from flask_script import Manager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///advertisements.db'
app.config['SECRET_KEY'] = 'abrakagabra'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Импорт всех моделей для Alembic
from app import User, Advertisement

# Для создания миграций с использованием Flask-Migrate
from flask_script import Manager

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()