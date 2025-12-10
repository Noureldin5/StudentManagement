# Activity Logger Service for MongoDB
from datetime import datetime, timezone, timedelta
from mongo_config import mongo_connection
from typing import Optional, Dict, Any, List


class ActivityLogger:
    """Service for logging user activities to MongoDB"""

    @staticmethod
    def log_activity(
        action_type: str,
        user_id: Optional[int] = None,
        user_type: Optional[str] = None,
        username: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Log an activity to MongoDB
        
        Args:
            action_type: Type of action (login, logout, enroll, grade_update, etc.)
            user_id: ID of the user performing the action
            user_type: Type of user (admin, teacher, student)
            username: Username of the user
            details: Additional details about the action
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            True if logged successfully, False otherwise
        """
        if not mongo_connection.is_connected:
            return False

        try:
            db = mongo_connection.db
            
            activity_log = {
                "action_type": action_type,
                "user_id": user_id,
                "user_type": user_type,
                "username": username,
                "details": details or {},
                "ip_address": ip_address,
                "user_agent": user_agent,
                "timestamp": datetime.now(timezone.utc)
            }
            
            db.activity_logs.insert_one(activity_log)
            return True
            
        except Exception as e:
            print(f"Error logging activity: {e}")
            return False

    @staticmethod
    def log_login(user, success: bool = True, ip_address: Optional[str] = None, 
                  user_agent: Optional[str] = None) -> bool:
        """Log user login attempt"""
        from templates.template_views import get_user_type
        
        if success:
            user_type = get_user_type(user) if user else None
            return ActivityLogger.log_activity(
                action_type="login_success",
                user_id=user.id if user else None,
                user_type=user_type,
                username=user.username if user else None,
                details={"success": True},
                ip_address=ip_address,
                user_agent=user_agent
            )
        else:
            return ActivityLogger.log_activity(
                action_type="login_failed",
                details={"success": False, "reason": "Invalid credentials"},
                ip_address=ip_address,
                user_agent=user_agent
            )

    @staticmethod
    def log_logout(user, ip_address: Optional[str] = None, 
                   user_agent: Optional[str] = None) -> bool:
        """Log user logout"""
        from templates.template_views import get_user_type
        
        user_type = get_user_type(user) if user else None
        return ActivityLogger.log_activity(
            action_type="logout",
            user_id=user.id if user else None,
            user_type=user_type,
            username=user.username if user else None,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_enrollment(student, course, enrolled_by, action: str = "enrolled") -> bool:
        """Log student enrollment action"""
        return ActivityLogger.log_activity(
            action_type=f"enrollment_{action}",
            user_id=enrolled_by.user.id if enrolled_by else None,
            user_type="teacher",
            username=enrolled_by.user.username if enrolled_by else "system",
            details={
                "student_id": student.id,
                "student_name": f"{student.first_name} {student.last_name}",
                "course_id": course.id,
                "course_name": course.name,
                "course_code": course.code,
                "action": action
            }
        )

    @staticmethod
    def log_grade_update(enrollment, old_grade: Optional[float], new_grade: Optional[float], 
                        teacher) -> bool:
        """Log grade update"""
        return ActivityLogger.log_activity(
            action_type="grade_update",
            user_id=teacher.user.id if teacher else None,
            user_type="teacher",
            username=teacher.user.username if teacher else "system",
            details={
                "enrollment_id": enrollment.id,
                "student_id": enrollment.student.id,
                "student_name": f"{enrollment.student.first_name} {enrollment.student.last_name}",
                "course_id": enrollment.course.id,
                "course_name": enrollment.course.name,
                "old_grade": old_grade,
                "new_grade": new_grade,
                "old_letter_grade": enrollment.letter_grade if old_grade else None,
                "new_letter_grade": enrollment.letter_grade if new_grade else None
            }
        )

    @staticmethod
    def log_enrollment_request(student, course, action: str, teacher=None, 
                               reason: Optional[str] = None) -> bool:
        """Log enrollment request actions (created, approved, rejected, waitlisted)"""
        details = {
            "student_id": student.id,
            "student_name": f"{student.first_name} {student.last_name}",
            "course_id": course.id,
            "course_name": course.name,
            "course_code": course.code,
            "action": action
        }
        
        if reason:
            details["reason"] = reason
            
        user_id = None
        user_type = None
        username = None
        
        if teacher:
            user_id = teacher.user.id
            user_type = "teacher"
            username = teacher.user.username
        elif action == "created":
            user_id = student.user.id
            user_type = "student"
            username = student.user.username
            
        return ActivityLogger.log_activity(
            action_type=f"enrollment_request_{action}",
            user_id=user_id,
            user_type=user_type,
            username=username,
            details=details
        )

    @staticmethod
    def log_registration(user, profile_type: str) -> bool:
        """Log new user registration"""
        return ActivityLogger.log_activity(
            action_type="user_registration",
            user_id=user.id,
            user_type=profile_type,
            username=user.username,
            details={
                "profile_type": profile_type,
                "email": user.email
            }
        )

    @staticmethod
    def log_course_deadline_update(course, old_deadline, new_deadline, teacher) -> bool:
        """Log course enrollment deadline update"""
        return ActivityLogger.log_activity(
            action_type="course_deadline_update",
            user_id=teacher.user.id if teacher else None,
            user_type="teacher",
            username=teacher.user.username if teacher else "system",
            details={
                "course_id": course.id,
                "course_name": course.name,
                "old_deadline": old_deadline.isoformat() if old_deadline else None,
                "new_deadline": new_deadline.isoformat() if new_deadline else None
            }
        )

    @staticmethod
    def get_recent_activities(limit: int = 50, action_type: Optional[str] = None,
                             user_id: Optional[int] = None) -> List[Dict]:
        """
        Retrieve recent activities from MongoDB
        
        Args:
            limit: Maximum number of activities to retrieve
            action_type: Filter by action type
            user_id: Filter by user ID
            
        Returns:
            List of activity dictionaries
        """
        if not mongo_connection.is_connected:
            return []

        try:
            db = mongo_connection.db
            
            # Build query filter
            query = {}
            if action_type:
                query["action_type"] = action_type
            if user_id:
                query["user_id"] = user_id
            
            # Query activities, sorted by timestamp descending
            activities = list(db.activity_logs.find(
                query,
                {"_id": 0}  # Exclude MongoDB _id field
            ).sort("timestamp", -1).limit(limit))
            
            return activities
            
        except Exception as e:
            print(f"Error retrieving activities: {e}")
            return []

    @staticmethod
    def get_activity_stats(days: int = 7) -> Dict[str, Any]:
        """
        Get activity statistics for the last N days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with statistics
        """
        if not mongo_connection.is_connected:
            return {}

        try:
            db = mongo_connection.db
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Get total activities
            total_activities = db.activity_logs.count_documents({
                "timestamp": {"$gte": cutoff_date}
            })
            
            # Get activities by type
            pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": "$action_type",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            activities_by_type = list(db.activity_logs.aggregate(pipeline))
            
            # Get activities by user type
            pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": "$user_type",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            activities_by_user_type = list(db.activity_logs.aggregate(pipeline))
            
            return {
                "total_activities": total_activities,
                "activities_by_type": activities_by_type,
                "activities_by_user_type": activities_by_user_type,
                "period_days": days
            }
            
        except Exception as e:
            print(f"Error retrieving activity stats: {e}")
            return {}

    @staticmethod
    def log_notification(recipient_email: str, subject: str, message: str, 
                        status: str = "sent", notification_type: str = "email") -> bool:
        """Log notification/email sent"""
        if not mongo_connection.is_connected:
            return False

        try:
            db = mongo_connection.db
            
            notification_log = {
                "notification_type": notification_type,
                "recipient_email": recipient_email,
                "subject": subject,
                "message": message,
                "status": status,
                "created_at": datetime.now(timezone.utc)
            }
            
            db.notification_logs.insert_one(notification_log)
            return True
            
        except Exception as e:
            print(f"Error logging notification: {e}")
            return False

