from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from database import db

class ItemGroupe(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.VARCHAR(100), nullable=False)
  description = db.Column(db.VARCHAR(100), nullable=True)
  color = db.Column(db.Float, nullable=True)
  state = db.Column(db.Integer, server_default= "0")

class Item(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.VARCHAR(100), nullable=False)
  description = db.Column(db.VARCHAR(100), nullable=True)
  price = db.Column(db.Float, nullable=True)
  state = db.Column(db.Integer, server_default= "0")
