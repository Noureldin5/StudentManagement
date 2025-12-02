from django.test import TestCase


import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("STUDENT MANAGEMENT SYSTEM - API TEST")
print("=" * 60)

def print_response(test_name, response):
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print("=" * 60)

# Test 1: Home Page
print("\n\n1️⃣ Testing Home Page...")
response = requests.get(f"{BASE_URL}/")
print_response("Home Page", response)

# Test 2: Register Student
print("\n\n2️⃣ Testing Student Registration...")
student_data = {
    "username": "alice_student",
    "email": "alice@example.com",
    "password": "StudentPass123",
    "first_name": "Alice",
    "last_name": "Johnson",
    "age": 21,
    "gpa": 3.8
}
response = requests.post(f"{BASE_URL}/auth/register/student/", json=student_data)
print_response("Register Student", response)
if response.status_code == 201:
    student_id = response.json().get('student_id')
    print(f"✅ Student created with ID: {student_id}")

# Test 3: Register Teacher
print("\n\n3️⃣ Testing Teacher Registration...")
teacher_data = {
    "username": "prof_williams",
    "email": "williams@example.com",
    "password": "TeacherPass123",
    "first_name": "Robert",
    "last_name": "Williams",
    "subject": "Mathematics"
}
response = requests.post(f"{BASE_URL}/auth/register/teacher/", json=teacher_data)
print_response("Register Teacher", response)
if response.status_code == 201:
    teacher_id = response.json().get('teacher_id')
    print(f"✅ Teacher created with ID: {teacher_id}")

# Test 4: Get JWT Token (Login)
print("\n\n4️⃣ Testing JWT Token Login...")
login_data = {
    "username": "alice_student",
    "password": "StudentPass123"
}
response = requests.post(f"{BASE_URL}/auth/token/", json=login_data)
print_response("Get JWT Token", response)
if response.status_code == 200:
    access_token = response.json().get('access')
    refresh_token = response.json().get('refresh')
    print(f"✅ Access Token: {access_token[:50]}...")
    print(f"✅ Refresh Token: {refresh_token[:50]}...")

    # Save token for later use
    headers = {"Authorization": f"Bearer {access_token}"}
else:
    headers = {}

# Test 5: Traditional Login
print("\n\n5️⃣ Testing Traditional Login...")
response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
print_response("Traditional Login", response)

# Test 6: Get All Students
print("\n\n6️⃣ Testing Get All Students...")
response = requests.get(f"{BASE_URL}/students/")
print_response("Get All Students", response)

# Test 7: Get All Courses
print("\n\n7️⃣ Testing Get All Courses...")
response = requests.get(f"{BASE_URL}/courses/")
print_response("Get All Courses", response)

# If there are courses and students, test enrollment
print("\n\n8️⃣ Testing Enrollment Request...")
enrollment_request_data = {
    "student_id": 1,  # Change this based on your data
    "course_id": 1,   # Change this based on your data
    "notes": "Very interested in this course"
}
response = requests.post(f"{BASE_URL}/enrollment/request/", json=enrollment_request_data)
print_response("Student Request Enrollment", response)

# Test 9: Teacher Views Pending Requests
print("\n\n9️⃣ Testing Teacher View Pending Requests...")
response = requests.get(f"{BASE_URL}/teacher/requests/1/")  # teacher_id = 1
print_response("Teacher Pending Requests", response)

# Test 10: Refresh Token
print("\n\n🔟 Testing Token Refresh...")
if 'refresh_token' in locals():
    refresh_data = {"refresh": refresh_token}
    response = requests.post(f"{BASE_URL}/auth/token/refresh/", json=refresh_data)
    print_response("Refresh Token", response)

print("\n\n" + "=" * 60)
print("✅ API TESTING COMPLETED!")
print("=" * 60)
print("\nNOTE: Some tests may fail if:")
print("- Database is empty (no courses/students)")
print("- Teacher doesn't have courses assigned")
print("- Student/Course IDs don't exist")
print("\nUse Django Admin to add Courses and assign them to Teachers!")
print("Admin URL: http://127.0.0.1:8000/admin/")
print("=" * 60)

