# API Views for Activity Logs
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from activity_logger import ActivityLogger
from django.contrib.auth.decorators import login_required
from templates.template_views import get_user_type


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_activity_logs(request):
    """
    Get activity logs with optional filtering
    
    Query params:
    - limit: Number of logs to retrieve (default: 50, max: 200)
    - action_type: Filter by action type
    - user_id: Filter by user ID
    """
    # Check if user is admin or teacher
    user_type = get_user_type(request.user)
    if user_type not in ['admin', 'teacher']:
        return Response(
            {"error": "Permission denied. Admins and teachers only."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get query parameters
    limit = min(int(request.query_params.get('limit', 50)), 200)
    action_type = request.query_params.get('action_type')
    user_id = request.query_params.get('user_id')
    
    # Convert user_id to int if provided
    if user_id:
        try:
            user_id = int(user_id)
        except ValueError:
            user_id = None
    
    # Get activities
    activities = ActivityLogger.get_recent_activities(
        limit=limit,
        action_type=action_type,
        user_id=user_id
    )
    
    return Response({
        "count": len(activities),
        "activities": activities
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_activity_stats(request):
    """
    Get activity statistics (Admin only)
    
    Query params:
    - days: Number of days to analyze (default: 7)
    """
    days = int(request.query_params.get('days', 7))
    
    stats = ActivityLogger.get_activity_stats(days=days)
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_activity_logs(request):
    """
    Get activity logs for the current user
    
    Query params:
    - limit: Number of logs to retrieve (default: 50)
    """
    limit = min(int(request.query_params.get('limit', 50)), 200)
    
    activities = ActivityLogger.get_recent_activities(
        limit=limit,
        user_id=request.user.id
    )
    
    return Response({
        "count": len(activities),
        "activities": activities
    })


@login_required
def activity_logs_view(request):
    """Template view for activity logs (Admin and Teacher only)"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    
    user_type = get_user_type(request.user)
    if user_type not in ['admin', 'teacher']:
        messages.error(request, 'Access denied. Admins and teachers only.')
        return redirect('/')
    
    # Get query parameters
    action_filter = request.GET.get('action_type', '')
    limit = min(int(request.GET.get('limit', 50)), 200)
    
    # Get activities
    activities = ActivityLogger.get_recent_activities(
        limit=limit,
        action_type=action_filter if action_filter else None
    )
    
    # Get statistics
    stats = ActivityLogger.get_activity_stats(days=7)
    
    # Get unique action types for filter dropdown
    action_types = set()
    for activity in activities:
        if 'action_type' in activity:
            action_types.add(activity['action_type'])
    action_types = sorted(list(action_types))
    
    return render(request, 'activity_logs.html', {
        'activities': activities,
        'stats': stats,
        'action_types': action_types,
        'selected_action_type': action_filter,
        'limit': limit
    })

