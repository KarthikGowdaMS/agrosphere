from dotenv import load_dotenv
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

load_dotenv()
app = Flask(__name__)
db_url = os.getenv('db_url')

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
db = SQLAlchemy(app)


# Models
class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    weather_condition = db.Column(db.String(100))

# create models for farmer, field, harvest and marketplace
class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_details = db.Column(db.String(100), nullable=False)
    land_size = db.Column(db.String(100), nullable=False)
    crop_performance = db.Column(db.String(100), nullable=False)
    
class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    size = db.Column(db.String(100), nullable=False)
    soil_type = db.Column(db.String(100), nullable=False)
    
class Harvestandyield(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    farmer_id = db.Column(db.Integer,db.ForeignKey('farmer.id') ,nullable=False)
    crop_id = db.Column(db.Integer,db.ForeignKey('crop.id') ,nullable=False)
    
class Marketplace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    price = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)


@app.route('/')
def index():
    crops = Crop.query.all()
    farmers= Farmer.query.all()
    fields = Field.query.all()
    harvests = Harvestandyield.query.all()
    markets = Marketplace.query.all()
    return render_template('index.html', crops=crops,farmers=farmers, fields=fields,harvests=harvests,markets=markets)


if __name__ == '__main__':
    app.run(debug=True)
    
