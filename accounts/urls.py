from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('register/',           views.register_view,        name='register'),
    path('login/',              views.login_view,            name='login'),
    path('logout/',             views.logout_view,           name='logout'),
    path('pending-approval/',   views.pending_approval_view, name='pending_approval'),

    # Member
    path('dashboard/',          views.dashboard_view,        name='dashboard'),
    path('profile/',            views.profile_view,          name='profile'),
    path('profile/password/',   views.change_password_view,  name='change_password'),
    path('my-books/',           views.my_borrowing_history,  name='my_borrows'),

    # Staff — user management
    path('users/',              views.manage_users_view,     name='manage_users'),
    path('users/create/',       views.create_user_view,      name='create_user'),
    path('users/<int:user_id>/approve/', views.approve_user_view, name='approve_user'),
    path('users/<int:user_id>/delete/',  views.delete_user_view,  name='delete_user'),
    path('users/<int:user_id>/history/', views.user_borrow_history, name='user_history'),

    # Staff — borrowing
    path('issue/',              views.issue_book_view,       name='issue_book'),
    path('return/<int:record_id>/', views.return_book_view,  name='return_book'),
    
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    
    
     # AJAX search
    path('ajax/search-members/',    views.search_members_ajax,  name='search_members_ajax'),
    path('ajax/search-books/',      views.search_books_ajax,    name='search_books_ajax'),
]