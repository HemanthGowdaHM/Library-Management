import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.utils import timezone

from .models import Book, Reservation, LibraryDocument
from .forms import BookForm, LibraryDocumentForm
from accounts.decorators import approved_required, staff_required
from accounts.models import BorrowRecord


def require_staff(request):
    if not request.user.can_manage_books:
        raise PermissionDenied


# ── BOOK LIST ──────────────────────────────────────────────────────────────

@login_required
@approved_required
def book_list(request):
    query  = request.GET.get('q', '')
    avail  = request.GET.get('avail', '')
    books  = Book.objects.all()

    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query))
    if avail == '1':
        books = books.filter(quantity__gt=0)

    # Annotate each book with user's active reservation
    user_reservations = {}
    if request.user.is_authenticated:
        for r in Reservation.objects.filter(
            user=request.user, status__in=['PENDING','NOTIFIED']
        ).select_related('book'):
            user_reservations[r.book_id] = r

    book_data = []
    for b in books:
        book_data.append({
            'book': b,
            'reservation': user_reservations.get(b.pk),
        })

    return render(request, 'books/book_list.html', {
        'book_data': book_data,
        'query': query,
        'avail': avail,
        'can_manage': request.user.can_manage_books,
    })


# ── BOOK DETAIL ─────────────────────────────────────────────────────────────

@login_required
@approved_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    user_reservation = Reservation.objects.filter(
        user=request.user, book=book, status__in=['PENDING','NOTIFIED']
    ).first()
    queue_count = Reservation.objects.filter(book=book, status='PENDING').count()
    return render(request, 'books/book_detail.html', {
        'book': book,
        'can_manage': request.user.can_manage_books,
        'user_reservation': user_reservation,
        'queue_count': queue_count,
    })


# ── ADD / EDIT / DELETE BOOK ─────────────────────────────────────────────────

@login_required
@approved_required
def add_book(request):
    require_staff(request)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.added_by = request.user
            book.save()
            messages.success(request, f"'{book.title}' added. Cover and QR code generated automatically.")
            return redirect('books:book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form, 'action': 'Add'})


@login_required
@approved_required
def edit_book(request, pk):
    require_staff(request)
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{book.title}' updated.")
            return redirect('books:book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'action': 'Edit', 'book': book})


@login_required
@approved_required
def delete_book(request, pk):
    require_staff(request)
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f"'{title}' deleted.")
        return redirect('books:book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})


# ── QR CODE VIEW ─────────────────────────────────────────────────────────────

@login_required
@approved_required
def book_qr(request, pk):
    """Serve the QR code image, or redirect to book detail."""
    book = get_object_or_404(Book, pk=pk)
    if not book.qr_code:
        book.generate_qr_code()
        book.save(update_fields=['qr_code'])
    if book.qr_code:
        return redirect(book.qr_code.url)
    return redirect('books:book_detail', pk=pk)


@login_required
@staff_required
def qr_scanner(request):
    """Page that opens the camera for QR scanning."""
    return render(request, 'books/qr_scanner.html')


# ── ISBN LOOKUP AJAX ─────────────────────────────────────────────────────────

@login_required
@staff_required
def isbn_lookup(request):
    """AJAX: Look up book info from Google Books API by ISBN."""
    isbn = request.GET.get('isbn', '').strip().replace('-', '')
    if len(isbn) not in (10, 13):
        return JsonResponse({'error': 'Invalid ISBN length'}, status=400)
    try:
        url  = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        resp = requests.get(url, timeout=6)
        data = resp.json()
        items = data.get('items', [])
        if not items:
            return JsonResponse({'error': 'No book found for this ISBN'}, status=404)
        info = items[0]['volumeInfo']
        image_links = info.get('imageLinks', {})
        cover = (
            image_links.get('extraLarge') or image_links.get('large') or
            image_links.get('medium')     or image_links.get('thumbnail', '')
        )
        published = info.get('publishedDate', '')[:10]   # take YYYY-MM-DD part
        return JsonResponse({
            'title':     info.get('title', ''),
            'author':    ', '.join(info.get('authors', [])),
            'published': published,
            'description': info.get('description', '')[:400],
            'cover':     cover.replace('http://', 'https://'),
            'isbn':      isbn,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ── RESERVATION ───────────────────────────────────────────────────────────────

@login_required
@approved_required
def reserve_book(request, pk):
    """Student reserves a book that is out of stock."""
    book = get_object_or_404(Book, pk=pk)

    if book.is_available:
        messages.info(request, f"'{book.title}' is currently available — ask the librarian to issue it directly.")
        return redirect('books:book_detail', pk=pk)

    existing = Reservation.objects.filter(
        user=request.user, book=book, status__in=['PENDING','NOTIFIED']
    ).first()
    if existing:
        messages.warning(request, f"You already have a reservation for '{book.title}' (#{existing.queue_position} in queue).")
        return redirect('books:book_detail', pk=pk)

    if request.method == 'POST':
        reservation = Reservation.objects.create(user=request.user, book=book)
        messages.success(request, f"Reserved! You are #{reservation.queue_position} in the queue for '{book.title}'.")
        return redirect('books:book_detail', pk=pk)

    queue_count = Reservation.objects.filter(book=book, status='PENDING').count()
    return render(request, 'books/reserve_confirm.html', {
        'book': book,
        'queue_position': queue_count + 1,
    })


@login_required
@approved_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == 'POST':
        reservation.status = Reservation.Status.CANCELLED
        reservation.save()
        messages.success(request, f"Reservation for '{reservation.book.title}' cancelled.")
        return redirect('books:book_list')
    return render(request, 'books/cancel_reservation.html', {'reservation': reservation})


@login_required
@approved_required
def my_reservations(request):
    reservations = Reservation.objects.filter(
        user=request.user
    ).exclude(status__in=['CANCELLED','EXPIRED']).select_related('book').order_by('-created_at')
    return render(request, 'books/my_reservations.html', {'reservations': reservations})


# ── STAFF: manage reservations ──────────────────────────────────────────────

@login_required
@staff_required
def all_reservations(request):
    reservations = Reservation.objects.filter(
        status__in=['PENDING','NOTIFIED']
    ).select_related('user','book').order_by('book__title','created_at')
    return render(request, 'books/all_reservations.html', {'reservations': reservations})


@login_required
@staff_required
def notify_reservation(request, pk):
    """Mark first-in-queue as notified when book becomes available."""
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        reservation.notify()
        messages.success(request, f"Notified {reservation.user.get_full_name() or reservation.user.username} that '{reservation.book.title}' is ready.")
    return redirect('books:all_reservations')


# ── DOCUMENT VIEWS (unchanged) ───────────────────────────────────────────────

@login_required
@approved_required
def document_list(request):
    doc_type = request.GET.get('type', '')
    dept     = request.GET.get('dept', '')
    query    = request.GET.get('q', '')
    docs     = LibraryDocument.objects.filter(is_public=True)
    if doc_type: docs = docs.filter(doc_type=doc_type)
    if dept:     docs = docs.filter(department__icontains=dept)
    if query:    docs = docs.filter(Q(title__icontains=query)|Q(subject__icontains=query))
    departments = LibraryDocument.objects.values_list('department',flat=True).distinct().exclude(department='')
    return render(request, 'books/document_list.html', {
        'docs': docs,
        'doc_types': LibraryDocument.DocType.choices,
        'departments': departments,
        'selected_type': doc_type, 'selected_dept': dept, 'query': query,
        'qp_current':  docs.filter(doc_type='QUESTION_CURR').count(),
        'qp_previous': docs.filter(doc_type='QUESTION_PREV').count(),
        'can_manage':  request.user.can_manage_books,
    })


@login_required
@approved_required
def upload_document(request):
    require_staff(request)
    if request.method == 'POST':
        form = LibraryDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, f"'{doc.title}' uploaded successfully.")
            return redirect('books:document_list')
    else:
        form = LibraryDocumentForm()
    return render(request, 'books/document_form.html', {'form': form, 'action': 'Upload'})


@login_required
@approved_required
def edit_document(request, pk):
    require_staff(request)
    doc = get_object_or_404(LibraryDocument, pk=pk)
    if request.method == 'POST':
        form = LibraryDocumentForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{doc.title}' updated.")
            return redirect('books:document_list')
    else:
        form = LibraryDocumentForm(instance=doc)
    return render(request, 'books/document_form.html', {'form': form, 'action': 'Edit', 'doc': doc})


@login_required
@approved_required
def delete_document(request, pk):
    require_staff(request)
    doc = get_object_or_404(LibraryDocument, pk=pk)
    if request.method == 'POST':
        doc.file.delete(save=False)
        doc.delete()
        messages.success(request, "Document deleted.")
        return redirect('books:document_list')
    return render(request, 'books/document_confirm_delete.html', {'doc': doc})