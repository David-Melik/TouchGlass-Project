# from flask import Flask, render_template, redirect, url_for, request, flash, session
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime, date
# import os

# from models import db, User, Preferences  # Import User and Preferences models


# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db.init_app(app)

# # Function to create the database file if it doesn't exist
# def create_database():
#     db_path = 'database.db'
#     if os.path.exists(db_path):
#         os.remove(db_path)  # Delete the existing database file to avoid schema mismatches
#     with app.app_context():
#         db.create_all()  # Create tables for both User and Preferences
#         print("Database created successfully.")

#         # Check if an admin user exists, and if not, create one
#         if not User.query.filter_by(is_admin=True).first():
#             admin_user = User(
#                 user_name='admin',
#                 surname='Admin',
#                 name='System',
#                 ddn=datetime(1970, 1, 1),  # Arbitrary date
#                 email='admin@example.com',
#                 sex='Other',
#                 password=generate_password_hash('admin123'),  # Default password
#                 is_admin=True
#             )
#             db.session.add(admin_user)
#             db.session.commit()
#             print("Default admin user created.")

# # Ensure the database is created at startup
# create_database()

# # Adding a new preference
# def add_preference(user_id, locations, music_genre):
#     new_preference = Preferences(
#         user_id=user_id,
#         locations=locations,
#         music_genre=music_genre
#     )
#     db.session.add(new_preference)
#     db.session.commit()

# # Fetching preferences for a user
# def get_user_preferences(user_id):
#     return Preferences.query.filter_by(user_id=user_id).first()

# # Home route
# @app.route('/',methods = ['GET'])
# def home():
#     return render_template('login.html')

# # Register route
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         user_name = request.form.get('user_name')
#         surname = request.form.get('surname')
#         name = request.form.get('name')
#         ddn = request.form.get('ddn')  # Date of birth
#         email = request.form.get('email')
#         sex = request.form.get('sex')
#         password = request.form.get('password')
#         locations = request.form.get('locations')  # User preferences
#         music_genre = request.form.get('music_genre')  # User preferences

#         # Check for existing email
#         if User.query.filter_by(email=email).first():
#             flash('Email already taken, please choose another one')
#             return redirect(url_for('register'))

#         # Convert ddn (date of birth) to datetime
#         try:
#             ddn_datetime = datetime.strptime(ddn, '%Y-%m-%d')
#         except ValueError:
#             flash('Invalid date format. Please use YYYY-MM-DD.')
#             return redirect(url_for('register'))

#         # Create new user and add to the database
#         new_user = User(
#             user_name=user_name,
#             surname=surname,
#             name=name,
#             ddn=ddn_datetime,
#             email=email,
#             sex=sex,
#             password=generate_password_hash(password)
#         )
#         db.session.add(new_user)
#         db.session.commit()

#         # Create user preferences if provided
#         if locations and music_genre:
#             add_preference(new_user.user_id, locations, music_genre)

#         flash('Registration successful! You can now log in.')
#         return redirect(url_for('login'))

#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         identifier = request.form.get('identifier')  # Can be either email or username
#         password = request.form.get('password')

#         # Check if identifier is an email format
#         if '@' in identifier and '.' in identifier:
#             user = User.query.filter_by(email=identifier).first()
#         else:
#             user = User.query.filter_by(user_name=identifier).first()

#         # Verify password
#         if user and check_password_hash(user.password, password):
#             session['user_id'] = user.user_id
#             session['is_admin'] = user.is_admin  # Store admin status in session
#             flash('Logged in successfully!')
#             return redirect(url_for('admin_dashboard' if user.is_admin else 'dashboard'))
#         else:
#             flash('Invalid username/email or password')

#     return render_template('login.html')


# # Dashboard route
# @app.route('/dashboard')
# def dashboard():
#     if 'user_id' not in session:
#         flash('You need to log in first.')
#         return redirect(url_for('login'))

#     user_id = session['user_id']
#     user = User.query.get(user_id)
#     preferences = get_user_preferences(user_id)  # Fetch preferences for the current user

#     return render_template('user_dashboard.html', user=user, preferences=preferences)
# @app.route('/modify_user/<int:user_id>', methods=['GET', 'POST'])
# def modify_user(user_id):
#     if 'user_id' not in session or session['user_id'] != user_id:
#         flash('You can only modify your own profile.')
#         return redirect(url_for('dashboard'))

#     user = User.query.get_or_404(user_id)

#     if request.method == 'POST':
#         user.user_name = request.form.get('user_name')
#         user.surname = request.form.get('surname')
#         user.name = request.form.get('name')
#         ddn = request.form.get('ddn')
#         user.email = request.form.get('email')
#         user.sex = request.form.get('sex')

#         if ddn:
#             try:
#                 user.ddn = datetime.strptime(ddn, '%Y-%m-%d')
#             except ValueError:
#                 flash('Invalid date format. Please use YYYY-MM-DD.')
#                 return redirect(url_for('modify_user', user_id=user_id))

#         locations = request.form.get('locations')
#         music_genre = request.form.get('music_genre')
#         preference = Preferences.query.filter_by(user_id=user_id).first()

#         if preference:
#             preference.locations = locations
#             preference.music_genre = music_genre
#         else:
#             add_preference(user_id, locations, music_genre)

#         db.session.commit()
#         flash('Profile updated successfully.')
#         return redirect(url_for('dashboard'))

#     return render_template('modify_user.html', user=user, preferences=get_user_preferences(user_id))
# @app.route('/logout')
# def logout():
#     session.pop('user_id', None)
#     flash('Logged out successfully.')
#     return redirect(url_for('login'))

# @app.route('/admin_dashboard')
# def admin_dashboard():
#     if 'user_id' not in session or not session.get('is_admin'):
#         flash('You need admin access to view this page.')
#         return redirect(url_for('login'))

#     # Query all users and pass them to the admin dashboard template
#     users = User.query.all()
#     return render_template('admin_dashboard.html', users=users)

# @app.route('/delete_user/<int:user_id>', methods=['POST'])
# def delete_user(user_id):
#     if 'user_id' not in session or not session.get('is_admin'):
#         flash('You need admin access to delete a user.')
#         return redirect(url_for('login'))

#     # Get the user object based on user_id
#     user = User.query.get_or_404(user_id)  # Ensure the user exists

#     # Delete preferences related to this user (if any)
#     preferences = Preferences.query.filter_by(user_id=user_id).first()
#     if preferences:
#         db.session.delete(preferences)  # Delete the preferences associated with the user
#         db.session.commit()  # Commit the deletion of preferences

#     # Now delete the user
#     db.session.delete(user)
#     db.session.commit()  # Commit the deletion of the user

#     flash('User and their preferences deleted successfully.')
#     return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard

# # Main entry point
# if __name__ == '__main__':
#     app.run(debug=True)
