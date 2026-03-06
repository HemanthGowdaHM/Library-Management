from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    # Reviews
    path('books/<int:book_pk>/reviews/',        views.book_reviews,     name='book_reviews'),
    path('reviews/<int:pk>/delete/',            views.delete_review,    name='delete_review'),
    path('reviews/<int:pk>/like/',              views.like_review,      name='like_review'),

    # Reading lists
    path('reading-lists/',                      views.reading_lists,          name='reading_lists'),
    path('reading-lists/create/',               views.create_reading_list,    name='create_reading_list'),
    path('reading-lists/<int:pk>/',             views.reading_list_detail,    name='reading_list_detail'),
    path('reading-lists/<int:pk>/delete/',      views.delete_reading_list,    name='delete_reading_list'),
    path('reading-lists/<int:pk>/add-book/',    views.add_book_to_list,       name='add_book_to_list'),
    path('reading-lists/<int:pk>/remove/<int:book_pk>/', views.remove_book_from_list, name='remove_book_from_list'),

    # Discussions
    path('discussions/',                        views.discussions,          name='discussions'),
    path('books/<int:book_pk>/discussions/',    views.discussions,          name='book_discussions'),
    path('discussions/<int:pk>/',               views.discussion_detail,    name='discussion_detail'),
    path('discussions/create/',                 views.create_discussion,    name='create_discussion'),
    path('books/<int:book_pk>/discussions/create/', views.create_discussion, name='create_book_discussion'),
    path('discussions/<int:pk>/delete/',        views.delete_discussion,    name='delete_discussion'),
    path('replies/<int:pk>/delete/',            views.delete_reply,         name='delete_reply'),
    path('replies/<int:pk>/like/',              views.like_reply,           name='like_reply'),

    # Study rooms
    path('study-rooms/',                        views.study_rooms,          name='study_rooms'),
    path('study-rooms/create/',                 views.create_study_room,    name='create_study_room'),
    path('study-rooms/<int:pk>/',               views.study_room_detail,    name='study_room_detail'),
    path('study-rooms/<int:pk>/join/',          views.join_study_room,      name='join_study_room'),
    path('study-rooms/<int:pk>/leave/',         views.leave_study_room,     name='leave_study_room'),
    path('study-rooms/notes/<int:pk>/delete/',  views.delete_note,          name='delete_note'),
    path('study-rooms/notes/<int:pk>/like/',    views.like_note,            name='like_note'),
    path('study-rooms/notes/<int:pk>/pin/',     views.pin_note,             name='pin_note'),
    path('study-rooms/<int:pk>/delete/',        views.delete_study_room,    name='delete_study_room'),
]