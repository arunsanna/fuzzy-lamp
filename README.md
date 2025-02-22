# Fuzzy Lamp

Fuzzy Lamp is a simple Flask web application that allows users to sign up and provides an admin panel to view all signups. The application uses SQLAlchemy for database interactions and supports PostgreSQL as the database backend.

## Features

- User signup with first name, last name, and email.
- Admin login to view all signups.
- In-memory SQLite database for testing.
- Docker support for easy deployment.

## Requirements

- Python 3.9
- Flask 2.0.3
- Flask-SQLAlchemy 2.5.1
- psycopg2-binary 2.9.3
- pytest 7.1.2
- Werkzeug 2.0.3
- SQLAlchemy 1.4.47
- Docker
- Docker Compose

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/fuzzy-lamp.git
    cd fuzzy-lamp
    ```

2. Create a virtual environment and activate it:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Application

1. Start the application using Docker Compose:
    ```sh
    docker-compose up --build
    ```

2. The application will be available at `http://localhost:5001`.

## Running Tests

1. To run the tests, use the following command:
    ```sh
    pytest
    ```

## Project Structure

```plaintext
project/
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration for the web app
├── docker-compose.yml       # Docker Compose file to run the app and PostgreSQL
├── templates/               # HTML templates
│   ├── signup.html          # Signup page (with success messages)
│   ├── admin.html           # Admin panel to list signups
│   └── login.html           # Admin login page
├── tests/                   # Pytest test cases
│   └── test_app.py
└── .devcontainer/           # VS Code dev container configuration
    └── devcontainer.json
```


## License

This project is licensed under the MIT License. See the [LICENSE](http://_vscodecontentref_/1) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## Contact

For any questions or inquiries, please contact [Mr.A](mailto:arun.sanna@outlook.com).