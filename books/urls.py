from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # Books
    path('',                        views.book_list,    name='book_list'),
    path('<int:pk>/',               views.book_detail,  name='book_detail'),
    path('add/',                    views.add_book,     name='add_book'),
    path('<int:pk>/edit/',          views.edit_book,    name='edit_book'),
    path('<int:pk>/delete/',        views.delete_book,  name='delete_book'),

    # QR Code
    path('<int:pk>/qr/',            views.book_qr,      name='book_qr'),
    path('qr-scanner/',             views.qr_scanner,   name='qr_scanner'),

    # ISBN Lookup (AJAX)
    path('isbn-lookup/',            views.isbn_lookup,  name='isbn_lookup'),

    # Reservations
    path('<int:pk>/reserve/',       views.reserve_book,       name='reserve_book'),
    path('reservation/<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('reservation/<int:pk>/notify/', views.notify_reservation, name='notify_reservation'),
    path('my-reservations/',        views.my_reservations,    name='my_reservations'),
    path('all-reservations/',       views.all_reservations,   name='all_reservations'),

    # Documents
    path('documents/',                    views.document_list,    name='document_list'),
    path('documents/upload/',             views.upload_document,  name='upload_document'),
    path('documents/<int:pk>/edit/',      views.edit_document,    name='edit_document'),
    path('documents/<int:pk>/delete/',    views.delete_document,  name='delete_document'),
]