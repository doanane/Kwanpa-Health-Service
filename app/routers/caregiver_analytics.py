from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
import statistics
import logging

from app.database import get_db
from app.auth.security import get_current_user
from app.models.user import User
from app.models.caregiver import CaregiverRelationship
from app.models.health import HealthData
from app.models.caregiver_tasks import CaregiverTask, TaskStatus
from app.models.caregiver_schedule import CaregiverSchedule, AppointmentStatus

router = APIRouter(prefix="/caregiver/analytics", tags=["caregiver_analytics"])
logger = logging.getLogger(__name__)

@router.get("/patient/{patient_id}")
async def get_patient_analytics(
    patient_id: int,
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific patient"""
    
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    # Verify relationship
    relationship = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.patient_id == patient_id,
        CaregiverRelationship.status == "approved"
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view analytics for this patient"
        )
    
    # Get patient info
    patient = db.query(User).filter(User.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Health data analysis
    health_data = db.query(HealthData).filter(
        HealthData.user_id == patient_id,
        HealthData.created_at >= start_date
    ).order_by(HealthData.created_at).all()
    
    # Task analysis
    tasks = db.query(CaregiverTask).filter(
        CaregiverTask.patient_id == patient_id,
        CaregiverTask.created_at >= start_date
    ).all()
    
    # Appointment analysis
    appointments = db.query(CaregiverSchedule).filter(
        CaregiverSchedule.patient_id == patient_id,
        CaregiverSchedule.created_at >= start_date
    ).all()
    
    # Analyze health trends
    health_trends = analyze_health_trends(health_data)
    
    # Analyze task performance
    task_analytics = analyze_task_performance(tasks)
    
    # Analyze appointment adherence
    appointment_analytics = analyze_appointment_adherence(appointments)
    
    # Overall health score
    overall_score = calculate_health_score(health_trends, task_analytics, appointment_analytics)
    
    # Risk assessment
    risk_assessment = assess_health_risk(health_trends)
    
    return {
        "patient_info": {
            "id": patient.id,
            "name": patient.username or patient.email,
            "patient_id": patient.patient_id
        },
        "analysis_period": {
            "days": days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat()
        },
        "health_trends": health_trends,
        "task_analytics": task_analytics,
        "appointment_analytics": appointment_analytics,
        "overall_score": overall_score,
        "risk_assessment": risk_assessment,
        "recommendations": generate_recommendations(health_trends, risk_assessment)
    }

def analyze_health_trends(health_data: List[HealthData]) -> Dict[str, Any]:
    """Analyze health data trends"""
    
    trends = {
        "heart_rate": analyze_metric_trend(health_data, "heart_rate"),
        "blood_pressure": analyze_metric_trend(health_data, "blood_pressure"),
        "blood_glucose": analyze_metric_trend(health_data, "blood_glucose"),
        "weight": analyze_metric_trend(health_data, "weight"),
        "sleep_time": analyze_metric_trend(health_data, "sleep_time"),
        "steps": analyze_metric_trend(health_data, "steps"),
        "water_intake": analyze_metric_trend(health_data, "water_intake")
    }
    
    # Calculate overall health trend
    metric_trends = [t["trend"] for t in trends.values() if t["has_data"]]
    if metric_trends:
        improving = metric_trends.count("improving")
        stable = metric_trends.count("stable")
        declining = metric_trends.count("declining")
        
        if improving > declining:
            overall_trend = "improving"
        elif declining > improving:
            overall_trend = "declining"
        else:
            overall_trend = "stable"
    else:
        overall_trend = "unknown"
    
    trends["overall_trend"] = overall_trend
    return trends

def analyze_metric_trend(health_data: List[HealthData], metric_name: str) -> Dict[str, Any]:
    """Analyze trend for a specific metric"""
    
    metric_data = []
    for data in health_data:
        value = getattr(data, metric_name, None)
        if value is not None:
            metric_data.append({
                "value": value,
                "timestamp": data.created_at,
                "is_critical": getattr(data, 'is_critical', False)
            })
    
    if not metric_data:
        return {
            "has_data": False,
            "message": f"No {metric_name.replace('_', ' ')} data available"
        }
    
    # Calculate statistics
    values = [d["value"] for d in metric_data]
    recent_values = values[-5:] if len(values) >= 5 else values
    
    # Determine trend
    if len(values) >= 2:
        first_half_avg = statistics.mean(values[:len(values)//2])
        second_half_avg = statistics.mean(values[len(values)//2:])
        
        if second_half_avg > first_half_avg * 1.1:
            trend = "improving"
        elif second_half_avg < first_half_avg * 0.9:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    # Check for critical values
    critical_count = sum(1 for d in metric_data if d["is_critical"])
    
    return {
        "has_data": True,
        "average": statistics.mean(values) if values else 0,
        "min": min(values) if values else 0,
        "max": max(values) if values else 0,
        "recent_average": statistics.mean(recent_values) if recent_values else 0,
        "trend": trend,
        "data_points": len(values),
        "critical_count": critical_count,
        "latest_value": values[-1] if values else None,
        "latest_timestamp": metric_data[-1]["timestamp"].isoformat() if metric_data else None
    }

def analyze_task_performance(tasks: List[CaregiverTask]) -> Dict[str, Any]:
    """Analyze task performance"""
    
    if not tasks:
        return {
            "total_tasks": 0,
            "completion_rate": 0,
            "average_completion_time": 0,
            "overdue_rate": 0
        }
    
    total_tasks = len(tasks)
    completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
    overdue_tasks = [t for t in tasks if t.is_overdue()]
    
    completion_rate = len(completed_tasks) / total_tasks * 100 if total_tasks > 0 else 0
    
    # Calculate average completion time (for completed tasks)
    completion_times = []
    for task in completed_tasks:
        if task.due_date and task.completed_at:
            completion_time = (task.completed_at - task.due_date).total_seconds() / 3600  # hours
            completion_times.append(completion_time)
    
    avg_completion_time = statistics.mean(completion_times) if completion_times else 0
    
    overdue_rate = len(overdue_tasks) / total_tasks * 100 if total_tasks > 0 else 0
    
    # Task type distribution
    task_types = {}
    for task in tasks:
        task_type = task.task_type or "other"
        task_types[task_type] = task_types.get(task_type, 0) + 1
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": len(completed_tasks),
        "completion_rate": round(completion_rate, 1),
        "average_completion_time": round(avg_completion_time, 1),
        "overdue_tasks": len(overdue_tasks),
        "overdue_rate": round(overdue_rate, 1),
        "task_type_distribution": task_types
    }

def analyze_appointment_adherence(appointments: List[CaregiverSchedule]) -> Dict[str, Any]:
    """Analyze appointment adherence"""
    
    if not appointments:
        return {
            "total_appointments": 0,
            "attendance_rate": 0,
            "cancellation_rate": 0,
            "no_show_rate": 0
        }
    
    total_appointments = len(appointments)
    completed = [a for a in appointments if a.status == AppointmentStatus.COMPLETED]
    cancelled = [a for a in appointments if a.status == AppointmentStatus.CANCELLED]
    no_show = [a for a in appointments if a.status == AppointmentStatus.NO_SHOW]
    
    attendance_rate = len(completed) / total_appointments * 100 if total_appointments > 0 else 0
    cancellation_rate = len(cancelled) / total_appointments * 100 if total_appointments > 0 else 0
    no_show_rate = len(no_show) / total_appointments * 100 if total_appointments > 0 else 0
    
    # Appointment type distribution
    appointment_types = {}
    for appointment in appointments:
        app_type = appointment.appointment_type.value
        appointment_types[app_type] = appointment_types.get(app_type, 0) + 1
    
    return {
        "total_appointments": total_appointments,
        "completed": len(completed),
        "cancelled": len(cancelled),
        "no_show": len(no_show),
        "attendance_rate": round(attendance_rate, 1),
        "cancellation_rate": round(cancellation_rate, 1),
        "no_show_rate": round(no_show_rate, 1),
        "appointment_type_distribution": appointment_types
    }

def calculate_health_score(health_trends: Dict, task_analytics: Dict, appointment_analytics: Dict) -> float:
    """Calculate overall health score (0-100)"""
    
    weights = {
        "health_trends": 0.5,
        "task_performance": 0.3,
        "appointment_adherence": 0.2
    }
    
    # Health trends score
    health_score = 0
    health_metrics = [t for t in health_trends.values() if isinstance(t, dict) and t.get("has_data")]
    
    if health_metrics:
        metric_scores = []
        for metric in health_metrics:
            if metric["trend"] == "improving":
                metric_scores.append(80)
            elif metric["trend"] == "stable":
                metric_scores.append(60)
            else:  # declining
                metric_scores.append(40)
        
            # Penalize for critical values
            if metric.get("critical_count", 0) > 0:
                metric_scores[-1] -= min(20, metric["critical_count"] * 5)
        
        health_score = statistics.mean(metric_scores) if metric_scores else 50
    else:
        health_score = 50  # Default if no data
    
    # Task performance score
    task_score = task_analytics.get("completion_rate", 0) * 0.01 * 100
    task_score -= task_analytics.get("overdue_rate", 0) * 0.5  # Penalty for overdue tasks
    
    # Appointment adherence score
    appointment_score = appointment_analytics.get("attendance_rate", 0)
    appointment_score -= appointment_analytics.get("no_show_rate", 0) * 0.5  # Penalty for no-shows
    
    # Weighted total
    total_score = (
        health_score * weights["health_trends"] +
        task_score * weights["task_performance"] +
        appointment_score * weights["appointment_adherence"]
    )
    
    return max(0, min(100, total_score))

def assess_health_risk(health_trends: Dict) -> Dict[str, Any]:
    """Assess health risk level"""
    
    risk_factors = []
    warnings = []
    
    for metric_name, metric_data in health_trends.items():
        if isinstance(metric_data, dict) and metric_data.get("has_data"):
            
            # Check critical values
            if metric_data.get("critical_count", 0) > 0:
                risk_factors.append(f"Critical {metric_name.replace('_', ' ')} readings")
                warnings.append(f"Multiple critical {metric_name.replace('_', ' ')} readings detected")
            
            # Check declining trends
            if metric_data.get("trend") == "declining":
                risk_factors.append(f"Declining {metric_name.replace('_', ' ')}")
                warnings.append(f"{metric_name.replace('_', ' ').title()} is showing a declining trend")
    
    # Determine risk level
    if len(risk_factors) >= 3:
        risk_level = "high"
    elif len(risk_factors) >= 1:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "warnings": warnings,
        "total_risk_factors": len(risk_factors)
    }

def generate_recommendations(health_trends: Dict, risk_assessment: Dict) -> List[str]:
    """Generate health recommendations"""
    
    recommendations = []
    
    # General recommendations
    if health_trends.get("overall_trend") == "declining":
        recommendations.append("Schedule a consultation with healthcare provider")
        recommendations.append("Increase frequency of health monitoring")
    
    # Specific recommendations based on metrics
    for metric_name, metric_data in health_trends.items():
        if isinstance(metric_data, dict) and metric_data.get("has_data"):
            if metric_data.get("trend") == "declining":
                if metric_name == "blood_pressure":
                    recommendations.append("Monitor blood pressure twice daily")
                    recommendations.append("Reduce sodium intake and increase physical activity")
                elif metric_name == "blood_glucose":
                    recommendations.append("Check blood glucose levels before and after meals")
                    recommendations.append("Consult with dietitian for meal planning")
                elif metric_name == "heart_rate":
                    recommendations.append("Practice stress reduction techniques")
                    recommendations.append("Monitor heart rate during physical activity")
    
    # Task-related recommendations
    if risk_assessment["risk_level"] in ["medium", "high"]:
        recommendations.append("Increase task frequency for critical health monitoring")
        recommendations.append("Set up automated alerts for abnormal readings")
    
    # Appointment recommendations
    if len(recommendations) > 3:
        recommendations.append("Schedule weekly check-in with care team")
    
    return recommendations[:5]  # Limit to top 5 recommendations

@router.get("/comparative")
async def get_comparative_analytics(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comparative analytics across all patients"""
    
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    # Get all patients
    relationships = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.status == "approved"
    ).all()
    
    patient_ids = [rel.patient_id for rel in relationships]
    
    comparative_data = {}
    for patient_id in patient_ids:
        try:
            analytics = await get_patient_analytics(patient_id, days, current_user, db)
            comparative_data[patient_id] = {
                "patient_name": analytics["patient_info"]["name"],
                "overall_score": analytics["overall_score"],
                "risk_level": analytics["risk_assessment"]["risk_level"],
                "completion_rate": analytics["task_analytics"]["completion_rate"],
                "attendance_rate": analytics["appointment_analytics"]["attendance_rate"]
            }
        except Exception as e:
            logger.error(f"Error analyzing patient {patient_id}: {e}")
            continue
    
    # Calculate averages
    scores = [data["overall_score"] for data in comparative_data.values()]
    completion_rates = [data["completion_rate"] for data in comparative_data.values()]
    attendance_rates = [data["attendance_rate"] for data in comparative_data.values()]
    
    return {
        "comparative_data": comparative_data,
        "averages": {
            "overall_score": statistics.mean(scores) if scores else 0,
            "completion_rate": statistics.mean(completion_rates) if completion_rates else 0,
            "attendance_rate": statistics.mean(attendance_rates) if attendance_rates else 0
        },
        "rankings": {
            "by_score": sorted(comparative_data.items(), key=lambda x: x[1]["overall_score"], reverse=True)[:5],
            "by_risk": [item for item in comparative_data.items() if item[1]["risk_level"] != "low"][:5]
        }
    }