from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.helpers import add_preference, get_user_preferences
from app.models.user import friendship_association

from .models import db, User, Preferences, Event, Notification

register_views = Blueprint("views", __name__)


# Home route
@register_views.route("/")
def home():
    return render_template("./home.html")


@register_views.route("/event_calendar")
def event_calendar():
    return render_template("./eventcalendar.html")


@register_views.route("/events", methods=["GET"])
def get_events():
    # Query all events from the database
    events = Event.query.all()
    # Return a JSON representation of the events
    return jsonify(
        [
            {
                "title": event.title,
                "start": event.date_event.isoformat(),  # Format the date as ISO string
                "description": event.description,  # Include the description
                "localisation": event.localisation,
                "age_requirement": event.age_requirement,
                "rules": event.rules,
                "average_price": event.average_price,
                "student_advantages": event.student_advantages,
                "event_type": event.event_type,
                "event_id": event.event_id,
            }
            for event in events
        ]
    )


@register_views.route("/add_event", methods=["GET", "POST"])
def add_event():
    if request.method == "POST":  # When the form is submitted
        # Get form data
        event_title = request.form["titre"]
        event_description = request.form["description"]
        event_rules = request.form["rules"]
        event_localisation = request.form["localisation"]
        event_age_requirement = request.form["age_requirement"]
        event_date = request.form["date_event"]
        event_average_price = request.form["average_price"]
        event_student_advantages = request.form["student_advantages"]
        event_type = request.form["event_type"]

        # Create new event
        new_event = Event(
            title=event_title,
            description=event_description,
            rules=event_rules,
            localisation=event_localisation,
            age_requirement=event_age_requirement,
            average_price=event_average_price,
            student_advantages=event_student_advantages,
            date_event=datetime.strptime(event_date, "%Y-%m-%dT%H:%M"),
            event_type=event_type,
        )
        try:
            db.session.add(new_event)
            db.session.commit()

            # Create notification for event creation
            notification = Notification(
                action="Created",
                message=f"Event '{new_event.title}' was created at {new_event.date_event.strftime('%Y-%m-%d %H:%M')}",
            )
            db.session.add(notification)
            db.session.commit()

            return redirect(url_for("views.event_calendar"))

        except Exception as e:
            return f"An error occurred: {str(e)}"

    else:
        events = Event.query.all()
        return render_template("add_event.html", events=events)


# Register route
@register_views.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        surname = request.form.get("surname")
        name = request.form.get("name")
        ddn = request.form.get("ddn")  # Date of birth
        email = request.form.get("email")
        sex = request.form.get("sex")
        password = request.form.get("password")
        locations = request.form.get("locations")  # User preferences
        music_genre = request.form.get("music_genre")  # User preferences

        # Check if email is already taken
        if User.query.filter_by(email=email).first():
            flash("Email already taken, please choose another one")
            return redirect(
                url_for("views.register")
            )  # Fixed reference to views.register

        # Convert ddn (date of birth) to datetime
        try:
            ddn_datetime = datetime.strptime(ddn, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return redirect(
                url_for("views.register")
            )  # Fixed reference to views.register

        # Create new user and add to the database
        new_user = User(
            user_name=user_name,
            surname=surname,
            name=name,
            ddn=ddn_datetime,
            email=email,
            sex=sex,
            password=generate_password_hash(password),
        )
        db.session.add(new_user)
        db.session.commit()

        # Create user preferences if provided
        if locations and music_genre:
            add_preference(new_user.user_id, locations, music_genre)

        flash("Registration successful! You can now log in.")
        return redirect(url_for("views.login"))  # Fixed reference to views.login

    return render_template("register.html")


# Login route
@register_views.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier")  # Can be either email or username
        password = request.form.get("password")

        # Check if identifier is email or username
        user = (
            User.query.filter_by(email=identifier).first()
            if "@" in identifier
            else User.query.filter_by(user_name=identifier).first()
        )

        # Verify password
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.user_id
            session["is_admin"] = user.is_admin  # Store admin status in session
            flash("Logged in successfully!")
            return redirect(
                url_for("views.admin_dashboard" if user.is_admin else "views.dashboard")
            )  # Fixed reference to views.admin_dashboard and views.dashboard
        else:
            flash("Invalid username/email or password")

    return render_template("login.html")


# Dashboard route
@register_views.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("You need to log in first.")
        return redirect(url_for("views.login"))  # Fixed reference to views.login

    user_id = session["user_id"]
    user = User.query.get(user_id)
    preferences = get_user_preferences(
        user_id
    )  # Fetch preferences for the current user

    return render_template("user_dashboard.html", user=user, preferences=preferences)


# Modify user profile route
@register_views.route("/modify_user/<int:user_id>", methods=["GET", "POST"])
def modify_user(user_id):
    if "user_id" not in session or session["user_id"] != user_id:
        flash("You can only modify your own profile.")
        return redirect(
            url_for("views.dashboard")
        )  # Fixed reference to views.dashboard

    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.user_name = request.form.get("user_name")
        user.surname = request.form.get("surname")
        user.name = request.form.get("name")
        ddn = request.form.get("ddn")
        user.email = request.form.get("email")
        user.sex = request.form.get("sex")

        if ddn:
            try:
                user.ddn = datetime.strptime(ddn, "%Y-%m-%d")
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.")
                return redirect(
                    url_for("views.modify_user", user_id=user_id)
                )  # Fixed reference to views.modify_user

        locations = request.form.get("locations")
        music_genre = request.form.get("music_genre")
        preference = Preferences.query.filter_by(user_id=user_id).first()

        if preference:
            preference.locations = locations
            preference.music_genre = music_genre
        else:
            add_preference(user_id, locations, music_genre)

        db.session.commit()
        flash("Profile updated successfully.")
        return redirect(
            url_for("views.dashboard")
        )  # Fixed reference to views.dashboard

    return render_template(
        "modify_user.html", user=user, preferences=get_user_preferences(user_id)
    )


# Logout route
@register_views.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully.")
    return redirect(url_for("views.login"))  # Fixed reference to views.login


# Admin Dashboard route
@register_views.route("/admin_dashboard")
def admin_dashboard():
    if "user_id" not in session or not session.get("is_admin"):
        flash("You need admin access to view this page.")
        return redirect(url_for("views.login"))  # Fixed reference to views.login

    # Query all users and pass them to the admin dashboard template
    users = User.query.all()
    return render_template("admin_dashboard.html", users=users)


# Delete user route
@register_views.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if "user_id" not in session or not session.get("is_admin"):
        flash("You need admin access to delete a user.")
        return redirect(url_for("views.login"))  # Fixed reference to views.login

    # Get the user object based on user_id
    user = User.query.get_or_404(user_id)  # Ensure the user exists

    # Delete preferences related to this user (if any)
    preferences = Preferences.query.filter_by(user_id=user_id).first()
    if preferences:
        db.session.delete(
            preferences
        )  # Delete the preferences associated with the user
        db.session.commit()  # Commit the deletion of preferences

    # Now delete the user
    db.session.delete(user)
    db.session.commit()  # Commit the deletion of the user

    flash("User and their preferences deleted successfully.")
    return redirect(
        url_for("views.admin_dashboard")
    )  # Fixed reference to views.admin_dashboard


# -------------------------- Friends Features ------------------------
@register_views.route("/friends")
def friends():
    if "user_id" not in session:
        flash("You need to log in first.")
        return redirect(url_for("login"))

    current_user = User.query.get(session["user_id"])

    # All users except the current one
    users = User.query.filter(User.user_id != current_user.user_id).all()

    # Pending friend requests (requests made by other users to current_user)
    friend_requests = (
        db.session.query(User)
        .join(friendship_association, friendship_association.c.user_id == User.user_id)
        .filter(
            friendship_association.c.friend_id == current_user.user_id,
            friendship_association.c.status == "requested",
        )
        .all()
    )

    # Waiting friend requests (requests made by current_user to other users that are still pending)
    waiting_requests = (
        db.session.query(User)
        .join(
            friendship_association, friendship_association.c.friend_id == User.user_id
        )
        .filter(
            friendship_association.c.user_id == current_user.user_id,
            friendship_association.c.status == "requested",
        )
        .all()
    )

    # Accepted friends (requests where both users have accepted the friendship)
    accepted_friends = (
        db.session.query(User)
        .join(
            friendship_association, friendship_association.c.friend_id == User.user_id
        )
        .filter(
            friendship_association.c.user_id == current_user.user_id,
            friendship_association.c.status == "accepted",
        )
        .all()
    )

    return render_template(
        "friends.html",
        current_user=current_user,
        users=users,
        friend_requests=friend_requests,
        waiting_requests=waiting_requests,
        accepted_friends=accepted_friends,  # Pass the accepted friends to the template
    )


@register_views.route("/account/<string:user_name>")
def account(user_name):
    # Get the currently logged-in user
    current_user = User.query.get(session.get("user_id"))

    if not current_user:
        flash("You need to be logged in to view this page.", "danger")
        return redirect(url_for("login"))

    # Use user_name to get the user whose profile we want to view
    user = User.query.filter_by(user_name=user_name).first()

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("views.friends"))

    # Check if the logged-in user and the viewed user are friends
    checkStatusFriend = (
        db.session.query(friendship_association)
        .filter_by(
            user_id=user.user_id, friend_id=current_user.user_id, status="accepted"
        )
        .first()
    )

    # If they are not friends or the friendship is not accepted, redirect to friends
    if not checkStatusFriend:
        flash(
            "You are not friends with this user, or the friendship is not accepted.",
            "warning",
        )
        return redirect(url_for("friends"))

    # Get the user's friends
    friends = user.friends

    return render_template(
        "account.html", user=user, current_user=current_user, friends=friends
    )


@register_views.route("/add_friend/<int:friend_id>")
def add_friend(friend_id):
    if "user_id" not in session:
        flash("You need to log in first.")
        return redirect(url_for("login"))

    current_user = User.query.get(session["user_id"])
    friend = User.query.get(friend_id)

    if not friend:
        flash("The user does not exist.")
        return redirect(url_for("friends"))

    # Check if a request already exists (either accepted or requested)
    existing_requests = (
        db.session.query(friendship_association)
        .filter(
            (friendship_association.c.user_id == current_user.user_id)
            & (friendship_association.c.friend_id == friend.user_id)
            | (friendship_association.c.user_id == friend.user_id)
            & (friendship_association.c.friend_id == current_user.user_id)
        )
        .all()
    )

    # If there are no previous requests or accepted friends, send a new friend request
    if not existing_requests:
        stmt = friendship_association.insert().values(
            user_id=current_user.user_id, friend_id=friend.user_id, status="requested"
        )
        db.session.execute(stmt)
        db.session.commit()
        flash(f"Friend request sent to {friend.name}.")
    else:
        # If there is a pending or accepted request, notify the user
        for request in existing_requests:
            if request.status == "requested":
                flash(f"You have already sent a request to {friend.name}.")
            elif request.status == "accepted":
                flash(f"You are already friends with {friend.name}.")
            break

    return redirect(url_for("friends"))


@register_views.route("/accept_friend/<int:friend_id>")
def accept_friend(friend_id):
    if "user_id" not in session:
        flash("You need to log in first.")
        return redirect(url_for("login"))

    current_user = User.query.get(session["user_id"])
    friend = User.query.get(friend_id)

    if not friend:
        flash("The user does not exist.")
        return redirect(url_for("friends"))

    # Get the incoming friend request from the association table
    incoming_request = (
        db.session.query(friendship_association)
        .filter_by(
            user_id=friend.user_id, friend_id=current_user.user_id, status="requested"
        )
        .first()
    )

    if incoming_request:
        # Update the friend request status to 'accepted'
        db.session.execute(
            friendship_association.update()
            .where(
                (friendship_association.c.user_id == friend.user_id)
                & (friendship_association.c.friend_id == current_user.user_id)
            )
            .values(status="accepted")
        )

        # Ensure the reciprocal relationship is created
        reciprocal_request = (
            db.session.query(friendship_association)
            .filter_by(user_id=current_user.user_id, friend_id=friend.user_id)
            .first()
        )

        if not reciprocal_request:
            db.session.execute(
                friendship_association.insert().values(
                    user_id=current_user.user_id,
                    friend_id=friend.user_id,
                    status="accepted",
                )
            )
        db.session.commit()
        flash(f"You are now friends with {friend.name}.")
    else:
        flash("No friend request found.")

    return redirect(url_for("friends"))


@register_views.route("/reject_friend/<int:friend_id>")
def reject_friend(friend_id):
    if "user_id" not in session:
        flash("You need to log in first.")
        return redirect(url_for("login"))

    current_user = User.query.get(session["user_id"])
    friend = User.query.get(friend_id)

    if not friend:
        flash("The user does not exist.")
        return redirect(url_for("friends"))

    # Check if there's a pending friend request
    incoming_request = (
        db.session.query(friendship_association)
        .filter_by(
            user_id=friend.user_id, friend_id=current_user.user_id, status="requested"
        )
        .first()
    )

    if incoming_request:
        # Properly delete the request using SQLAlchemy's delete method
        db.session.execute(
            friendship_association.delete().where(
                (friendship_association.c.user_id == friend.user_id)
                & (friendship_association.c.friend_id == current_user.user_id)
            )
        )
        db.session.commit()
        flash(f"Friend request from {friend.name} has been rejected.")
    else:
        flash("No friend request found.")

    return redirect(url_for("friends"))


@register_views.route("/remove_friend/<int:friend_id>")
def remove_friend(friend_id):
    if "user_id" not in session:
        flash("You need to log in first.")
        return redirect(url_for("login"))

    # Fetch the current user and the friend
    current_user = User.query.get(session["user_id"])
    friend = User.query.get(friend_id)

    if not friend:
        flash("The user does not exist.")
        return redirect(url_for("friends"))

    # Remove the friendship in both directions (both user->friend and friend->user)
    db.session.execute(
        friendship_association.delete().where(
            (friendship_association.c.user_id == current_user.user_id)
            & (friendship_association.c.friend_id == friend.user_id)
        )
    )

    db.session.execute(
        friendship_association.delete().where(
            (friendship_association.c.user_id == friend.user_id)
            & (friendship_association.c.friend_id == current_user.user_id)
        )
    )

    db.session.commit()
    flash(f"You have removed {friend.name} from your friends list.")
    return redirect(url_for("friends"))


# ----------------------Notifications-----------------------------------------


# Route for deleting an event
@register_views.route("/delete/<int:event_id>", methods=["POST"])
def delete_event(event_id):
    event_to_delete = Event.query.get_or_404(event_id)
    try:
        event_title = event_to_delete.title  # Save the event title for the notification
        db.session.delete(event_to_delete)
        db.session.commit()

        # Create notification for event deletion and link to event_id
        notification = Notification(
            action="Deleted",
            message=f"Event '{event_title}' was deleted.",
            event_id=event_id,  # Pass the event_id to associate with this notification
        )
        db.session.add(notification)
        db.session.commit()

        return redirect("/event_calendar")  # Redirect back to the events page
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Route for updating an event
@register_views.route("/update/<int:event_id>", methods=["GET", "POST"])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    old_title = event.title
    old_description = event.description

    if request.method == "POST":
        # Get form data
        event.title = request.form["titre"]
        event.description = request.form["description"]
        event.localisation = request.form["localisation"]
        event.age_requirement = request.form["age_requirement"]
        event.date_event = datetime.strptime(
            request.form["date_event"], "%Y-%m-%dT%H:%M"
        )  # Parse updated date
        event.event_type = request.form["event_type"]

        try:
            db.session.commit()

            # Create notification for event update
            changes = []
            if old_title != event.title:
                changes.append(f"Title changed from '{old_title}' to '{event.title}'")
            if old_description != event.description:
                changes.append(
                    f"Description changed from '{old_description}' to '{event.description}'"
                )

            notification_message = " ; ".join(changes)
            notification = Notification(
                action="Updated",
                message=f"Event '{event.title}' was updated. Changes: {notification_message}",
            )
            db.session.add(notification)
            db.session.commit()

            return redirect("/event_calendar")  # Redirect back to the events page
        except Exception as e:
            return f"An error occurred: {str(e)}"

    return render_template("update.html", event=event)


# Route for displaying notifications
@register_views.route("/notifications")
def notifications():
    notifications = Notification.query.order_by(Notification.timestamp.desc()).all()
    return render_template("notifications.html", notifications=notifications)


# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if not exist
    app.run(debug=True)
