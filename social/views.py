from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q, F

from .models import BookReview, ReadingList, Discussion, DiscussionReply, StudyRoom, StudyNote
from books.models import Book
from accounts.decorators import approved_required


# ═══════════════════════════════════════════════════════════
# 1. REVIEWS & RATINGS
# ═══════════════════════════════════════════════════════════

# In social/views.py — replace the book_reviews view with this:

# In social/views.py — replace the book_reviews view with this:

@login_required
@approved_required
def book_reviews(request, book_pk):
    book       = get_object_or_404(Book, pk=book_pk)
    reviews    = book.reviews.select_related('user').all()
    my_review  = reviews.filter(user=request.user).first()
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    rating_counts = {i: reviews.filter(rating=i).count() for i in range(1, 6)}

    if request.method == 'POST' and not my_review:
        rating = int(request.POST.get('rating', 0))
        body   = request.POST.get('body', '').strip()
        title  = request.POST.get('title', '').strip()
        if 1 <= rating <= 5 and body:
            BookReview.objects.create(
                book=book, user=request.user,
                rating=rating, body=body, title=title
            )
            messages.success(request, 'Your review has been posted!')
            return redirect('social:book_reviews', book_pk=book_pk)
        else:
            messages.error(request, 'Please provide a rating and review text.')

    # ✅ Get IDs of reviews the current user has liked
    # Uses the M2M through table directly — no related_name needed
    liked_review_ids = set(
        BookReview.likes.through.objects.filter(
            customuser_id=request.user.pk
        ).values_list('bookreview_id', flat=True)
    )

    return render(request, 'social/book_reviews.html', {
        'book':             book,
        'reviews':          reviews,
        'my_review':        my_review,
        'avg_rating':       round(avg_rating, 1),
        'total_reviews':    reviews.count(),
        'rating_counts':    rating_counts,
        'liked_review_ids': liked_review_ids,
    })
    
    
@login_required
@approved_required
def delete_review(request, pk):
    review = get_object_or_404(BookReview, pk=pk, user=request.user)
    book_pk = review.book_id
    review.delete()
    messages.success(request, 'Review deleted.')
    return redirect('social:book_reviews', book_pk=book_pk)


@login_required
@approved_required
def like_review(request, pk):
    review = get_object_or_404(BookReview, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    # Check if already liked using through table
    already_liked = BookReview.likes.through.objects.filter(
        customuser_id=request.user.pk,
        bookreview_id=review.pk
    ).exists()

    if already_liked:
        review.likes.remove(request.user)
        liked = False
    else:
        review.likes.add(request.user)
        liked = True

    return JsonResponse({'liked': liked, 'count': review.like_count})

# ═══════════════════════════════════════════════════════════
# 2. READING LISTS
# ═══════════════════════════════════════════════════════════

@login_required
@approved_required
def reading_lists(request):
    """Browse all public reading lists + own lists."""
    public_lists = ReadingList.objects.filter(is_public=True).exclude(
        owner=request.user
    ).select_related('owner').prefetch_related('books').annotate(bc=Count('books'))
    my_lists = ReadingList.objects.filter(owner=request.user).prefetch_related('books').annotate(bc=Count('books'))
    return render(request, 'social/reading_lists.html', {
        'public_lists': public_lists,
        'my_lists': my_lists,
    })


@login_required
@approved_required
def reading_list_detail(request, pk):
    lst = get_object_or_404(ReadingList, pk=pk)
    if not lst.is_public and lst.owner != request.user:
        messages.error(request, "This reading list is private.")
        return redirect('social:reading_lists')
    books = lst.books.all()
    # Books not yet in list (for adding)
    all_books = Book.objects.exclude(pk__in=books.values_list('pk', flat=True)) if lst.owner == request.user else []
    return render(request, 'social/reading_list_detail.html', {
        'lst': lst, 'books': books, 'all_books': all_books,
        'is_owner': lst.owner == request.user,
    })


@login_required
@approved_required
def create_reading_list(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        desc  = request.POST.get('description', '').strip()
        pub   = request.POST.get('is_public') == 'on'
        if title:
            lst = ReadingList.objects.create(owner=request.user, title=title, description=desc, is_public=pub)
            messages.success(request, f'Reading list "{lst.title}" created!')
            return redirect('social:reading_list_detail', pk=lst.pk)
        messages.error(request, 'Please enter a title.')
    return render(request, 'social/create_reading_list.html')


@login_required
@approved_required
def add_book_to_list(request, pk):
    lst     = get_object_or_404(ReadingList, pk=pk, owner=request.user)
    book_id = request.POST.get('book_id')
    if book_id:
        book = get_object_or_404(Book, pk=book_id)
        lst.books.add(book)
        messages.success(request, f'"{book.title}" added to your list.')
    return redirect('social:reading_list_detail', pk=pk)


@login_required
@approved_required
def remove_book_from_list(request, pk, book_pk):
    lst  = get_object_or_404(ReadingList, pk=pk, owner=request.user)
    book = get_object_or_404(Book, pk=book_pk)
    lst.books.remove(book)
    messages.success(request, f'"{book.title}" removed from your list.')
    return redirect('social:reading_list_detail', pk=pk)


@login_required
@approved_required
def delete_reading_list(request, pk):
    lst = get_object_or_404(ReadingList, pk=pk, owner=request.user)
    lst.delete()
    messages.success(request, 'Reading list deleted.')
    return redirect('social:reading_lists')


# ═══════════════════════════════════════════════════════════
# 3. DISCUSSION THREADS
# ═══════════════════════════════════════════════════════════

@login_required
@approved_required
def discussions(request, book_pk=None):
    book = get_object_or_404(Book, pk=book_pk) if book_pk else None
    qs   = Discussion.objects.select_related('author').prefetch_related('replies')
    if book:
        qs = qs.filter(book=book)
    return render(request, 'social/discussions.html', {
        'threads': qs, 'book': book,
    })


@login_required
@approved_required
def discussion_detail(request, pk):
    thread = get_object_or_404(Discussion, pk=pk)

    # ✅ Use F() expression — atomic increment, no race condition
    Discussion.objects.filter(pk=pk).update(views=F('views') + 1)
    thread.refresh_from_db(fields=['views'])

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            DiscussionReply.objects.create(
                discussion=thread, author=request.user, body=body
            )
            messages.success(request, 'Reply posted.')
            return redirect('social:discussion_detail', pk=pk)

    replies = thread.replies.select_related('author')

    # Get IDs of replies the current user has liked
    liked_reply_ids = set(
        DiscussionReply.likes.through.objects.filter(
            customuser_id=request.user.pk
        ).values_list('discussionreply_id', flat=True)
    )

    return render(request, 'social/discussion_detail.html', {
        'thread':          thread,
        'replies':         replies,
        'liked_reply_ids': liked_reply_ids,
    })

@login_required
@approved_required
def create_discussion(request, book_pk=None):
    book = get_object_or_404(Book, pk=book_pk) if book_pk else None
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body  = request.POST.get('body', '').strip()
        if title and body:
            thread = Discussion.objects.create(
                author=request.user, title=title, body=body, book=book
            )
            messages.success(request, 'Discussion started!')
            return redirect('social:discussion_detail', pk=thread.pk)
        messages.error(request, 'Title and body are required.')
    return render(request, 'social/create_discussion.html', {'book': book})


@login_required
@approved_required
def delete_discussion(request, pk):
    thread = get_object_or_404(Discussion, pk=pk)
    if thread.author != request.user and not request.user.can_manage_books:
        messages.error(request, 'Not allowed.')
        return redirect('social:discussion_detail', pk=pk)
    book_pk = thread.book_id
    thread.delete()
    messages.success(request, 'Discussion deleted.')
    return redirect('social:book_discussions', book_pk=book_pk) if book_pk else redirect('social:discussions')


@login_required
@approved_required
def delete_reply(request, pk):
    reply = get_object_or_404(DiscussionReply, pk=pk)
    if reply.author != request.user and not request.user.can_manage_books:
        messages.error(request, 'Not allowed.')
        return redirect('social:discussion_detail', pk=reply.discussion_id)
    disc_pk = reply.discussion_id
    reply.delete()
    messages.success(request, 'Reply deleted.')
    return redirect('social:discussion_detail', pk=disc_pk)


@login_required
@approved_required
def like_reply(request, pk):
    reply = get_object_or_404(DiscussionReply, pk=pk)
    if request.user in reply.likes.all():
        reply.likes.remove(request.user)
        liked = False
    else:
        reply.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': reply.like_count})


# ═══════════════════════════════════════════════════════════
# 4. STUDY ROOMS
# ═══════════════════════════════════════════════════════════

@login_required
@approved_required
def study_rooms(request):
    public_rooms = StudyRoom.objects.filter(is_private=False).select_related('created_by', 'book').prefetch_related('members')
    my_rooms     = StudyRoom.objects.filter(members=request.user).select_related('created_by', 'book')
    return render(request, 'social/study_rooms.html', {
        'public_rooms': public_rooms,
        'my_rooms': my_rooms,
    })


@login_required
@approved_required
def study_room_detail(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    if room.is_private and request.user not in room.members.all() and room.created_by != request.user:
        messages.error(request, 'This room is private.')
        return redirect('social:study_rooms')

    is_member = request.user in room.members.all() or room.created_by == request.user

    if request.method == 'POST' and is_member:
        body = request.POST.get('body', '').strip()
        if body:
            StudyNote.objects.create(room=room, author=request.user, body=body)
            return redirect('social:study_room_detail', pk=pk)

    notes = room.notes.select_related('author').prefetch_related('likes')
    return render(request, 'social/study_room_detail.html', {
        'room': room, 'notes': notes,
        'is_member': is_member, 'is_owner': room.created_by == request.user,
        'member_count': room.member_count,
    })


@login_required
@approved_required
def create_study_room(request):
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        desc    = request.POST.get('description', '').strip()
        book_id = request.POST.get('book_id')
        private = request.POST.get('is_private') == 'on'
        if name:
            book = Book.objects.filter(pk=book_id).first() if book_id else None
            room = StudyRoom.objects.create(
                created_by=request.user, name=name,
                description=desc, book=book, is_private=private,
            )
            room.members.add(request.user)
            messages.success(request, f'Study room "{room.name}" created!')
            return redirect('social:study_room_detail', pk=room.pk)
        messages.error(request, 'Please enter a room name.')
    books = Book.objects.all()
    return render(request, 'social/create_study_room.html', {'books': books})


@login_required
@approved_required
def join_study_room(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk, is_private=False)
    room.members.add(request.user)
    messages.success(request, f'Joined "{room.name}"!')
    return redirect('social:study_room_detail', pk=pk)


@login_required
@approved_required
def leave_study_room(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    room.members.remove(request.user)
    messages.success(request, f'Left "{room.name}".')
    return redirect('social:study_rooms')


@login_required
@approved_required
def delete_note(request, pk):
    note = get_object_or_404(StudyNote, pk=pk)
    if note.author != request.user and not request.user.can_manage_books:
        return JsonResponse({'error': 'Not allowed'}, status=403)
    room_pk = note.room_id
    note.delete()
    return redirect('social:study_room_detail', pk=room_pk)


@login_required
@approved_required
def like_note(request, pk):
    note = get_object_or_404(StudyNote, pk=pk)
    if request.user in note.likes.all():
        note.likes.remove(request.user)
        liked = False
    else:
        note.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': note.like_count})


@login_required
@approved_required
def pin_note(request, pk):
    note = get_object_or_404(StudyNote, pk=pk)
    if note.author == request.user or request.user.can_manage_books:
        note.is_pinned = not note.is_pinned
        note.save(update_fields=['is_pinned'])
    return redirect('social:study_room_detail', pk=note.room_id)


@login_required
@approved_required
def delete_study_room(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    # Only the creator may delete the room
    if room.created_by != request.user:
        messages.error(request, 'Only the room creator can delete this room.')
        return redirect('social:study_room_detail', pk=pk)
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Study room deleted.')
        return redirect('social:study_rooms')
    # simple confirmation page reuse: redirect back if not POST
    return render(request, 'social/confirm_delete_room.html', {'room': room})