# Library Management System

A Django-based web application for managing a library's book collection. This project provides a user-friendly interface to create, read, update, and delete book records with search functionality.

## Features

- **Book Management**: Create, view, update, and delete book records
- **Search Functionality**: Search for books by title
- **Database-Indexed Fields**: Optimized queries for title, author, and ISBN
- **Responsive Design**: Built with Django templates for a clean user interface
- **Admin Panel**: Django admin interface for administrative tasks
- **Validation**: Form validation for book data entry
- **Timestamps**: Automatic tracking of creation and update times

## Technology Stack

- **Backend**: Django 6.0.2
- **Database**: SQLite3
- **Frontend**: HTML/CSS with Django Templates
- **Python**: 3.x

## Project Structure

```
library_project/
├── books/                          # Main app for book management
│   ├── migrations/                 # Database migrations
│   ├── templates/books/            # HTML templates
│   │   ├── book_list.html         # List all books
│   │   ├── book_form.html         # Create/Edit book form
│   │   ├── book_confirm_delete.html # Delete confirmation
│   │   └── invalid_url.html       # Error page
│   ├── models.py                  # Book model definition
│   ├── views.py                   # View logic (CRUD operations)
│   ├── forms.py                   # Book form definition
│   ├── urls.py                    # URL routing
│   ├── admin.py                   # Django admin configuration
│   └── tests.py                   # Test cases
├── library_project/               # Project configuration
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Main URL configuration
│   ├── wsgi.py                   # WSGI configuration
│   └── asgi.py                   # ASGI configuration
├── static/                        # Static files (CSS, JS, images)
├── templates/
│   └── base.html                # Base template for inheritance
├── db.sqlite3                    # SQLite database
├── manage.py                     # Django management script
└── README.md                     # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository** (if applicable)
   ```bash
   cd library_project
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install django
   ```

5. **Run migrations** (if needed)
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (for admin access)
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

   The application will be available at `http://127.0.0.1:8000/`

## Usage

### Accessing the Application

- **Book List**: `http://127.0.0.1:8000/books/`
- **Add Book**: `http://127.0.0.1:8000/books/add/`
- **Edit Book**: `http://127.0.0.1:8000/books/edit/<id>/`
- **Delete Book**: `http://127.0.0.1:8000/books/delete/<id>/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`

### Search Books

1. Navigate to the book list page
2. Enter a book title in the search field
3. The results will be filtered in real-time

### Add a New Book

1. Click on "Add Book" button
2. Fill in the book details:
   - Title
   - Author
   - ISBN (13 digits, must be unique)
   - Published Date
   - Quantity
3. Click "Save" to add the book

### Edit a Book

1. Click on the "Edit" button next to a book
2. Modify the book information
3. Click "Save" to update

### Delete a Book

1. Click on the "Delete" button next to a book
2. Confirm the deletion
3. The book will be permanently removed

## Book Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | CharField | Book title (max 200 characters, indexed) |
| `author` | CharField | Author name (max 200 characters, indexed) |
| `isbn` | CharField | ISBN code (13 characters, unique, indexed) |
| `published_date` | DateField | Date the book was published |
| `quantity` | PositiveIntegerField | Number of copies available (default: 1) |
| `created_at` | DateTimeField | Timestamp when record was created |
| `updated_at` | DateTimeField | Timestamp when record was last updated |

## Admin Panel Features

The Django admin panel allows administrators to:
- View all books in the database
- Add, edit, and delete books directly
- Filter books by creation date
- Search books by title and author

Access the admin panel at `/admin/` with superuser credentials.

## Development

### Running Tests

```bash
python manage.py test
```

### Database Migrations

Create new migrations:
```bash
python manage.py makemigrations
```

Apply migrations:
```bash
python manage.py migrate
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

## Troubleshooting

**Issue**: Database locked error
- **Solution**: Delete `db.sqlite3` and run `python manage.py migrate` again

**Issue**: Static files not loading
- **Solution**: Run `python manage.py collectstatic`

**Issue**: Port 8000 already in use
- **Solution**: Run on a different port: `python manage.py runserver 8001`

## Future Enhancements

- Add book categories/genres
- Implement user authentication for borrowing
- Add book reviews and ratings
- Implement pagination for large book lists
- Add book cover images
- Export book list to CSV/PDF
- Add book recommendations
- Implement barcode scanning

## License

This project is open source and available for educational purposes.

## Contributing

Contributions are welcome! Please feel free to:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For questions or issues, please feel free to open an issue in the repository.

---

**Last Updated**: February 2026
