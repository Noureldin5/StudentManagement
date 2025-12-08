# Generated manually to convert letter grades to numeric grades

from django.db import migrations, models


def convert_letter_to_numeric(apps, schema_editor):
    """Convert existing letter grades to numeric grades and clear student GPA"""
    Enrollment = apps.get_model('students', 'Enrollment')
    
    # Map letter grades to numeric equivalents (midpoint of range)
    grade_mapping = {
        'A': 95.0,
        'A+': 97.0,
        'A-': 92.0,
        'B': 85.0,
        'B+': 87.0,
        'B-': 82.0,
        'C': 75.0,
        'C+': 77.0,
        'C-': 72.0,
        'D': 65.0,
        'D+': 67.0,
        'D-': 62.0,
        'F': 50.0,
    }
    
    # For enrollments with letter grades, we'll clear them
    # Teachers will need to re-enter numeric grades
    for enrollment in Enrollment.objects.all():
        if enrollment.grade and enrollment.grade.strip():
            # If it's a letter grade, clear it
            if enrollment.grade.strip() in grade_mapping:
                enrollment.grade = None
                enrollment.save()


def reverse_conversion(apps, schema_editor):
    """Reverse migration - not really possible, just clear grades"""
    Enrollment = apps.get_model('students', 'Enrollment')
    Enrollment.objects.all().update(grade=None)


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0005_alter_student_enrolled_courses'),
    ]

    operations = [
        # First, run the data migration to clear letter grades
        migrations.RunPython(convert_letter_to_numeric, reverse_conversion),
        
        # Remove the gpa field from Student model
        migrations.RemoveField(
            model_name='student',
            name='gpa',
        ),
        
        # Change grade field from CharField to FloatField
        migrations.AlterField(
            model_name='enrollment',
            name='grade',
            field=models.FloatField(blank=True, null=True, help_text='Numeric grade (0-100)'),
        ),
    ]

