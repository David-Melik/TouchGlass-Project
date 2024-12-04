from app import create_app
from app.helpers import create_database

# Create the Flask app instance
app = create_app()

# Pass the app instance to the create_database function
create_database(app)


if __name__ == "__main__":
    app.run(debug=True)
