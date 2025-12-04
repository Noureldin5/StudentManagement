# python
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json
from . import views as teacher_views
from teachers import views as teacher_views
from teachers.models import Teacher
from courses.models import Course
from students.models import Student, Enrollment, EnrollmentRequest


class TeacherViewsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Users
        self.user_teacher = User.objects.create_user(username='t1', email='t1@example.com', password='pass')
        self.user_teacher2 = User.objects.create_user(username='t2', email='t2@example.com', password='pass')
        self.user_student = User.objects.create_user(username='s1', email='s1@example.com', password='pass')

        # Teacher objects
        self.teacher = Teacher.objects.create(user=self.user_teacher, first_name='Alice', last_name='T', subject='Math')
        self.teacher2 = Teacher.objects.create(user=self.user_teacher2, first_name='Bob', last_name='T', subject='Physics')

        # Student
        self.student = Student.objects.create(user=self.user_student, first_name='Stu', last_name='Dent', age=20, gpa=3.5)

        # Courses
        # create a course with openings=1 for "full" tests
        self.course = Course.objects.create(name='Algebra', code='M101', credits=3, openings=2)
        self.course_full = Course.objects.create(name='Optics', code='P201', credits=3, openings=1)

        # assign courses to teacher
        self.teacher.courses.add(self.course)
        self.teacher.courses.add(self.course_full)
        # teacher2 has no access to course_full (for permission tests)
        self.teacher2.courses.add(self.course)

        # Make one enrollment in course_full to make it full
        Enrollment.objects.create(student=self.student, course=self.course_full, enrolled_by=self.teacher)

        # EnrollmentRequest - pending for course
        self.enroll_req = EnrollmentRequest.objects.create(
            student=self.student,
            course=self.course,
            status='pending',
            requested_at=timezone.now(),
            notes='Please accept'
        )

    def _json_response(self, response):
        return json.loads(response.content.decode())

    def test_teacher_list_and_detail(self):
        req = self.factory.get('/teachers/')
        resp = teacher_views.teacher_list(req)
        assert resp.status_code == 200
        data = self._json_response(resp)
        assert any(t['user__username'] == 't1' for t in data)

        req = self.factory.get('/teachers/detail/')
        resp = teacher_views.teacher_detail(req, self.teacher.id)
        assert resp.status_code == 200
        d = self._json_response(resp)
        assert d['first_name'] == 'Alice'
        assert 'courses' in d

    def test_pending_requests(self):
        req = self.factory.get('/teachers/pending/')
        resp = teacher_views.pending_requests(req, self.teacher.id)
        assert resp.status_code == 200
        data = self._json_response(resp)
        assert any(r['student__id'] == self.student.id for r in data)

    def test_approve_request_permission_and_full_checks(self):
        # Permission check: teacher2 tries to approve request for course teacher1 teaches -> should be 403
        # create a new student for this test
        new_student_user = User.objects.create_user(username='s_temp', email='s_temp@example.com', password='pass')
        new_student = Student.objects.create(user=new_student_user, first_name='Temp', last_name='Student', age=20, gpa=3.5)

        # create a request for course_full (which teacher2 does not teach)
        # Note: When created, this will be auto-waitlisted because course_full is full
        req_for_full = EnrollmentRequest.objects.create(
            student=new_student, course=self.course_full, status='pending', requested_at=timezone.now()
        )

        # Change it back to pending to test permission check
        req_for_full.status = 'pending'
        req_for_full.save(update_fields=['status'])

        body = json.dumps({'teacher_id': self.teacher2.id})
        req = self.factory.post('/teachers/approve/{}/'.format(req_for_full.id), data=body, content_type='application/json')
        resp = teacher_views.approve_request(req, req_for_full.id)
        assert resp.status_code == 403
        data = self._json_response(resp)
        assert 'permission' in data.get('error', '').lower()

        # Full course check: teacher tries to approve a request for a course that is full -> 400
        # The course_full already has 1 enrollment (self.student), so it's full (openings=1)
        # req_for_full still exists and the teacher has permission, so approve it and it should fail because course is full
        body = json.dumps({'teacher_id': self.teacher.id})
        req = self.factory.post('/teachers/approve/{}/'.format(req_for_full.id), data=body, content_type='application/json')
        resp = teacher_views.approve_request(req, req_for_full.id)
        assert resp.status_code == 400
        data = self._json_response(resp)
        assert 'full' in data.get('error', '').lower()

        # Approve successfully for non-full course
        # Create a new student and request to avoid conflicts
        student_for_approval = Student.objects.create(
            user=User.objects.create_user(username='s_approve', email='s_approve@example.com', password='pass'),
            first_name='Approve', last_name='Student', age=21, gpa=3.2
        )

        req_to_approve = EnrollmentRequest.objects.create(
            student=student_for_approval, course=self.course, status='pending', requested_at=timezone.now()
        )

        body = json.dumps({'teacher_id': self.teacher.id})
        req = self.factory.post('/teachers/approve/{}/'.format(req_to_approve.id), data=body, content_type='application/json')
        resp = teacher_views.approve_request(req, req_to_approve.id)
        assert resp.status_code == 200
        data = self._json_response(resp)
        assert 'enrollment_id' in data

    def test_reject_request(self):
        # create a new student and pending request and reject it
        new_student_user = User.objects.create_user(username='s_reject', email='s_reject@example.com', password='pass')
        new_student = Student.objects.create(user=new_student_user, first_name='Reject', last_name='Test', age=20, gpa=3.5)
        r = EnrollmentRequest.objects.create(student=new_student, course=self.course, status='pending', requested_at=timezone.now())
        body = json.dumps({'teacher_id': self.teacher.id, 'notes': 'not eligible'})
        req = self.factory.post('/teachers/reject/{}/'.format(r.id), data=body, content_type='application/json')
        resp = teacher_views.reject_request(req, r.id)
        assert resp.status_code == 200
        data = self._json_response(resp)
        assert data['notes'] == 'not eligible'
        r.refresh_from_db()
        assert r.status == 'rejected'
        assert r.reviewed_by == self.teacher

    def test_direct_enroll(self):
        # permission: teacher2 doesn't teach course_full -> 403 when trying to enroll someone into course_full via teacher2
        body = json.dumps({'teacher_id': self.teacher2.id, 'student_id': self.student.id, 'course_id': self.course_full.id})
        req = self.factory.post('/teachers/direct_enroll/', data=body, content_type='application/json')
        resp = teacher_views.direct_enroll(req)
        assert resp.status_code == 403

        # course full: teacher tries to direct enroll into full course -> 400
        body = json.dumps({'teacher_id': self.teacher.id, 'student_id': self.student.id, 'course_id': self.course_full.id})
        req = self.factory.post('/teachers/direct_enroll/', data=body, content_type='application/json')
        resp = teacher_views.direct_enroll(req)
        assert resp.status_code == 400

        # enroll into non-full course
        new_student_user = User.objects.create_user(username='s2', email='s2@example.com', password='pass')
        new_student = Student.objects.create(user=new_student_user, first_name='New', last_name='Stu', age=21, gpa=3.2)
        body = json.dumps({'teacher_id': self.teacher.id, 'student_id': new_student.id, 'course_id': self.course.id})
        req = self.factory.post('/teachers/direct_enroll/', data=body, content_type='application/json')
        resp = teacher_views.direct_enroll(req)
        assert resp.status_code == 201
        data = self._json_response(resp)
        assert 'enrollment_id' in data

        # enrolling same student again should return error 400
        req = self.factory.post('/teachers/direct_enroll/', data=body, content_type='application/json')
        resp = teacher_views.direct_enroll(req)
        assert resp.status_code == 400

    def test_course_students_and_my_courses(self):
        # ensure course_students returns list and permission enforced
        # teacher2 tries to access course_full which they don't own -> 403 (teacher2 doesn't have course_full)
        req = self.factory.get('/teachers/course_students/')
        resp = teacher_views.course_students(req, self.teacher2.id, self.course_full.id)
        assert resp.status_code == 403

        # teacher accesses their course
        req = self.factory.get('/teachers/course_students/')
        resp = teacher_views.course_students(req, self.teacher.id, self.course.id)
        assert resp.status_code == 200
        data = self._json_response(resp)
        assert 'students' in data

        # my_courses
        req = self.factory.get('/teachers/my_courses/')
        resp = teacher_views.my_courses(req, self.teacher.id)
        assert resp.status_code == 200
        data = self._json_response(resp)
        assert 'courses' in data
        assert any(c['id'] == self.course.id for c in data['courses'])

    def test_update_enrollment_deadline(self):
        # only teacher with permission can update
        new_deadline = (timezone.now() + timedelta(days=7)).isoformat()
        body = json.dumps({'teacher_id': self.teacher2.id, 'enrollment_deadline': new_deadline})
        req = self.factory.put('/teachers/update_deadline/{}/'.format(self.course_full.id), data=body, content_type='application/json')
        resp = teacher_views.update_enrollment_deadline(req, self.course_full.id)
        assert resp.status_code == 403

        # teacher updates deadline
        body = json.dumps({'teacher_id': self.teacher.id, 'enrollment_deadline': new_deadline})
        req = self.factory.put('/teachers/update_deadline/{}/'.format(self.course.id), data=body, content_type='application/json')
        resp = teacher_views.update_enrollment_deadline(req, self.course.id)
        assert resp.status_code == 200
        data = self._json_response(resp)
        assert 'new_deadline' in data

    def test_update_grade(self):
        # create enrollment for course_full which teacher2 doesn't have access to
        new_student_user = User.objects.create_user(username='s3', email='s3@example.com', password='pass')
        new_student = Student.objects.create(user=new_student_user, first_name='G', last_name='Stu', age=22, gpa=3.0)

        # Create enrollment in course that teacher2 doesn't teach (course_full)
        # First, we need to increase openings temporarily or use a non-full course
        # Let's create enrollment for course (which both teachers teach) and one for course_full
        enrollment_shared = Enrollment.objects.create(student=new_student, course=self.course, enrolled_by=self.teacher, grade=None)

        # For permission test, create a third course that only teacher has
        course_teacher_only = Course.objects.create(name='Calculus', code='M201', credits=4, openings=10)
        self.teacher.courses.add(course_teacher_only)
        enrollment = Enrollment.objects.create(student=new_student, course=course_teacher_only, enrolled_by=self.teacher, grade=None)

        # permission check: teacher2 cannot update grade for course_teacher_only
        body = json.dumps({'teacher_id': self.teacher2.id, 'grade': 'A'})
        req = self.factory.put('/teachers/update_grade/{}/'.format(enrollment.id), data=body, content_type='application/json')
        resp = teacher_views.update_grade(req, enrollment.id)
        assert resp.status_code == 403

        # teacher updates grade
        body = json.dumps({'teacher_id': self.teacher.id, 'grade': 'A'})
        req = self.factory.put('/teachers/update_grade/{}/'.format(enrollment.id), data=body, content_type='application/json')
        resp = teacher_views.update_grade(req, enrollment.id)
        assert resp.status_code == 200
        data = self._json_response(resp)
        assert data['new_grade'] == 'A'
        enrollment.refresh_from_db()
        assert enrollment.grade == 'A'
