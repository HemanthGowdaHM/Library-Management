from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from .models import Book, LibraryDocument
from .forms import BookForm, LibraryDocumentForm
from accounts.decorators import approved_required, staff_required


# ─────────────────────────────────────────────
#  PERMISSION HELPER
# ─────────────────────────────────────────────

def require_staff(request):
    """Raise 403 if user is not Admin / Librarian."""
    if not request.user.can_manage_books:
        raise PermissionDenied


# ─────────────────────────────────────────────
#  BOOK VIEWS
# ─────────────────────────────────────────────

@login_required
@approved_required
def book_list(request):
    query = request.GET.get('q', '')
    books = Book.objects.all()
    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query)
        )
    return render(request, 'books/book_list.html', {
        'books': books,
        'query': query,
        'can_manage': request.user.can_manage_books,
    })


@login_required
@approved_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/book_detail.html', {
        'book': book,
        'can_manage': request.user.can_manage_books,
    })


@login_required
@approved_required
def add_book(request):
    require_staff(request)          # 🔒 Students & Teachers blocked
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.added_by = request.user
            book.save()
            messages.success(request, f"'{book.title}' added to the catalogue.")
            return redirect('books:book_list')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form, 'action': 'Add'})


@login_required
@approved_required
def edit_book(request, pk):
    require_staff(request)          # 🔒 Students & Teachers blocked
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
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
    require_staff(request)          # 🔒 Students & Teachers blocked
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f"'{title}' deleted.")
        return redirect('books:book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})


# ─────────────────────────────────────────────
#  DOCUMENT VIEWS (PDFs, Question Papers, etc.)
# ─────────────────────────────────────────────

@login_required
@approved_required
def document_list(request):
    """All approved members can browse documents."""
    doc_type = request.GET.get('type', '')
    dept     = request.GET.get('dept', '')
    query    = request.GET.get('q', '')

    docs = LibraryDocument.objects.filter(is_public=True)

    if doc_type:
        docs = docs.filter(doc_type=doc_type)
    if dept:
        docs = docs.filter(department__icontains=dept)
    if query:
        docs = docs.filter(
            Q(title__icontains=query) |
            Q(subject__icontains=query) |
            Q(description__icontains=query)
        )

    # Group question papers by type for convenience
    qp_current  = docs.filter(doc_type='QUESTION_CURR').count()
    qp_previous = docs.filter(doc_type='QUESTION_PREV').count()
    departments = LibraryDocument.objects.values_list('department', flat=True).distinct().exclude(department='')

    return render(request, 'books/document_list.html', {
        'docs': docs,
        'doc_types': LibraryDocument.DocType.choices,
        'departments': departments,
        'selected_type': doc_type,
        'selected_dept': dept,
        'query': query,
        'qp_current': qp_current,
        'qp_previous': qp_previous,
        'can_manage': request.user.can_manage_books,
    })


@login_required
@approved_required
def upload_document(request):
    require_staff(request)          # 🔒 Students & Teachers blocked
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
    require_staff(request)          # 🔒 Students & Teachers blocked
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
    require_staff(request)          # 🔒 Students & Teachers blocked
    doc = get_object_or_404(LibraryDocument, pk=pk)
    if request.method == 'POST':
        title = doc.title
        doc.file.delete(save=False)   # delete physical file
        doc.delete()
        messages.success(request, f"'{title}' deleted.")
        return redirect('books:document_list')
    return render(request, 'books/document_confirm_delete.html', {'doc': doc})