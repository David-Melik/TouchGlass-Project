from flask import Blueprint, render_template, request, redirect, url_for, flash, session,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.helpers import add_preference, get_user_preferences
from .models import db, User, Preferences, Event

register_views = Blueprint('views', __name__)

# Home route
@register_views.route('/')
def home():
    return render_template('./home.html')

@register_views.route('/event_calendar')
def event_calendar():
    return render_template('./eventcalendar.html')
@register_views.route('/events', methods=['GET'])
def get_events():
    # Query all events from the database
    events = Event.query.all()
    # Return a JSON representation of the events
    return jsonify([
        {
            'title': event.title,
            'start': event.date_event.isoformat(),  # Format the date as ISO string
            'description': event.description,  # Include the description
            'localisation': event.localisation,
            'age_requirement': event.age_requirement,
            'rules': event.rules,
            'average_price': event.average_price,
            'student_advantages': event.student_advantages,
            'event_type': event.event_type
        } for event in events
    ])


@register_views.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        # Gather data from the submitted form
        title = request.form['title']
        description = request.form['description']
        localisation = request.form['localisation']
        age_requirement = request.form['age_requirement']
        # Parse the date_event from the input format
        date_event = datetime.strptime(request.form['date_event'], '%Y-%m-%dT%H:%M')
        rules = request.form.get('rules', '')  # Use empty string if not provided
        average_price = request.form.get('average_price', '')  # Use empty string if not provided
        student_advantages = request.form.get('student_advantages', '')  # Use empty string if not provided
        event_type = request.form['event_type']
        
        # Create a new Event instance with the collected data
        new_event = Event(
            title=title,
            description=description,
            localisation=localisation,
            age_requirement=age_requirement,
            date_event=date_event,
            rules=rules,
            average_price=average_price,
            student_advantages=student_advantages,
            event_type=event_type
        )

        # Add the new event to the database session and commit the changes
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('views.event_calendar'))  # Redirect to the home page after adding the event

    return render_template('add_event.html')  # Render the form to add a new event if GET request


# Register route
@register_views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        surname = request.form.get('surname')
        name = request.form.get('name')
        ddn = request.form.get('ddn')  # Date of birth
        email = request.form.get('email')
        sex = request.form.get('sex')
        password = request.form.get('password')
        locations = request.form.get('locations')  # User preferences
        music_genre = request.form.get('music_genre')  # User preferences

        # Check if email is already taken
        if User.query.filter_by(email=email).first():
            flash('Email already taken, please choose another one')
            return redirect(url_for('views.register'))  # Fixed reference to views.register

        # Convert ddn (date of birth) to datetime
        try:
            ddn_datetime = datetime.strptime(ddn, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.')
            return redirect(url_for('views.register'))  # Fixed reference to views.register

        # Create new user and add to the database
        new_user = User(
            user_name=user_name,
            surname=surname,
            name=name,
            ddn=ddn_datetime,
            email=email,
            sex=sex,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        # Create user preferences if provided
        if locations and music_genre:
            add_preference(new_user.user_id, locations, music_genre)
        
        flash('Registration successful! You can now log in.')
        return redirect(url_for('views.login'))  # Fixed reference to views.login
    
    return render_template('register.html')

# Login route
@register_views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')  # Can be either email or username
        password = request.form.get('password')
        
        # Check if identifier is email or username
        user = User.query.filter_by(email=identifier).first() if '@' in identifier else User.query.filter_by(user_name=identifier).first()
        
        # Verify password
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['is_admin'] = user.is_admin  # Store admin status in session
            flash('Logged in successfully!')
            return redirect(url_for('views.admin_dashboard' if user.is_admin else 'views.dashboard'))  # Fixed reference to views.admin_dashboard and views.dashboard
        else:
            flash('Invalid username/email or password')
    
    return render_template('login.html')

# Dashboard route
@register_views.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('views.login'))  # Fixed reference to views.login
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    preferences = get_user_preferences(user_id)  # Fetch preferences for the current user

    return render_template('user_dashboard.html', user=user, preferences=preferences)

# Modify user profile route
@register_views.route('/modify_user/<int:user_id>', methods=['GET', 'POST'])
def modify_user(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        flash('You can only modify your own profile.')
        return redirect(url_for('views.dashboard'))  # Fixed reference to views.dashboard
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.user_name = request.form.get('user_name')
        user.surname = request.form.get('surname')
        user.name = request.form.get('name')
        ddn = request.form.get('ddn')
        user.email = request.form.get('email')
        user.sex = request.form.get('sex')

        if ddn:
            try:
                user.ddn = datetime.strptime(ddn, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.')
                return redirect(url_for('views.modify_user', user_id=user_id))  # Fixed reference to views.modify_user

        locations = request.form.get('locations')
        music_genre = request.form.get('music_genre')
        preference = Preferences.query.filter_by(user_id=user_id).first()
        
        if preference:
            preference.locations = locations
            preference.music_genre = music_genre
        else:
            add_preference(user_id, locations, music_genre)

        db.session.commit()
        flash('Profile updated successfully.')
        return redirect(url_for('views.dashboard'))  # Fixed reference to views.dashboard
    
    return render_template('modify_user.html', user=user, preferences=get_user_preferences(user_id))

# Logout route
@register_views.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.')
    return redirect(url_for('views.login'))  # Fixed reference to views.login

# Admin Dashboard route
@register_views.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('You need admin access to view this page.')
        return redirect(url_for('views.login'))  # Fixed reference to views.login
    
    # Query all users and pass them to the admin dashboard template
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

# Delete user route
@register_views.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('You need admin access to delete a user.')
        return redirect(url_for('views.login'))  # Fixed reference to views.login
    
    # Get the user object based on user_id
    user = User.query.get_or_404(user_id)  # Ensure the user exists
    
    # Delete preferences related to this user (if any)
    preferences = Preferences.query.filter_by(user_id=user_id).first()
    if preferences:
        db.session.delete(preferences)  # Delete the preferences associated with the user
        db.session.commit()  # Commit the deletion of preferences

    # Now delete the user
    db.session.delete(user)
    db.session.commit()  # Commit the deletion of the user
    
    flash('User and their preferences deleted successfully.')
    return redirect(url_for('views.admin_dashboard'))  # Fixed reference to views.admin_dashboard
