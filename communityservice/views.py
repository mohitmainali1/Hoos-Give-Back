import os
import calendar

from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout as auth_logout
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.utils.safestring import mark_safe
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
from google_auth_oauthlib.flow import Flow
from .models import *
from .forms import *
from chat.models import *

# Configure the Google OAuth2 flow
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"
REDIRECT_URI = "http://127.0.0.1:8000/google/callback/" # Change for your site if not hosting locally.

flow = Flow.from_client_config(
    {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    scopes=["openid", "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email"],
    redirect_uri=REDIRECT_URI,
)

# Home view
def home(request):
    if request.user.is_authenticated:
        # Projects owned by the user
        projects_you_own = Project.objects.filter(owner=request.user)

        # Projects the user is collaborating in
        projects_you_are_a_part_of = Project.objects.filter(collaborators=request.user).exclude(owner=request.user)

        # Projects the user is neither an owner nor a collaborator in
        other_projects = Project.objects.exclude(owner=request.user).exclude(collaborators=request.user)
    else:
        # For anonymous users, show all projects without links
        projects_you_own = []
        projects_you_are_a_part_of = []
        other_projects = Project.objects.all()

    return render(request, 'communityservice/home.html', {
        'projects_you_own': projects_you_own,
        'projects_you_are_a_part_of': projects_you_are_a_part_of,
        'other_projects': other_projects,
    })

# Login view to start the Google OAuth2 flow
def google_login(request):
    authorization_url, state = flow.authorization_url(prompt="consent")
    request.session['state'] = state
    return redirect(authorization_url)

# Callback view for handling the response from Google
def google_callback(request):
    state = request.session.get('state')

    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials
    id_info = verify_oauth2_token(credentials.id_token, Request())

    user_email = id_info.get('email')
    user_first_name = id_info.get('given_name')
    user_last_name = id_info.get('family_name')

    user, created = CustomUser.objects.get_or_create(email=user_email, defaults={
        "username": user_email,
        "first_name": user_first_name or "Unknown",
        "last_name": user_last_name or "",
    })

    if not user.first_name:
        user.first_name = user_first_name or "Unknown"
        user.last_name = user_last_name or ""
        user.save()

    login(request, user)
    return redirect('home')

# Logout view
def google_logout(request):
    auth_logout(request)
    return redirect('home')

# Create project view
@login_required
def create_project(request):
    if request.user.is_site_admin:
        return HttpResponseForbidden("Site admins are not allowed to create projects.")

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            form.save_m2m()
            return redirect('home')
    else:
        form = ProjectForm()

    return render(request, 'communityservice/create_project.html', {'form': form})

# View for a specific project
@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Checks if ChatGroup already exists for the project and creates one if
    chat_group_exists = ChatGroup.objects.filter(group_name=project.title)
    if not chat_group_exists:
        ChatGroup.objects.create(group_name=project.title)

    is_owner = request.user == project.owner
    is_collaborator = request.user in project.collaborators.all()
    has_requested = JoinRequest.objects.filter(project=project, user=request.user).exists()

    # Only fetch documents and tasks if the user is the owner or a collaborator or a site admin
    documents = []
    tasks = []
    if is_owner or is_collaborator or request.user.is_site_admin:
        documents = project.documents.all()
        tasks = project.tasks.all()

    return render(request, 'communityservice/project_detail.html', {
        'project': project,
        'is_owner': is_owner,
        'is_collaborator': is_collaborator,
        'has_requested': has_requested,
        'documents': documents,
        'tasks': tasks,
    })

# Add collaborators to a project
@login_required
def add_collaborators(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user != project.owner:
        messages.error(request, "Only the project owner can add collaborators.")
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = AddCollaboratorsForm(request.POST)
        if form.is_valid():
            collaborators = form.cleaned_data['collaborators']
            project.collaborators.add(*collaborators)
            messages.success(request, "Collaborators added successfully.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = AddCollaboratorsForm()

    return render(request, 'communityservice/add_collaborators.html', {'form': form, 'project': project})

# Approve join requests
@login_required
def approve_requests(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Ensure only the project owner can access this page
    if request.user != project.owner:
        messages.error(request, "You do not have permission to approve requests for this project.")
        return redirect('project_detail', project_id=project.id)

    pending_requests = JoinRequest.objects.filter(project=project, status='pending')

    if request.method == 'POST':
        selected_request_ids = request.POST.getlist('approve_requests')
        action = request.POST.get('action')

        if selected_request_ids:
            selected_requests = pending_requests.filter(id__in=selected_request_ids)

            if action == 'approve':
                for join_request in selected_requests:
                    join_request.status = 'approved'
                    join_request.save()
                    project.collaborators.add(join_request.user)
                    messages.success(request, f"{join_request.user.first_name} has been approved.")
            elif action == 'deny':
                selected_requests.update(status='denied')
                messages.info(request, "Selected requests have been denied.")

        return redirect('approve_requests', project_id=project.id)

    return render(request, 'communityservice/approve_requests.html', {
        'project': project,
        'pending_requests': pending_requests,
    })

# Upload documents
@login_required
def upload_document(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Check if the user is allowed to upload documents
    is_collaborator_or_owner = request.user == project.owner or request.user in project.collaborators.all()
    if not is_collaborator_or_owner:
        messages.error(request, "You are not allowed to upload documents to this project.")
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.project = project
            document.uploader = request.user
            document.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = DocumentUploadForm()

    return render(request, 'communityservice/upload_document.html', {'form': form, 'project': project})

# Request to join a project
@login_required
def request_to_join(request, project_id):
    if request.user.is_site_admin:
        return HttpResponseForbidden("Site admins are not allowed to request to join projects.")

    project = get_object_or_404(Project, id=project_id)

    # Check if the user has already sent a request
    existing_request = JoinRequest.objects.filter(user=request.user, project=project).first()
    if existing_request:
        messages.info(request, "You have already requested to join this project.")
        return redirect('project_detail', project_id=project.id)

    # Create a new join request
    JoinRequest.objects.create(user=request.user, project=project)
    messages.success(request, "Your request to join the project has been sent.")
    return redirect('project_detail', project_id=project.id)

# Leave a project view
@login_required
def leave_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user == project.owner:
        collaborators = project.collaborators.exclude(id=request.user.id)

        if not collaborators.exists():
            messages.error(request, "You cannot leave a project without appointing a new owner.")
            return redirect('project_detail', project_id=project.id)

        if request.method == "POST":
            new_owner_id = request.POST.get('new_owner')
            new_owner = get_object_or_404(CustomUser, id=new_owner_id)
            project.owner = new_owner
            project.collaborators.remove(request.user)
            project.save()

            messages.success(request, "You have successfully transferred ownership and left the project.")
            return redirect('home')

        return render(request, 'communityservice/transfer_ownership.html',
                      {'project': project, 'collaborators': collaborators})

    else:
        project.collaborators.remove(request.user)
        messages.success(request, "You have successfully left the project.")
        return redirect('home')

# View for deleting a project
@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Allow only site admins or the project owner to delete the project
    if not (request.user == project.owner or request.user.is_site_admin):
        messages.error(request, "You do not have permission to delete this project.")
        return redirect("project_detail", project_id=project.id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "The project has been successfully deleted.")
        return redirect("home")

    return render(request, "communityservice/delete_project.html", {"project": project})

# View for adding collaborators
@login_required
def add_collaborators(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user != project.owner:
        messages.error(request, "Only the project owner can add collaborators.")
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = AddCollaboratorsForm(request.POST)
        if form.is_valid():
            collaborators = form.cleaned_data['collaborators']
            # Exclude site admins from being added
            collaborators = [user for user in collaborators if not user.is_site_admin]
            project.collaborators.add(*collaborators)
            messages.success(request, "Collaborators added successfully.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = AddCollaboratorsForm()

    return render(request, 'communityservice/add_collaborators.html', {'form': form, 'project': project})

# Revoke request
@login_required
def revoke_request(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    join_request = JoinRequest.objects.filter(project=project, user=request.user).first()
    if join_request:
        join_request.delete()
        messages.success(request, "Your request to join this project has been revoked.")
    else:
        messages.error(request, "You have no pending request for this project.")

    return redirect('project_detail', project_id=project.id)

# Transfer ownership
@login_required
def transfer_ownership(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Ensure only the current owner can transfer ownership
    if request.user != project.owner:
        messages.error(request, "You do not have permission to transfer ownership of this project.")
        return redirect('project_detail', project_id=project.id)

    # Get collaborators eligible for ownership transfer
    collaborators = project.collaborators.exclude(id=request.user.id)

    if not collaborators.exists():
        messages.error(request, "No collaborators available to transfer ownership.")
        return redirect('project_detail', project_id=project.id)

    if request.method == "POST":
        new_owner_id = request.POST.get('new_owner')
        new_owner = get_object_or_404(CustomUser, id=new_owner_id)

        # Transfer ownership
        project.owner = new_owner
        project.collaborators.add(request.user)  # Add current owner as a collaborator
        project.collaborators.remove(new_owner)  # Remove new owner from collaborators
        project.save()

        messages.success(
            request,
            f"Ownership successfully transferred to {new_owner.first_name} {new_owner.last_name}.",
        )
        return redirect('project_detail', project_id=project.id)

    return render(request, 'communityservice/transfer_ownership.html', {
        'project': project,
        'collaborators': collaborators,
    })

@login_required
def upload_document(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user not in project.collaborators.all() and request.user != project.owner:
        messages.error(request, "You are not allowed to upload documents to this project.")
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.project = project
            document.uploader = request.user
            document.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = DocumentUploadForm()

    return render(request, 'communityservice/upload_document.html', {'form': form, 'project': project})

@login_required
def search_documents(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Restrict access to project collaborators or owner
    if request.user not in project.collaborators.all() and request.user != project.owner:
        messages.error(request, "You do not have permission to search documents in this project.")
        return redirect("project_detail", project_id=project_id)

    query = request.GET.get("q", "").strip()
    results = []

    if query:
        results = project.documents.filter(Q(title__icontains=query) | Q(keywords__icontains=query))

    return render(request, "communityservice/search_results.html", {
        "project": project,
        "query": query,
        "results": results,
    })

@login_required
def delete_documents(request, project_id):
    # Ensure the project exists
    project = get_object_or_404(Project, id=project_id)

    # Check if the user is a site admin
    if request.user.is_site_admin:
        # Site admins can see all files for the project
        files = Document.objects.filter(project=project)
    else:
        # Regular users can only see files they uploaded for the project
        files = Document.objects.filter(uploader=request.user, project=project)

    if request.method == 'POST':
        # Get selected files from the form
        file_ids = request.POST.getlist('files')
        # Allow site admins to delete any files; regular users can only delete their own
        if request.user.is_site_admin:
            Document.objects.filter(id__in=file_ids, project=project).delete()
        else:
            Document.objects.filter(id__in=file_ids, uploader=request.user, project=project).delete()

        messages.success(request, "Selected files were deleted successfully.")
        return redirect('delete_documents', project_id=project.id)

    return render(request, 'communityservice/delete_documents.html', {
        'files': files,
        'project': project,
    })

class ProjectCalendar(calendar.HTMLCalendar):
    def __init__(self, projects):
        super().__init__()
        self.projects = projects

    def formatday(self, day, weekday, month, year):
        if day == 0:
            return '<td></td>'

        day_projects = [
            project for project in self.projects
            if project.project_date == datetime(year, month, day).date()
        ]

        events = "".join(
            f"<div>{project.title} ({project.start_time} - {project.end_time})</div>"
            for project in day_projects
        )

        return f"<td><span>{day}</span><div>{events}</div></td>"

    def formatweek(self, theweek, month, year):
        week_html = "".join(self.formatday(d, wd, month, year) for d, wd in theweek)
        return f"<tr>{week_html}</tr>"

    def formatmonth(self, year, month):
        calendar_html = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        calendar_html += f"{self.formatmonthname(year, month, withyear=True)}\n"
        calendar_html += f"{self.formatweekheader()}\n"
        for week in self.monthdays2calendar(year, month):
            calendar_html += f"{self.formatweek(week, month, year)}\n"
        calendar_html += "</table>"
        return calendar_html

def project_calendar_view(request, year=None, month=None):
    today = datetime.today()
    year = year or today.year
    month = month or today.month

    # Get projects for the user
    if request.user.is_authenticated:
        projects = Project.objects.filter(
            collaborators=request.user,
            project_date__year=year,
            project_date__month=month
        )
    else:
        # empty queryset for unauthenticated users
        projects = Project.objects.none()

        # Generate calendar
    cal = ProjectCalendar(projects)
    html_calendar = mark_safe(cal.formatmonth(year, month))

    context = {
        "calendar": html_calendar,
        "current_month": datetime(year, month, 1).strftime("%B %Y"),
        "prev_month": (month - 1) or 12,
        "prev_year": year - 1 if month == 1 else year,
        "next_month": (month % 12) + 1,
        "next_year": year + 1 if month == 12 else year,
    }
    return render(request, "communityservice/project_calendar.html", context)

@login_required
def add_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user != project.owner and request.user not in project.collaborators.all():
        return HttpResponseForbidden("You are not allowed to add tasks to this project.")

    if request.method == "POST":
        title = request.POST.get("task_title", "").strip()
        if title:
            Task.objects.create(project=project, title=title)
            messages.success(request, "Task added successfully.")
        return redirect("project_detail", project_id=project.id)

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
        task.is_completed = True
        task.save()
        messages.success(request, "Task marked as complete.")
        return redirect("project_detail", project_id=task.project.id)

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
        project_id = task.project.id
        task.delete()
        messages.success(request, "Task deleted successfully.")
        return redirect("project_detail", project_id=project_id)

@login_required
def profile(request):
    user = request.user
    context = {
        'name': user.first_name + " " + user.last_name,
        'email': user.email,
        'date_joined': user.date_joined,
    }
    return render(request, 'communityservice/profile.html', context)