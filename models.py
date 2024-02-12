

# Models
class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    weather_condition = db.Column(db.String(100))

class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password=db.column(db.String(20))
    land_size = db.Column(db.String(100), nullable=False)
    crop_performance = db.Column(db.String(100), nullable=False)
    
class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    size = db.Column(db.String(100), nullable=False)
    soil_type = db.Column(db.String(100), nullable=False)
    
class Harvestandyield(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    farmer_id = db.Column(db.Integer,db.ForeignKey('farmer.id') ,nullable=False)
    crop_id = db.Column(db.Integer,db.ForeignKey('crop.id') ,nullable=False)
    
class Marketplace(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    price = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)
