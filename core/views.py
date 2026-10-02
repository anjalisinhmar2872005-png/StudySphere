from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm
from .models import (
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
    StudyActivity,
)
from datetime import date, timedelta

def home_view(request):
    return render(request, 'core/home.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'core/register.html', {'form': form})
    

@login_required
def dashboard_view(request):
    subjects = Subject.objects.filter(user=request.user)
    topics = Topic.objects.filter(subject__user=request.user)
    study_plans = StudyPlan.objects.filter(user=request.user)
    tasks = Task.objects.filter(user=request.user)
    goals = Goal.objects.filter(user=request.user)

    total_subjects = subjects.count()
    total_topics = topics.count()
    completed_topics = topics.filter(is_completed=True).count()

    pending_tasks = tasks.exclude(status='Completed').count()
    active_goals = goals.filter(status='Active').count()

    today = timezone.localdate()

    upcoming_tasks = tasks.filter(
        status__in=['Pending', 'In Progress'],
        due_date__gte=today
    ).order_by('due_date')[:5]

    # Smart Priority
    smart_priority_tasks = []

    for task in tasks:
        if task.status == 'Completed':
            continue

        days_left = (task.due_date - today).days

        if task.priority == 'High' or days_left <= 2:
            priority_level = 'High'

        elif task.priority == 'Medium' or days_left <= 5:
            priority_level = 'Medium'

        else:
            priority_level = 'Low'

        smart_priority_tasks.append({
            'task': task,
            'priority_level': priority_level,
        })

    # High priority tasks first
    priority_order = {
        'High': 1,
        'Medium': 2,
        'Low': 3,
    }

    smart_priority_tasks.sort(
        key=lambda item: (
            priority_order[item['priority_level']],
            item['task'].due_date
        )
    )

    context = {
        'total_subjects': total_subjects,
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'pending_tasks': pending_tasks,
        'active_goals': active_goals,
        'upcoming_tasks': upcoming_tasks,
        'study_plans': study_plans,
        'goals': goals,
        'smart_priority_tasks': smart_priority_tasks[:5],
    }

    return render(request, 'core/dashboard.html', context)

@login_required
def analytics_view(request):
    subjects = Subject.objects.filter(user=request.user)
    tasks = Task.objects.filter(user=request.user)
    goals = Goal.objects.filter(user=request.user)
    activities = StudyActivity.objects.filter(user=request.user)

    subject_data = []

    for subject in subjects:
        total_topics = Topic.objects.filter(subject=subject).count()

        completed_topics = Topic.objects.filter(
            subject=subject,
            is_completed=True
        ).count()

        if total_topics > 0:
            progress = int((completed_topics / total_topics) * 100)
        else:
            progress = 0

        subject_data.append({
            'name': subject.subject_name,
            'progress': progress,
            'total_topics': total_topics,
            'completed_topics': completed_topics,
        })

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='Completed').count()
    pending_tasks = tasks.exclude(status='Completed').count()

    total_goals = goals.count()
    completed_goals = goals.filter(status='Completed').count()

    # Study Activity
    total_study_minutes = sum(
        activity.duration for activity in activities
    )

    total_study_hours = round(
        total_study_minutes / 60, 1
    )

    # Study Streak
    activity_dates = set(
        activity.date for activity in activities
    )

    current_streak = 0
    today = date.today()

    while today in activity_dates:
        current_streak += 1
        today -= timedelta(days=1)

    context = {
        'subject_data': subject_data,

        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,

        'total_goals': total_goals,
        'completed_goals': completed_goals,

        'total_study_minutes': total_study_minutes,
        'total_study_hours': total_study_hours,

        'current_streak': current_streak,
    }

    return render(
        request,
        'core/analytics.html',
        context
    )

@login_required
def smart_priority_view(request):
    tasks = Task.objects.filter(
        user=request.user
    ).order_by('due_date')

    high_priority = []
    medium_priority = []
    low_priority = []

    today = date.today()

    for task in tasks:
        if task.status == 'Completed':
            continue

        days_left = (task.due_date - today).days

        if task.priority == 'High' or days_left <= 2:
            high_priority.append(task)

        elif task.priority == 'Medium' or days_left <= 5:
            medium_priority.append(task)

        else:
            low_priority.append(task)

    return render(
        request,
        'core/smart_priority.html',
        {
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority,
        }
    )


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {'form': form})


@login_required
def profile_view(request):
    profile = request.user.studentprofile
    return render(request, 'core/profile.html', {'profile': profile})


@login_required
def edit_profile_view(request):
    profile = request.user.studentprofile

    if request.method == 'POST':
        profile.name = request.POST.get('name')
        profile.email = request.POST.get('email')
        profile.course = request.POST.get('course')
        profile.college = request.POST.get('college')
        profile.bio = request.POST.get('bio')
        profile.skills = request.POST.get('skills')
        profile.education = request.POST.get('education')

        if request.FILES.get('profile_photo'):
            profile.profile_photo = request.FILES.get('profile_photo')

        profile.save()

        return redirect('profile')

    return render(
        request,
        'core/edit_profile.html',
        {'profile': profile}
    )


@login_required
def subject_list_view(request):
    subjects = Subject.objects.filter(user=request.user)

    for subject in subjects:
        total_topics = subject.topic_set.count()
        completed_topics = subject.topic_set.filter(
            is_completed=True
        ).count()

        if total_topics > 0:
            subject.progress = int(
                (completed_topics / total_topics) * 100
            )
        else:
            subject.progress = 0

    return render(
        request,
        'core/subjects.html',
        {'subjects': subjects}
    )

@login_required
def delete_subject_view(request, subject_id):
    subject = Subject.objects.get(id=subject_id, user=request.user)
    subject.delete()
    return redirect('subjects')


@login_required
def add_subject_view(request):
    if request.method == 'POST':
        Subject.objects.create(
            user=request.user,
            subject_name=request.POST.get('subject_name'),
            subject_code=request.POST.get('subject_code'),
            semester=request.POST.get('semester'),
            description=request.POST.get('description')
        )

        return redirect('subjects')

    return render(request, 'core/add_subject.html')

@login_required
def edit_subject_view(request, subject_id):
    subject = Subject.objects.get(
        id=subject_id,
        user=request.user
    )

    if request.method == 'POST':
        subject.subject_name = request.POST.get('subject_name')
        subject.subject_code = request.POST.get('subject_code')
        subject.semester = request.POST.get('semester')
        subject.description = request.POST.get('description')

        subject.save()

        return redirect('subjects')

    return render(
        request,
        'core/edit_subject.html',
        {'subject': subject}
    )


@login_required
def topic_list_view(request, subject_id):
    subject = Subject.objects.get(
        id=subject_id,
        user=request.user
    )

    topics = Topic.objects.filter(subject=subject)

    return render(
        request,
        'core/topics.html',
        {
            'subject': subject,
            'topics': topics
        }
    )


@login_required
def add_topic_view(request, subject_id):
    subject = Subject.objects.get(
        id=subject_id,
        user=request.user
    )

    if request.method == 'POST':
        Topic.objects.create(
            subject=subject,
            topic_name=request.POST.get('topic_name'),
            chapter=request.POST.get('chapter'),
            description=request.POST.get('description'),
            priority=request.POST.get('priority')
        )

        return redirect('topics', subject_id=subject.id)

    return render(
        request,
        'core/add_topic.html',
        {'subject': subject}
    )


@login_required
def toggle_topic_view(request, topic_id):
    topic = Topic.objects.get(
        id=topic_id,
        subject__user=request.user
    )

    topic.is_completed = not topic.is_completed
    topic.save()

    return redirect('topics', subject_id=topic.subject.id)


@login_required
def edit_topic_view(request, topic_id):
    topic = Topic.objects.get(
        id=topic_id,
        subject__user=request.user
    )

    if request.method == 'POST':
        topic.topic_name = request.POST.get('topic_name')
        topic.chapter = request.POST.get('chapter')
        topic.description = request.POST.get('description')
        topic.priority = request.POST.get('priority')
        topic.save()

        return redirect(
            'topics',
            subject_id=topic.subject.id
        )

    return render(
        request,
        'core/edit_topic.html',
        {'topic': topic}
    )


@login_required
def delete_topic_view(request, topic_id):
    topic = Topic.objects.get(
        id=topic_id,
        subject__user=request.user
    )

    subject_id = topic.subject.id

    if request.method == 'POST':
        topic.delete()

    return redirect('topics', subject_id=subject_id)

@login_required
def study_plan_view(request):
    study_plans = StudyPlan.objects.filter(
        user=request.user
    ).order_by('date', 'start_time')

    return render(
        request,
        'core/study_plans.html',
        {'study_plans': study_plans}
    )


@login_required
def study_plan_list_view(request):
    study_plans = StudyPlan.objects.filter(
        user=request.user
    )

    return render(
        request,
        'core/study_plans.html',
        {'study_plans': study_plans}
    )


@login_required
def add_study_plan_view(request):
    subjects = Subject.objects.filter(user=request.user)
    topics = Topic.objects.filter(
        subject__user=request.user
    )

    if request.method == 'POST':
        StudyPlan.objects.create(
            user=request.user,
            subject_id=request.POST.get('subject'),
            topic_id=request.POST.get('topic'),
            date=request.POST.get('date'),
            start_time=request.POST.get('start_time') or None,
            duration=request.POST.get('duration'),
            priority=request.POST.get('priority'),
            notes=request.POST.get('notes')
        )

        return redirect('study_plans')

    return render(
        request,
        'core/add_study_plan.html',
        {
            'subjects': subjects,
            'topics': topics
        }
    )

@login_required
def delete_study_plan_view(request, study_plan_id):
    study_plan = StudyPlan.objects.get(
        id=study_plan_id,
        user=request.user
    )
    study_plan.delete()
    return redirect('study_plans')


@login_required
def task_list_view(request):
    tasks = Task.objects.filter(user=request.user)

    return render(
        request,
        'core/tasks.html',
        {'tasks': tasks}
    )



@login_required
def add_task_view(request):
    subjects = Subject.objects.filter(user=request.user)
    topics = Topic.objects.filter(
        subject__user=request.user
    )

    if request.method == 'POST':
        task = Task.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            subject_id=request.POST.get('subject'),
            topic_id=request.POST.get('topic'),
            due_date=request.POST.get('due_date'),
            priority=request.POST.get('priority'),
            description=request.POST.get('description'),
            status=request.POST.get('status')
        )
        task.refresh_from_db()

        if task.status != 'Completed':
            today = timezone.localdate()

            if task.due_date > today:
                Notification.objects.create(
                    user=request.user,
                    title='Upcoming Task',
                    message=(
                        f"Your task '{task.title}' "
                        f"is due on {task.due_date}."
                    ),
                    notification_type='Task'
                )
            else:
                Notification.objects.create(
                    user=request.user,
                    title='Overdue Task',
                    message=(
                        f"Your task '{task.title}' "
                        f"is due today or is overdue."
                    ),
                    notification_type='Task'
                )

        return redirect('tasks')

    return render(
        request,
        'core/add_task.html',
        {
            'subjects': subjects,
            'topics': topics
        }
    )


@login_required
def edit_task_view(request, task_id):
    task = Task.objects.get(
        id=task_id,
        user=request.user
    )

    subjects = Subject.objects.filter(user=request.user)
    topics = Topic.objects.filter(
        subject__user=request.user
    )

    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.subject_id = request.POST.get('subject')
        task.topic_id = request.POST.get('topic')
        task.due_date = request.POST.get('due_date')
        task.priority = request.POST.get('priority')
        task.status = request.POST.get('status')
        task.description = request.POST.get('description')
        task.save()

        return redirect('tasks')

    return render(
        request,
        'core/edit_task.html',
        {
            'task': task,
            'subjects': subjects,
            'topics': topics
        }
    )


@login_required
def delete_task_view(request, task_id):
    task = Task.objects.get(
        id=task_id,
        user=request.user
    )

    task.delete()

    return redirect('tasks')


@login_required
def toggle_task_view(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)

    if request.method == 'POST':
        task.status = 'Pending' if task.status == 'Completed' else 'Completed'
        task.save()

        Notification.objects.filter(
            user=request.user,
            notification_type='Task',
            message__contains=task.title
        ).delete()

        if task.status != 'Completed':
            today = timezone.localdate()
            title = 'Upcoming Task' if task.due_date > today else 'Overdue Task'
            message = (
                f"Your task '{task.title}' is due on {task.due_date}."
                if task.due_date > today
                else f"Your task '{task.title}' is due today or is overdue."
            )

            Notification.objects.create(
                user=request.user,
                title=title,
                message=message,
                notification_type='Task'
            )

    return redirect('tasks')


@login_required
def goal_list_view(request):
    goals = Goal.objects.filter(user=request.user)

    return render(
        request,
        'core/goals.html',
        {'goals': goals}
    )


@login_required
def add_goal_view(request):
    if request.method == 'POST':
        Goal.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            target_date=request.POST.get('target_date'),
            priority=request.POST.get('priority'),
            progress=request.POST.get('progress') or 0,
            status=request.POST.get('status')
        )

        return redirect('goals')

    return render(request, 'core/add_goal.html')


@login_required
def edit_goal_view(request, goal_id):
    goal = Goal.objects.get(
        id=goal_id,
        user=request.user
    )

    if request.method == 'POST':
        goal.title = request.POST.get('title')
        goal.description = request.POST.get('description')
        goal.target_date = request.POST.get('target_date')
        goal.priority = request.POST.get('priority')
        goal.progress = request.POST.get('progress') or 0
        goal.status = request.POST.get('status')
        goal.save()

        return redirect('goals')

    return render(
        request,
        'core/edit_goal.html',
        {'goal': goal}
    )


@login_required
def delete_goal_view(request, goal_id):
    goal = Goal.objects.get(id=goal_id, user=request.user)
    goal.delete()
    return redirect('goals')


@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'core/notifications.html',
        {'notifications': notifications}
    )


@login_required
def delete_notification_view(request, notification_id):
    notification = Notification.objects.get(
        id=notification_id,
        user=request.user
    )
    notification.delete()
    return redirect('notifications')

@login_required
def portfolio_view(request):
    portfolio, created = PortfolioData.objects.get_or_create(
        user=request.user
    )

    projects = Project.objects.filter(
        user=request.user
    ).order_by('-created_at')

    achievements = Achievement.objects.filter(
        user=request.user
    ).order_by('-date')

    return render(
        request,
        'core/portfolio.html',
        {
            'portfolio': portfolio,
            'projects': projects,
            'achievements': achievements,
        }
    )


@login_required
def portfolio_contact_view(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.user.get_full_name()
            or request.user.username,
            email=request.user.email,
            message=request.POST.get('message')
        )

        return redirect('portfolio')

    return redirect('portfolio')

   
@login_required
def add_study_activity_view(request):
    subjects = Subject.objects.filter(user=request.user)
    topics = Topic.objects.filter(subject__user=request.user)

    if request.method == 'POST':
        StudyActivity.objects.create(
            user=request.user,
            subject_id=request.POST.get('subject'),
            topic_id=request.POST.get('topic'),
            date=request.POST.get('date'),
            duration=request.POST.get('duration'),
            notes=request.POST.get('notes')
        )
        return redirect('study_activity')

    return render(request, 'core/add_study_activity.html', {
        'subjects': subjects,
        'topics': topics
    })
@login_required
def study_activity_list_view(request):
    activities = StudyActivity.objects.filter(
        user=request.user
    ).order_by('-date', '-created_at')

    return render(request, 'core/study_activity.html', {
        'activities': activities
    })

def home_view(request):
    return render(request, 'core/home.html')

def about_view(request):
        return render(request, 'core/about.html')

def contact_view(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            message=request.POST.get('message')
        )
        return render(request, 'core/contact.html', {
            'success': 'Your message has been sent successfully!'
        })

    return render(request, 'core/contact.html')