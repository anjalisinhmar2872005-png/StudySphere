from django.contrib import admin
from .models import (
    StudentProfile,
    Subject,
    Topic,
    StudyPlan,
    Task,
    Goal,
    Notification,
    PortfolioData,
    Project,
    Achievement,
    ContactMessage,
    StudyActivity,
)


admin.site.register(StudentProfile)
admin.site.register(Subject)
admin.site.register(Topic)
admin.site.register(StudyPlan)
admin.site.register(Task)
admin.site.register(Goal)
admin.site.register(Notification)
admin.site.register(PortfolioData)
admin.site.register(Project)
admin.site.register(Achievement)
admin.site.register(ContactMessage)
admin.site.register(StudyActivity)