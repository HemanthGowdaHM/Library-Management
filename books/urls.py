from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # Books
    path('',                    views.book_list,    name='book_list'),
    path('<int:pk>/',           views.book_detail,  name='book_detail'),
    path('add/',                views.add_book,     name='add_book'),
    path('<int:pk>/edit/',      views.edit_book,    name='edit_book'),
    path('<int:pk>/delete/',    views.delete_book,  name='delete_book'),

    # Documents — PDFs, Question Papers, Notes
    path('documents/',              views.document_list,        name='document_list'),
    path('documents/upload/',       views.upload_document,      name='upload_document'),
    path('documents/<int:pk>/edit/',   views.edit_document,     name='edit_document'),
    path('documents/<int:pk>/delete/', views.delete_document,   name='delete_document'),
]