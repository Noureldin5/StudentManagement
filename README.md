# Student Management System

A comprehensive REST API built with Django and Django REST Framework for managing students, teachers, courses, and enrollments with JWT authentication and SQLite/PostgreSQL database.

## 🌟 Features

- **User Authentication**
  - Student and Teacher registration with automatic profile creation
  - JWT token-based authentication (access & refresh tokens)
  - Session-based authentication support
  - Secure password hashing
  - User type detection (student/teacher) on login

- **Student Management**
  - Complete CRUD operations for student records
  - Student profile management with GPA tracking
  - View personal enrollment history
  - Track enrollment request status (pending/approved/rejected/waitlisted)
  - Submit enrollment requests with notes

- **Teacher Management**
  - Teacher profile management with subject specialization
  - Multiple course assignment capability
  - View and manage pending enrollment requests
  - Approve/reject enrollment requests with notes
  - Direct student enrollment (bypass approval process)
  - Grade management and updates
  - View all students enrolled in courses
  - Update course enrollment deadlines
  - Permission-based course access control

- **Course & Enrollment System**
  - Comprehensive course catalog with detailed information
  - Course capacity management (openings tracking)
  - Real-time enrollment count and available spots
  - Enrollment deadline enforcement
  - Automatic waitlist system for full courses
  - Priority-based waitlist processing
  - Student-course enrollment tracking with timestamps
  - Grade assignment and updates
  - View course enrollments and statistics

- **Advanced Features**
  - **Waitlist Management**: Automatic waitlisting when courses are full
  - **Deadline Control**: Course-specific enrollment deadlines
  - **Capacity Tracking**: Real-time monitoring of course capacity
  - **Priority System**: Priority-based enrollment request handling
  - **Auto-enrollment**: Automatic processing from waitlist when spots open
  - **Audit Trail**: Track who enrolled students and when

- **Security**
  - JWT token authentication with configurable expiration
  - Access token: 1 hour lifetime
  - Refresh token: 7 days lifetime with rotation
  - Permission-based access control
  - Teachers can only manage their assigned courses
  - CSRF protection for session-based requests
  - Staff privileges for teachers

## 🛠️ Tech Stack

- **Backend Framework:** Django 5.2+
- **API Framework:** Django REST Framework 3.14+
- **Authentication:** Simple JWT 5.3+
- **Database:** SQLite (default) / PostgreSQL (configurable)
- **ORM:** Django ORM
- **Language:** Python 3.8+
- **Additional Libraries:** psycopg2-binary, python-dotenv, requests

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL 12 or higher (optional - for production use; SQLite is included by default)

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

4. **Configure Database (Optional)**
   
   **Option A: Use SQLite (Default - No Configuration Needed)**
   - The project uses SQLite by default (`db.sqlite3`)
   - No additional setup required
   - Perfect for development and testing
   
   **Option B: Use PostgreSQL (Recommended for Production)**
   - Create a database named `StudentSystem`
   - Update database credentials in `StudentManagementSystem/settings.py`:
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
| GET | `/` | API home with all available endpoints |
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
| GET | `/students/<id>/` | Get student details |
| POST | `/students/add/` | Add a new student |
| PUT | `/students/<id>/update/` | Update student details |
| DELETE | `/students/<id>/delete/` | Delete a student |

### Course Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/courses/` | List all courses with enrollment counts |
| GET | `/courses/<id>/` | Get course details with teachers |
| GET | `/courses/<id>/openings/` | Get available course openings |
| GET | `/courses/<id>/enrollments/` | Get all enrollments for a course |

### Enrollment Endpoints (Student)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/enrollment/request/` | Student requests course enrollment |
| GET | `/students/<id>/enrollments/` | View student's enrollments |
| GET | `/students/<id>/requests/` | View student's enrollment requests |

### Teacher Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/teachers/` | List all teachers |
| GET | `/teachers/<teacher_id>/` | Get teacher details |
| GET | `/teachers/<teacher_id>/courses/` | Get teacher's assigned courses |
| GET | `/teachers/<teacher_id>/requests/` | View pending enrollment requests |
| POST | `/teachers/request/<request_id>/approve/` | Approve enrollment request |
| POST | `/teachers/request/<request_id>/reject/` | Reject enrollment request |
| POST | `/teachers/enroll/` | Directly enroll a student in a course |
| GET | `/teachers/<teacher_id>/courses/<course_id>/students/` | View students in a specific course |
| PUT | `/teachers/enrollment/<enrollment_id>/grade/` | Update student grade |
| PUT | `/teachers/<course_id>/deadline/` | Update course enrollment deadline |

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

**Response:**
```json
{
  "message": "Student registered successfully",
  "student_id": 1,
  "user_id": 1,
  "username": "john_doe"
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

**Response:**
```json
{
  "message": "Teacher registered successfully",
  "teacher_id": 1,
  "user_id": 2,
  "username": "prof_smith"
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

**Response (Success):**
```json
{
  "message": "Enrollment request submitted successfully",
  "request_id": 1,
  "status": "pending",
  "deadline": "2025-12-31T23:59:59Z"
}
```

**Response (Course Full - Waitlisted):**
```json
{
  "message": "Enrollment request submitted successfully",
  "request_id": 1,
  "status": "waitlisted",
  "deadline": "2025-12-31T23:59:59Z"
}
```

### Approve Enrollment Request

```bash
POST /teachers/request/1/approve/
Content-Type: application/json

{
  "teacher_id": 1
}
```

**Response:**
```json
{
  "message": "Enrollment request approved successfully",
  "enrollment_id": 1,
  "student": "John Doe",
  "course": "Introduction to Programming"
}
```

### Update Course Enrollment Deadline

```bash
PUT /teachers/1/deadline/
Content-Type: application/json

{
  "teacher_id": 1,
  "enrollment_deadline": "2025-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "message": "Enrollment deadline updated successfully",
  "course": "Introduction to Programming",
  "old_deadline": "2025-12-15T23:59:59Z",
  "new_deadline": "2025-12-31T23:59:59Z",
  "updated_by": "Jane Smith"
}
```

### Update Student Grade

```bash
PUT /teachers/enrollment/1/grade/
Content-Type: application/json

{
  "teacher_id": 1,
  "grade": "A"
}
```

**Response:**
```json
{
  "message": "Grade updated successfully",
  "student": "John Doe",
  "course": "Introduction to Programming",
  "old_grade": null,
  "new_grade": "A"
}
```

### View Course Students

```bash
GET /teachers/1/courses/1/students/
```

**Response:**
```json
{
  "course": {
    "id": 1,
    "name": "Introduction to Programming",
    "code": "CS101"
  },
  "total_students": 15,
  "students": [
    {
      "id": 1,
      "student__id": 1,
      "student__first_name": "John",
      "student__last_name": "Doe",
      "student__age": 20,
      "student__gpa": 3.5,
      "enrollment_date": "2025-01-15T10:30:00Z",
      "grade": "A",
      "enrolled_by__first_name": "Jane",
      "enrolled_by__last_name": "Smith"
    }
  ]
}
```

## 🗃️ Database Schema

### Models

- **User** - Django's built-in user model for authentication
  - Fields: username, email, password, is_staff
  
- **Student** - Student profile with personal information and GPA
  - Fields: user (OneToOne), first_name, last_name, age, gpa, created_at
  - Relationships: enrolled_courses (ManyToMany through Enrollment)
  
- **Teacher** - Teacher profile with subject specialization
  - Fields: user (OneToOne), first_name, last_name, subject, created_at
  - Relationships: courses (ManyToMany)
  
- **Course** - Course information including capacity and deadlines
  - Fields: name, code, description, credits, openings, enrollment_deadline, created_at
  - Properties: enrolled_students, available_spots, is_full, is_enrollment_open
  
- **Enrollment** - Links students to courses with grades
  - Fields: student (FK), course (FK), enrolled_by (FK to Teacher), enrollment_date, enrollment_deadline, grade
  - Constraints: unique_together=['student', 'course']
  
- **EnrollmentRequest** - Tracks enrollment requests with approval status
  - Fields: student (FK), course (FK), status, requested_at, reviewed_by (FK to Teacher), reviewed_at, enrollment_deadline, notes, priority
  - Status Choices: pending, approved, rejected, waitlisted
  - Constraints: unique_together=['student', 'course']

### Relationships

- **One-to-One**: User ↔ Student, User ↔ Teacher
- **Many-to-Many**: Teacher ↔ Course, Student ↔ Course (via Enrollment)
- **Foreign Keys**: 
  - EnrollmentRequest → Student, Course, Teacher (reviewed_by)
  - Enrollment → Student, Course, Teacher (enrolled_by)

### Key Features in Schema

- **Capacity Management**: Course model tracks openings and calculates available spots
- **Waitlist System**: EnrollmentRequest status can be 'waitlisted' when course is full
- **Deadline Tracking**: Both Course and EnrollmentRequest track enrollment deadlines
- **Priority Queue**: EnrollmentRequest has priority field for waitlist ordering
- **Audit Trail**: Enrollment tracks who enrolled the student and when
- **Validation**: Models include clean() methods to enforce business rules

## 🎯 Business Logic & Key Features

### Enrollment Request Flow

1. **Student Submits Request**
   - Student submits enrollment request with optional notes
   - System checks if deadline has passed - rejects if expired
   - System checks if already enrolled - prevents duplicates
   - System checks if request already exists - prevents re-submission

2. **Automatic Waitlist Management**
   - If course has available spots: status = 'pending'
   - If course is full: status = 'waitlisted'
   - Waitlisted requests tracked with priority (FIFO by default)

3. **Teacher Review**
   - Teacher can approve, reject, or waitlist requests
   - Only teachers assigned to the course can manage requests
   - System validates course capacity before approval
   - Automatically enrolls student upon approval if spots available

4. **Automatic Processing from Waitlist**
   - When a spot opens (student drops/withdrawn), system automatically:
     - Finds highest priority waitlisted request
     - Approves and enrolls that student
     - Updates all related records

### Enrollment Deadline Management

- **Course-Level Deadlines**: Each course can have its own enrollment deadline
- **Request Tracking**: Each enrollment request stores the deadline at time of request
- **Deadline Enforcement**:
  - Students cannot submit requests after deadline
  - Teachers can update deadlines (with audit trail)
  - System validates deadlines before processing requests
- **Flexible Updates**: Teachers can extend or modify deadlines as needed

### Course Capacity Management

- **Real-Time Tracking**: System maintains accurate count of enrolled students
- **Available Spots Calculation**: `available_spots = openings - enrolled_students`
- **Full Course Detection**: Course marked as full when `available_spots <= 0`
- **Capacity Validation**: 
  - Prevents over-enrollment beyond capacity
  - Automatically waitlists when full
  - Validates capacity on all enrollment operations

### Grade Management

- **Flexible Grading**: Teachers can assign/update grades for enrolled students
- **Grade Options**: Support for standard letter grades (A, B, C, D, F)
- **Permission Control**: Only assigned teachers can update grades
- **Audit Trail**: Grade changes tracked with timestamp and teacher info

### Direct Enrollment (Teacher Initiated)

- **Bypass Approval**: Teachers can directly enroll students without request
- **Capacity Override**: Can enroll even when course appears full (with validation)
- **Immediate Enrollment**: Creates enrollment record instantly
- **Permission Required**: Only teachers assigned to course can direct enroll

### Security & Permissions

- **Role-Based Access**:
  - Students: Can view courses, submit requests, view their enrollments
  - Teachers: Can manage courses they're assigned to, approve/reject requests, update grades
  - Staff: Full access via Django admin

- **Course Access Control**:
  - Teachers can only manage requests for courses they teach
  - Validation ensures teachers can't modify other teachers' courses

- **Data Validation**:
  - Duplicate enrollment prevention
  - Capacity enforcement
  - Deadline validation
  - GPA range validation (0.0 - 4.0)
  - Age validation

## 🧪 Testing

### Automated Testing

Run the included test script to validate all API endpoints:

```bash
python test_api.py
```

This script tests:
- Student registration and authentication
- Course listing and details
- Enrollment request workflow
- Teacher approval/rejection
- Grade management
- Deadline enforcement

### Manual Testing Options

**1. Django Admin Panel**
- URL: `http://127.0.0.1:8000/admin/`
- Login with superuser credentials
- Full CRUD operations for all models
- View relationships and data integrity
- Bulk actions and filtering

**2. API Clients (Postman/Insomnia)**
- Import endpoints from documentation
- Test authentication flow
- Validate request/response formats
- Save test collections

**3. Browser (for GET requests)**
- Visit `http://127.0.0.1:8000/` for API home
- Navigate to any GET endpoint directly
- View JSON responses in browser

### Unit Tests

Run Django's built-in test framework:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test students
python manage.py test teachers
python manage.py test courses

# Run with verbose output
python manage.py test --verbosity 2
```

## 👨‍💼 Admin Panel Features

Access the Django admin panel at `/admin/` with superuser credentials.

### Available Models

- **Users**: Manage all user accounts
- **Students**: View/edit student profiles and GPA
- **Teachers**: Manage teacher profiles and subject assignments
- **Courses**: CRUD operations for courses, set capacity and deadlines
- **Enrollments**: View all student-course enrollments with grades
- **Enrollment Requests**: Monitor and manage all enrollment requests

### Admin Capabilities

- **Bulk Actions**: Approve/reject multiple enrollment requests at once
- **Filtering**: Filter by status, date, course, student
- **Search**: Search students, teachers, courses by name/code
- **Inline Editing**: Edit related objects on same page
- **Audit Trail**: View created/updated timestamps
- **Data Export**: Export data to CSV/JSON

### Creating a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account with full access.

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
3. Set up environment variables for sensitive data using python-dotenv
4. Use a production-grade WSGI server (Gunicorn, uWSGI)
5. Set up a reverse proxy (Nginx, Apache)
6. Use a production PostgreSQL server instead of SQLite
7. Enable HTTPS/SSL
8. Configure proper logging
9. Set up database backups
10. Use Redis for caching (optional)

## 🔍 Common Use Cases

### For Students

1. **Register an Account**
   - POST to `/auth/register/student/` with your details
   - Login to receive JWT tokens

2. **Browse Courses**
   - GET `/courses/` to see all available courses
   - GET `/courses/<id>/` for detailed course information

3. **Request Enrollment**
   - POST to `/enrollment/request/` with student_id and course_id
   - Check deadline before requesting

4. **Track Your Requests**
   - GET `/students/<id>/requests/` to see all your enrollment requests
   - Monitor status: pending, approved, rejected, or waitlisted

5. **View Your Enrollments**
   - GET `/students/<id>/enrollments/` to see courses you're enrolled in
   - Check your grades

### For Teachers

1. **Register as Teacher**
   - POST to `/auth/register/teacher/` with your credentials
   - System automatically grants staff privileges

2. **View Assigned Courses**
   - GET `/teachers/<id>/courses/` to see your courses

3. **Manage Enrollment Requests**
   - GET `/teachers/<id>/requests/` to view pending requests
   - POST to `/teachers/request/<id>/approve/` to approve
   - POST to `/teachers/request/<id>/reject/` to reject

4. **Direct Enrollment**
   - POST to `/teachers/enroll/` to directly enroll a student
   - Useful for special cases or administrative enrollments

5. **Update Grades**
   - PUT to `/teachers/enrollment/<id>/grade/` with new grade
   - Track student performance

6. **Manage Deadlines**
   - PUT to `/teachers/<course_id>/deadline/` to update enrollment deadline
   - Extend deadlines as needed

## 🛠️ Troubleshooting

### Common Issues

**Issue: "Enrollment request deadline has passed"**
- Solution: Teacher needs to extend the deadline using the update deadline endpoint
- Or: Student must wait for next enrollment period

**Issue: "Course is full" / Request automatically waitlisted**
- Solution: Student is automatically added to waitlist
- When spot opens, highest priority waitlisted student is auto-enrolled

**Issue: "Already enrolled in this course"**
- Solution: Student cannot request enrollment in a course they're already in
- Check enrollments using `/students/<id>/enrollments/`

**Issue: "Permission denied" when approving requests**
- Solution: Ensure the teacher is assigned to the course
- Only assigned teachers can manage course enrollment requests

**Issue: JWT token expired**
- Solution: Use refresh token to get new access token
- POST to `/auth/token/refresh/` with refresh token

**Issue: Database migration errors**
- Solution: Run `python manage.py makemigrations` then `python manage.py migrate`
- For fresh start: Delete `db.sqlite3` and run migrations again

### Database Reset

To reset the database completely:

```bash
# Windows PowerShell
Remove-Item db.sqlite3
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

```bash
# Unix/Linux/Mac
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 📊 API Response Codes

- **200 OK**: Successful GET/PUT request
- **201 Created**: Successful POST request (resource created)
- **400 Bad Request**: Invalid data or business logic violation
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Authenticated but not authorized for this action
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server-side error

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

