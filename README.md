# Student Management System

A comprehensive REST API built with Django and Django REST Framework for managing students, teachers, courses, and enrollments with JWT authentication and PostgreSQL database.

## 🌟 Features

- **User Authentication**
  - Student and Teacher registration
  - JWT token-based authentication
  - Session-based authentication support
  - Secure password hashing

- **Student Management**
  - CRUD operations for student records
  - Student profile management
  - Course enrollment requests

- **Teacher Management**
  - Teacher profile management
  - Course assignment
  - Student enrollment approval/rejection
  - Grade management
  - Direct student enrollment capability

- **Course & Enrollment System**
  - Course catalog management
  - Enrollment request workflow
  - Student-course enrollment tracking
  - Grade assignment and updates

- **Security**
  - JWT token authentication with expiration
  - Permission-based access control
  - Teachers can only manage their assigned courses
  - CSRF protection

## 🛠️ Tech Stack

- **Backend Framework:** Django 5.2+
- **API Framework:** Django REST Framework 3.14+
- **Authentication:** Simple JWT 5.3+
- **Database:** PostgreSQL 
- **ORM:** Django ORM
- **Language:** Python 3.x

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd StudentManagementSystem
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure PostgreSQL**
   - Create a database named `StudentSystem`
   - Update database credentials in `StudentManagementSystem/settings.py` if needed:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql',
             'NAME': 'StudentSystem',
             'USER': 'postgres',
             'PASSWORD': 'your_password',
             'HOST': 'localhost',
             'PORT': '5432',
         }
     }
     ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/`

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/student/` | Register a new student |
| POST | `/auth/register/teacher/` | Register a new teacher |
| POST | `/auth/token/` | Obtain JWT token (login) |
| POST | `/auth/token/refresh/` | Refresh JWT token |
| POST | `/auth/login/` | Session-based login |
| POST | `/auth/logout/` | Logout |

### Student Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/students/` | List all students |
| POST | `/students/add/` | Add a new student |
| PUT | `/students/update/<id>/` | Update student details |
| DELETE | `/students/delete/<id>/` | Delete a student |

### Course Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/courses/` | List all courses |

### Enrollment Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/enrollment/request/` | Student requests course enrollment |

### Teacher Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/teacher/requests/<teacher_id>/` | View pending enrollment requests |
| POST | `/teacher/request/<request_id>/approve/` | Approve enrollment request |
| POST | `/teacher/request/<request_id>/reject/` | Reject enrollment request |
| POST | `/teacher/enroll/` | Directly enroll a student in a course |
| GET | `/teacher/<teacher_id>/course/<course_id>/students/` | View students in a specific course |
| PUT | `/teacher/enrollment/<enrollment_id>/grade/` | Update student grade |

### Admin Panel

| Endpoint | Description |
|----------|-------------|
| `/admin/` | Django admin interface |

## 🔐 Authentication

This API uses JWT (JSON Web Token) for authentication.

### Getting a Token

```bash
POST /auth/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using the Token

Include the access token in the Authorization header:

```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Token Lifetimes:**
- Access Token: 1 hour
- Refresh Token: 7 days

## 📝 Example API Calls

### Register a Student

```bash
POST /auth/register/student/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "age": 20,
  "gpa": 3.5
}
```

### Register a Teacher

```bash
POST /auth/register/teacher/
Content-Type: application/json

{
  "username": "prof_smith",
  "email": "smith@example.com",
  "password": "TeacherPass123",
  "first_name": "Jane",
  "last_name": "Smith",
  "subject": "Computer Science"
}
```

### Request Course Enrollment

```bash
POST /enrollment/request/
Content-Type: application/json

{
  "student_id": 1,
  "course_id": 1,
  "notes": "I am very interested in this course"
}
```

### Approve Enrollment Request

```bash
POST /teacher/request/1/approve/
Content-Type: application/json

{
  "teacher_id": 1
}
```

### Update Student Grade

```bash
PUT /teacher/enrollment/1/grade/
Content-Type: application/json

{
  "teacher_id": 1,
  "grade": "A"
}
```

## 🗃️ Database Schema

### Models

- **User** - Django's built-in user model for authentication
- **Student** - Student profile with personal information and GPA
- **Teacher** - Teacher profile with subject specialization
- **Course** - Course information including code, name, credits
- **Enrollment** - Links students to courses with grades
- **EnrollmentRequest** - Tracks enrollment requests with approval status

### Relationships

- One-to-One: User ↔ Student, User ↔ Teacher
- Many-to-Many: Teacher ↔ Course
- Many-to-Many (Through): Student ↔ Course (via Enrollment)
- Foreign Keys: EnrollmentRequest → Student, Course, Teacher

## 🧪 Testing

Run the automated test script:

```bash
python test_api.py
```

Or test manually using:
- **Browser:** Visit `http://127.0.0.1:8000/`
- **Postman/Insomnia:** Import and test API endpoints
- **Admin Panel:** `http://127.0.0.1:8000/admin/`

## 📂 Project Structure

```
StudentManagementSystem/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── StudentManagementSystem/
│   ├── __init__.py
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── students/
│   ├── __init__.py
│   ├── models.py            # Database models
│   ├── views.py             # API views/logic
│   ├── serializers.py       # Data serialization
│   ├── urls.py              # App URL routing
│   ├── admin.py             # Admin configuration
│   └── migrations/          # Database migrations
├── templates/
└── Documentation/
    ├── COMPLETE_GUIDE.md    # Detailed documentation
    ├── QUICK_START.md       # Quick start guide
    ├── ARCHITECTURE.md      # System architecture
    └── test_api.py          # Test script
```

## 🔧 Configuration

### JWT Settings

Edit `StudentManagementSystem/settings.py`:

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### Database Settings

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'StudentSystem',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🚀 Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Set up environment variables for sensitive data
4. Use a production-grade WSGI server (Gunicorn, uWSGI)
5. Set up a reverse proxy (Nginx, Apache)
6. Use a production PostgreSQL server
7. Enable HTTPS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Django Documentation
- Django REST Framework
- Simple JWT
- PostgreSQL Community

## 📞 Support

For support, email your-email@example.com or open an issue in the repository.

---

**Built with ❤️ using Django and Django REST Framework**

