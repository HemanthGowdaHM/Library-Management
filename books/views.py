from django.shortcuts import render

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Book
from .forms import BookForm
 
from django.db.models import Q
# Create your views here.


# class BookListView(ListView):
#     model = Book
#     template_name = 'books/book_list.html'
#     context_object_name = 'books'

from django.views.generic import ListView
from django.db.models import Q
from .models import Book


class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    ordering = ['-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context
    
    
class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:book_list')
    
    def form_valid(self,form):
        messages.success(self.request, "Book added successfully!")
        return super().form_valid(form)
    
    
class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:book_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Book Updated successfully!")
        return super().form_valid(form)
    

class BookDeleteView(DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('books:book_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Book deleted successfully!")
        return super().form_valid(form)

    

def invalid_url_view(request, *args, **kwargs):
    return render(request, 'books/invalid_url.html', status=404)