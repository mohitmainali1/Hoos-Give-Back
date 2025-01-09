from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('google/login/', views.google_login, name='google_login'),
    path('google/callback/', views.google_callback, name='google_callback'),
    path('logout/', views.google_logout, name='logout'),
    path('projects/create/', views.create_project, name='create_project'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/join/', views.request_to_join, name='request_to_join'),
    path('project/<int:project_id>/upload_document/', views.upload_document, name='upload_document'),
    path('project/<int:project_id>/leave/', views.leave_project, name='leave_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('project/<int:project_id>/approve_requests/', views.approve_requests, name='approve_requests'),
    path('project/<int:project_id>/add_collaborators/', views.add_collaborators, name='add_collaborators'),
    path('project/<int:project_id>/revoke_request/', views.revoke_request, name='revoke_request'),
    path('project/<int:project_id>/transfer_ownership/', views.transfer_ownership, name='transfer_ownership'),
    path('project/<int:project_id>/search_documents/', views.search_documents, name='search_documents'),
    path('project/<int:project_id>/delete_documents/', views.delete_documents, name='delete_documents'),
    path('calendar/<int:year>/<int:month>/', views.project_calendar_view, name='project_calendar'),
    path('calendar/', views.project_calendar_view, name='project_calendar'),
    path('project/<int:project_id>/add_task/', views.add_task, name='add_task'),
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
]