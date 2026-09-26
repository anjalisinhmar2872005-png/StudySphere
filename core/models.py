from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    course = models.CharField(max_length=100)
    college = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    education = models.TextField(blank=True)
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=50, blank=True)
    semester = models.IntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.subject_name


class Topic(models.Model):
    topic_name = models.CharField(max_length=150)
    chapter = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=20,
        choices=[
            ('Low', 'Low'),
            ('Medium', 'Medium'),
            ('High', 'High'),
        ],
        default='Medium'
    )
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return self.topic_name


class StudyPlan(models.Model):
    date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    duration = models.IntegerField()
    priority = models.CharField(
        max_length=20,
        choices=[
            ('Low', 'Low'),
            ('Medium', 'Medium'),
            ('High', 'High'),
        ],
        default='Medium'
    )
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Planned', 'Planned'),
            ('Completed', 'Completed'),
        ],
        default='Planned'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subject.subject_name} - {self.date}"


class Task(models.Model):
    title = models.CharField(max_length=150)
    due_date = models.DateField()
    priority = models.CharField(
        max_length=20,
        choices=[
            ('Low', 'Low'),
            ('Medium', 'Medium'),
            ('High', 'High'),
        ],
        default='Medium'
    )
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed'),
        ],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Goal(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    target_date = models.DateField()
    priority = models.CharField(
        max_length=20,
        choices=[
            ('Low', 'Low'),
            ('Medium', 'Medium'),
            ('High', 'High'),
        ],
        default='Medium'
    )
    progress = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Active', 'Active'),
            ('Completed', 'Completed'),
        ],
        default='Active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Notification(models.Model):
    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=[
            ('Task', 'Task'),
            ('Study Plan', 'Study Plan'),
            ('Goal', 'Goal'),
            ('Achievement', 'Achievement'),
        ]
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Achievement(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    organization = models.CharField(max_length=150, blank=True)
    date = models.DateField(blank=True, null=True)
    certificate = models.FileField(
        upload_to='certificates/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class PortfolioData(models.Model):
    about = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    education = models.TextField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} Portfolio"


class Project(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    technologies = models.CharField(max_length=300)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    image = models.ImageField(
        upload_to='project_images/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class StudyActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    date = models.DateField()
    duration = models.IntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject.subject_name} - {self.date}"