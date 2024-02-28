from flask import Flask, flash, render_template, request, redirect, url_for, jsonify, abort, Response
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SelectField
from wtforms.validators import InputRequired, Length, NumberRange, ValidationError
from wtforms.validators import Email
from flask_migrate import Migrate
from wtforms.validators import InputRequired, Length, Email 
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
import re
from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from sqlalchemy.orm import relationship
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__, static_url_path='/static')
basedir = os.path.abspath(os.path.dirname((__file__)))
database = "app.db"
con = sqlite3.connect(os.path.join(basedir, database))
mail = Mail(app)
app.config['SECRET_KEY'] = "jhkxhiuydu"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, database)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['MAIL_SERVER'] = 'intexcoin.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'info@intexcoin.com'
app.config['MAIL_SERVER'] = 'server148.web-hosting.com'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.add_url_rule('/uploads/<filename>', 'uploads', build_only=True)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(255)  )
    lastname = db.Column(db.String(255))

    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nin = db.Column(db.String(20), unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    def create(self, firstname='', lastname= '', email ='', password = '', nin = ''):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = generate_password_hash(password, method='sha256')
        self.nin = nin
    def save(self):
        db.session.add(self)
        db.session.commit()
    def commit(self):
        db.session.commit()   
    def get_id(self):
        return str(self.id)

class Realtor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', backref=db.backref('realtor', uselist=False))
    facebook_link = db.Column(db.String(255), nullable=True)
    instagram_link = db.Column(db.String(255), nullable=True)
    realtor_description = db.Column(db.Text, nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

class PropertyOwner(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', backref=db.backref('propertyowner', uselist=False))
    facebook_link = db.Column(db.String(255), nullable=True)
    instagram_link = db.Column(db.String(255), nullable=True)
    property_owner_description = db.Column(db.Text, nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

class Developer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', backref=db.backref('developer', uselist=False))
    company_name = db.Column(db.String(255), nullable=True)
    company_registration_number = db.Column(db.String(255), nullable=True)
    company_location = db.Column(db.String(255), nullable=True)
    facebook_link = db.Column(db.String(255), nullable=True)
    instagram_link = db.Column(db.String(255), nullable=True)
    developer_description = db.Column(db.Text, nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()
        
# Property Model
class Property(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    service_type = db.Column(db.String(255), nullable=False)  # Serviced, Newly Built, Developing, Furnished
    description = db.Column(db.Text, nullable=False)
    num_rooms = db.Column(db.Integer, nullable=False)
    num_baths = db.Column(db.Integer, nullable=False)
    num_toilets = db.Column(db.Integer, nullable=False)
    property_type = db.Column(db.String(20), nullable=False)  # Sale, Rent, Short Let, Developing
    main_image = db.Column(db.LargeBinary)
    main_image_filename = db.Column(db.String(100))
    main_image_one = db.Column(db.LargeBinary)
    main_image_one_filename = db.Column(db.String(100))
    main_image_two = db.Column(db.LargeBinary)
    main_image_two_filename = db.Column(db.String(100))
    main_image_three = db.Column(db.LargeBinary)
    main_image_three_filename = db.Column(db.String(100))
    main_image_four = db.Column(db.LargeBinary)
    main_image_four_filename = db.Column(db.String(100))
    main_image_five = db.Column(db.LargeBinary)
    main_image_five_filename = db.Column(db.String(100))
    likes = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', backref='properties')
    approved = db.Column(db.Boolean, default=False)  # Define the 'approved' field

    def save(self):
        db.session.add(self)
        db.session.commit()
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    property_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define a relationship with the User model
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))


class Secure(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def not_auth(self):
        return "not allowed"

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Define relationships
    property = db.relationship('Property', backref='cart_items')






@app.route('/create_property', methods=['GET', 'POST'])
@login_required
def create_property():
    if request.method == 'POST':
        title = request.form['title']
        location = request.form['location']
        price = float(request.form['price'])  # Assuming the price is a float
        service_type = request.form['service_type']
        description = request.form['description']
        num_rooms = int(request.form['num_rooms'])
        num_baths = int(request.form['num_baths'])
        num_toilets = int(request.form['num_toilets'])
        property_type = request.form['property_type']

         # Ensure the UPLOAD_FOLDER exists
        upload_folder = os.path.join(app.static_folder, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        print("UPLOAD_FOLDER:", upload_folder)  # Debugging line
        # Upload Main Image
        main_image = request.files['main_image']
        if main_image and allowed_file(main_image.filename):
            filename = secure_filename(main_image.filename)
            print("Saving to:", os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Debugging line
            main_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            main_image_filename = filename
        else:
            main_image_filename = None

        # Upload Image One
        main_image_one = request.files['main_image_one']
        if main_image_one and allowed_file(main_image_one.filename):
            filename = secure_filename(main_image_one.filename)
            main_image_one.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            main_image_one_filename = filename
        else:
            main_image_one_filename = None

        # Upload Image Two
        main_image_two = request.files['main_image_two']
        if main_image_two and allowed_file(main_image_two.filename):
            filename = secure_filename(main_image_two.filename)
            main_image_two.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            main_image_two_filename = filename
        else:
            main_image_two_filename = None
            
        main_image_three = request.files['main_image_three']
        if main_image_three and allowed_file(main_image_three.filename):
            filename = secure_filename(main_image_three.filename)
            main_image_three.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            main_image_three_filename = filename
        else:
            main_image_three_filename = None
            
        main_image_four = request.files['main_image_four']
        if main_image_four and allowed_file(main_image_four.filename):
            filename = secure_filename(main_image_four.filename)
            main_image_four.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            main_image_four_filename = filename
        else:
            main_image_four_filename = None

        main_image_five = request.files['main_image_five']
        if main_image_five and allowed_file(main_image_five.filename):
            filename = secure_filename(main_image_three.filename)
            main_image_five.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            main_image_five_filename = filename
        else:
            main_image_five_filename = None
        
        new_property = Property(
            title=title,
            location=location,
            price=price,
            service_type=service_type,
            description=description,
            num_rooms=num_rooms,
            num_baths=num_baths,
            num_toilets=num_toilets,
            property_type=property_type,
            main_image_filename = main_image_filename,
            main_image_one_filename = main_image_one_filename,
            main_image_two_filename = main_image_two_filename,
            main_image_three_filename = main_image_three_filename,
            main_image_four_filename = main_image_four_filename,
            main_image_five_filename = main_image_five_filename,
             approved=False,
            user=current_user 
          
        )
        print("Current User:", current_user)
        print("Property User:", new_property.user)

        db.session.add(new_property)
        db.session.commit()
        flash('Property has been created')
        return redirect(url_for('index'))

    return render_template('create_property.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Check if current user is an admin (you should have a way to identify admin users)
    if not current_user.is_admin:
        return redirect(url_for('index'))  # Redirect to homepage if not admin

    # Fetch pending properties for approval
    pending_properties = Property.query.filter_by(approved=False).all()

    return render_template('admin_dashboard.html', pending_properties=pending_properties)


@app.route('/approve_property/<int:property_id>')
@login_required
def approve_property(property_id):
    # Check if current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('index'))  # Redirect to homepage if not admin

    # Find the property by ID
    property_to_approve = Property.query.get_or_404(property_id)

    # Approve the property
    property_to_approve.approved = True
    db.session.commit()

    # Send notification to the user
    send_approval_notification(property_to_approve.user.email)

    flash('Property has been approved')
    return redirect(url_for('admin_dashboard'))

from flask_mail import Message

def send_approval_notification(user_email, property_id):
    """
    Sends an approval notification to the user's email and stores the message in the user's dashboard.
    """
    # Send email notification
    msg = Message(subject="Your property has been approved!",
                  recipients=[user_email],
                  body="Your property has been approved.")
    mail.send(msg)
    
    # Update user's notification dashboard
    user = User.query.filter_by(email=user_email).first()
    if user:
        user.notifications.append(Notification(message="Your property has been approved.", property_id=property_id))
        db.session.commit()
    else:
        flash('User not found')  # Handle the case where user is not found

def send_rejection_notification(user_email, property_id):
    """
    Sends a rejection notification to the user's email and stores the message in the user's dashboard.
    """
    # Send email notification
    msg = Message(subject="Your property has been rejected",
                  recipients=[user_email],
                  body="Your property has been rejected.")
    mail.send(msg)
    
    # Update user's notification dashboard
    user = User.query.filter_by(email=user_email).first()
    if user:
        user.notifications.append(Notification(message="Your property has been rejected.", property_id=property_id))
        db.session.commit()
    else:
        flash("User not found!")  # Handle the case where user is not found



@app.route('/reject_property/<int:property_id>')
@login_required
def reject_property(property_id):
    # Check if current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('index'))  # Redirect to homepage if not admin

    # Find the property by ID
    property_to_reject = Property.query.get_or_404(property_id)

    # Delete the property
    db.session.delete(property_to_reject)
    db.session.commit()

    # Send notification to the user
    send_rejection_notification(property_to_reject.user.email)

    flash('Property has been rejected')
    return redirect(url_for('admin_dashboard'))

@app.route('/signin',methods=['GET','POST'])
def signin():
    user = User()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['passwords']
        user = User.query.filter_by(email=email,is_admin=True).first()
       
        if user:
            if user.password == password:
                login_user(user)
                return redirect('admin')

                
                
            


    return render_template('admin_login.html')
@app.route('/process',methods=['GET','POST'])

def process():
    auths = User()
    if request.method == "POST":
        
        password = request.form['pass']
        email = request.form['email']
        auths = User(
             password=password,email=email,is_admin=True)
        db.session.add(auths)
        db.session.commit()
        return "welcome sign up completed"
    return render_template('admin_signup.html')
    
@app.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    if request.method == 'POST':
        property_id = request.form.get('property_id')

        # Validate property ID
        if not property_id or not property_id.isdigit():
            flash('Invalid property ID', 'error')
            return redirect(url_for('index'))

        # Check if the property exists
        property = Property.query.get(property_id)
        if not property:
            flash('Property not found', 'error')
            return redirect(url_for('index'))

        # Check if the property is already in the user's cart
        existing_cart_item = CartItem.query.filter_by(property_id=property_id, user_id=current_user.id).first()
        if existing_cart_item:
            flash('Property is already in your cart', 'error')
            return redirect(request.referrer or url_for('index'))  # Redirect back to the previous page or index

        # Add the property to the user's cart
        cart_item = CartItem(property_id=property_id, user_id=current_user.id)
        db.session.add(cart_item)
        try:
            db.session.commit()
            flash('Property added to your cart', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the property to your cart. Please try again.', 'error')
            app.logger.error(f"Error adding property to cart: {e}")
        return redirect(request.referrer or url_for('index'))  # Redirect back to the previous page or index

@app.route('/cart')
@login_required
def cart():
    # Query the cart items for the current user
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', cart_items=cart_items)

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    # Find the cart item by ID
    cart_item = CartItem.query.get(item_id)
    if not cart_item:
        flash('Cart item not found', 'error')
        return redirect(url_for('cart'))
    
    # Check if the cart item belongs to the current user
    if cart_item.user_id != current_user.id:
        flash('You are not authorized to remove this item from the cart', 'error')
        return redirect(url_for('cart'))
    
    # Delete the cart item from the database
    db.session.delete(cart_item)
    db.session.commit()
    
    flash('Item removed from cart', 'success')
    return redirect(url_for('cart'))
    

@app.route('/')
def index():
    properties = Property.query.all()
    approved_properties = Property.query.filter_by(approved=True).all()
    pending_properties = Property.query.filter_by(approved=False).all()
    return render_template('index.html', properties=properties, approved_properties=approved_properties, pending_properties=pending_properties)

# @app.route('/create_property', methods=['GET', 'POST'])
# @login_required
# def create_property():
#     form = PropertyForm()

#     if form.validate_on_submit():
#         form.save()
#         flash('Property created successfully!', 'success')
#         return redirect(url_for('index'))

#     return render_template('create_property.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')

        email = request.form.get('email')
        password = request.form.get('password')
        nin = request.form.get('nin')

        new_user = User(firstname= firstname, lastname=lastname, email=email, nin=nin)
        new_user.set_password(password)
        new_user.save()

        return render_template('role_selection.html', user=new_user)

    return render_template('signup.html')

@app.route('/select_role/<int:user_id>', methods=['GET', 'POST'])
def select_role(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        role = request.form.get('role')

        if role == 'realtor':
            return render_template('realtor_signup.html', user=user)
        elif role == 'property_owner':
            return render_template('property_owner_signup.html', user=user)
        elif role == 'developer':
            return render_template('developer_signup.html', user=user)

    return render_template('role_selection.html', user=user)

@app.route('/realtor_signup/<int:user_id>', methods=['POST'])
def realtor_signup(user_id):
    user = User.query.get_or_404(user_id)

    facebook_link = request.form.get('facebook_link')
    instagram_link = request.form.get('instagram_link')
    realtor_description = request.form.get('realtor_description')

    realtor = Realtor(user=user, facebook_link=facebook_link, instagram_link=instagram_link,
                      realtor_description=realtor_description)
    realtor.save()

    return redirect(url_for('index'))

@app.route('/property_owner_signup/<int:user_id>', methods=['POST'])
def property_owner_signup(user_id):
    user = User.query.get_or_404(user_id)

    facebook_link = request.form.get('facebook_link')
    instagram_link = request.form.get('instagram_link')
    property_owner_description = request.form.get('property_owner_description')

    property_owner = PropertyOwner(user=user, facebook_link=facebook_link, instagram_link=instagram_link,
                                   property_owner_description=property_owner_description)
    property_owner.save()

    return redirect(url_for('index'))

@app.route('/developer_signup/<int:user_id>', methods=['POST'])
def developer_signup(user_id):
    user = User.query.get_or_404(user_id)

    company_name = request.form.get('company_name')
    company_registration_number = request.form.get('company_registration_number')
    company_location = request.form.get('company_location')
    facebook_link = request.form.get('facebook_link')
    instagram_link = request.form.get('instagram_link')
    developer_description = request.form.get('developer_description')

    developer = Developer(user=user, company_name=company_name,
                          company_registration_number=company_registration_number,
                          company_location=company_location,
                          facebook_link=facebook_link, instagram_link=instagram_link,
                          developer_description=developer_description)
    developer.save()

    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')

    return render_template('login.html')


@app.route('/nav')
def nav():
    return render_template('nav.html')
@app.route('/dash_nav')
def dash_nav():
    return render_template('dash_nav.html')    

@app.route('/listing')
def listing():
    properties = Property.query.all()
    approved_properties = Property.query.filter_by(approved=True).all()
    pending_properties = Property.query.filter_by(approved=False).all()
    return render_template('listing.html' , properties=properties, approved_properties=approved_properties, pending_properties=pending_properties)


@app.route('/listinguser')
def listinguser():
    return render_template('listing_user.html')


# @app.route('/property/details/<int:property_id>',  methods=['GET', 'POST'])
# def property_details(property_id):
#     property = Property.query.get(property_id)
#     approved_properties = Property.query.filter_by(approved=True).all()
#     pending_properties = Property.query.filter_by(approved=False).all()
#     if not property:
#         return("error")
#     return render_template('property_details.html',  property=property, approved_properties=approved_properties, pending_properties=pending_properties)
@app.route('/property/details/<int:property_id>', methods=['GET', 'POST'])
def property_details(property_id):
    property = Property.query.get(property_id)
    approved_properties = Property.query.filter_by(approved=True).all()
    pending_properties = Property.query.filter_by(approved=False).all()

    if not property:
        flash('Property not found', 'error')
        return redirect(url_for('index'))  # Redirect to the home page or any other appropriate page

    if request.method == 'POST':
        if 'add_to_cart' in request.form:
            # Add the property to the user's cart
            cart_item = CartItem(property_id=property_id, user_id=current_user.id)
            db.session.add(cart_item)
            try:
                db.session.commit()
                flash('Property added to your cart', 'success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while adding the property to your cart. Please try again.', 'error')
                app.logger.error(f"Error adding property to cart: {e}")
            return redirect(url_for('property_details', property_id=property_id))  # Redirect back to the same property details page after adding to cart

    # Render the property details template and pass the property object to it
    return render_template('property_details.html', property=property, approved_properties=approved_properties, pending_properties=pending_properties)


@app.route('/dashboard')
@login_required
def dashboard():
    user_notifications = current_user.notifications
    return render_template('dashboard.html', notifications=user_notifications)

@app.route('/creatinglisting')
def createlisting():
    return render_template('createlisting.html')





@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route("/db")
def database():
    db.drop_all()
    db.create_all()
    return "Hello done!!!"

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
