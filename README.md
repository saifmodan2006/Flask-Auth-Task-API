# Flask Auth Task API

A comprehensive REST API built with Flask that provides user authentication and task management features with JWT token-based security.

## Features

- **User Authentication**
  - User registration with profile image upload
  - User login with JWT token generation
  - Secure password hashing using PBKDF2

- **Password Management**
  - Forgot password functionality with token generation
  - Reset password with time-limited tokens (15 minutes)

- **Task Management**
  - Create tasks with title and description
  - List all tasks
  - Update existing tasks
  - Delete tasks
  - Task ownership and user-specific task tracking

- **Security**
  - JWT token-based authentication
  - Token expiration (1 hour)
  - Password hashing with PBKDF2
  - Secure token generation using secrets module

## Tech Stack

- **Framework**: Flask
- **API**: Flask-RESTful
- **Database**: SQLAlchemy with SQLite
- **Authentication**: PyJWT
- **Password Hashing**: Passlib
- **Frontend**: HTML/Jinja2 Templates

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/saifmodan2006/Flask-Auth-Task-API.git
   cd Flask-Auth-Task-API
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv working
   ```

3. **Activate the virtual environment**
   
   On Windows:
   ```bash
   working\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source working/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The app is configured with the following settings in `app.py`:

```python
app.config["SECRET_KEY"] = "Millionaire"  # Change this in production
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Task.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/"
```

## Running the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

## API Endpoints

### User Management

#### Register
- **Endpoint**: `POST /register`
- **Form Data**:
  - `username` (required)
  - `email` (required)
  - `password` (required)
  - `image` (optional) - Profile image file
- **Response**: User object with JWT token

#### Login
- **Endpoint**: `POST /login`
- **Form/Query Data**:
  - `username` (required)
  - `password` (required)
- **Response**: JWT token

### Password Management

#### Forgot Password
- **Endpoint**: `POST /forgot-password`
- **Form Data**:
  - `email` (required)
- **Response**: Password reset link with token

#### Reset Password
- **Endpoint**: `POST /reset-password/<token>`
- **Form Data**:
  - `password` (required)
- **Response**: Success message

### Task Management

#### Add Task
- **Endpoint**: `POST /add-task`
- **Headers**: `Authorization: Bearer <token>`
- **JSON Data**:
  - `title` (required)
  - `description` (optional)
- **Response**: Task created confirmation

#### Get Task List
- **Endpoint**: `GET /task-list`
- **Response**: List of all tasks

#### Update Task
- **Endpoint**: `PUT /update-task/<task_id>`
- **Headers**: `Authorization: Bearer <token>`
- **JSON Data**:
  - `title` (optional)
  - `description` (optional)
- **Response**: Updated task object

#### Delete Task
- **Endpoint**: `DELETE /delete-task/<task_id>`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: Deletion confirmation

### Frontend Routes

- `GET /` - Register page
- `GET /login-page` - Login page
- `GET /forgot` - Forgot password page
- `GET /reset/<token>` - Reset password page

## Project Structure

```
.
├── app.py              # Main Flask application
├── models.py           # Database models (User, Task)
├── resources.py        # API resource classes
├── requirements.txt    # Python dependencies
├── static/             # Static files (images, etc.)
├── templates/          # HTML templates
│   ├── register.html
│   ├── login.html
│   ├── forgot.html
│   └── reset.html
└── working/            # Virtual environment (excluded from git)
```

## Database Models

### User Model
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email
- `password_hash` - Hashed password
- `profile_image` - Profile image filename
- `reset_token` - Password reset token
- `token_expiry` - Token expiration timestamp

### Task Model
- `id` - Primary key
- `title` - Task title
- `description` - Task description
- `user_id` - Foreign key to User

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. Register or login to get a token
2. Include the token in the Authorization header:
   ```
   Authorization: Bearer <your_token_here>
   ```

## Security Notes

- Change the `SECRET_KEY` in production
- Use HTTPS in production
- Implement rate limiting in production
- Use environment variables for sensitive configuration

## Dependencies

- Flask - Web framework
- Flask-RESTful - REST API extension
- Flask-SQLAlchemy - ORM for database
- PyJWT - JWT token handling
- Passlib - Password hashing
- Werkzeug - WSGI utilities

## Future Enhancements

- Email verification for new accounts
- Two-factor authentication
- Task categories/tags
- Task priorities and due dates
- User profile management
- Admin dashboard

## License

This project is open source and available under the MIT License.

## Author

Sahil Modan

## Contact

For more information, visit: https://github.com/saifmodan2006