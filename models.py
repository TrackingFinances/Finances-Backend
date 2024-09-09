
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID 
import uuid
from werkzeug.security  import generate_password_hash,check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()
class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name = db.Column(db.String(255),nullable=False)
    hashText = db.Column(db.String(500),nullable = False)

    def setHashText(self,plainText):
        self.hashText = generate_password_hash(plainText)
    def checkPlainText(self,plainText):
        return check_password_hash(self.hashText,plainText)

    expenses = db.relationship('Expense',backref='user',lazy=True)
    incomes = db.relationship('Income',backref='user',lazy=True)
    investments = db.relationship('Investment',backref='user',lazy=True)

    
    def __repr__(self):
        return f'<Name {self.name}>'


class Currency(db.Model):
    __tablename__ = 'currencies'
    id = db.Column(db.Integer ,primary_key=True,autoincrement=True, nullable=False)
    currency = db.Column(db.String(3),unique=True,nullable=False)

    expenses = db.relationship('Expense',backref='currency_ref',lazy=True)
    incomes = db.relationship('Income',backref='currency_ref',lazy=True)
    investments = db.relationship('Investment',backref='currency_ref',lazy=True)

    def __repr__(self):
        return f'<Currency {self.currency}>'
    
class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(UUID(as_uuid=True) ,primary_key=True,default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'),nullable=False)
    amount = db.Column(Numeric(precision=10, scale=2), nullable=False)
    currency = db.Column(db.String(3),db.ForeignKey('currencies.currency'),nullable=False)
    date = db.Column(DateTime)
    description = db.Column(db.String(255), nullable=True)

class Income(db.Model):
    __tablename__ = 'incomes'
    id = db.Column(UUID(as_uuid=True) ,primary_key=True,default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'),nullable=False)
    amount = db.Column(Numeric(precision=10, scale=2), nullable=False)
    currency = db.Column(db.String(3),db.ForeignKey('currencies.currency'),nullable=False)
    date = db.Column(DateTime)
    description = db.Column(db.String(255), nullable=True)

class Investment(db.Model):
    __tablename__ = 'investments'
    id = db.Column(UUID(as_uuid=True) ,primary_key=True,default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'),nullable=False)
    amount = db.Column(Numeric(precision=10, scale=2), nullable=False)
    currency = db.Column(db.String(3),db.ForeignKey('currencies.currency'),nullable=False)
    date = db.Column(DateTime)
    description = db.Column(db.String(255), nullable=True)

