# Library Management System

A comprehensive Django-based web application for managing a library's operations, including book cataloging, user management, document storage, and book borrowing with fine tracking system. This project provides a multi-role access system with role-based permissions for Admins, Librarians, Teachers, and Students.

## Features

### User Management
- **Role-Based Access Control**: Admin, Librarian, Teacher, and Student roles
- **User Registration & Approval**: New users register and await admin approval
- **User Profiles**: Upload profile pictures, manage personal information
- **Account Management**: Change password, update profile details
- **User Status Tracking**: Active members, pending approvals, department assignments

### Book Management
- **Book Catalog**: Create, view, update, and delete book records
- **Book Quantity Tracking**: Track available copies of each book
- **Advanced Search**: Search by title, author, or ISBN with filters
- **Database-Indexed Fields**: Optimized queries for title, author, and ISBN
- **Book Details**: ISBN, publication date, quantity, and description

### Book Borrowing System
- **Borrow/Return Tracking**: Track all borrow and return transactions
- **Due Date Management**: Automatic due date assignment and tracking
- **Overdue Detection**: Automatic marking of overdue books
- **Fine Calculation**: ₹5 per day fine for overdue books
- **Borrowing History**: View complete borrowing history
- **Borrow Status**: Track borrowed, returned, overdue, and reserved status

### Library Documents
- **Multiple Document Types**: PDFs, E-books, Question Papers (Current/Previous Year), Notes, Study Materials
- **Subject & Department Filtering**: Organize documents by subject and department
- **File Management**: Upload, edit, and delete documents
- **Access Control**: Visibility settings for public/private documents
- **Document Search**: Search by title, subject, or description

### Admin/Librarian Dashboard
- **Activity Monitoring**: Track recent borrowing activity
- **User Management**: Approve/deny registrations, manage user accounts
- **Statistics**: View total users, pending approvals, active borrows
- **Activity Search**: Filter borrowing records by user or book
- **Document Management**: Upload and manage library documents

### Additional Features
- **Responsive Design**: Built with Django templates for clean UI
- **Admin Panel**: Django admin interface for administrative tasks
- **Form Validation**: Comprehensive validation for all user inputs
- **Timestamps**: Automatic tracking of creation and update times
- **Email-style UI**: Clean, professional interface design

## Technology Stack

- **Backend**: Django 6.0.2
- **Database**: SQLite3
- **Frontend**: HTML/CSS with Django Templates
- **Python**: 3.8+
- **Authentication**: Django's built-in authentication system with custom user model
- **File Handling**: FileField for document storage, ImageField for profile pictures

## Project Structure

```
library_project/
├── accounts/                                # User authentication & management
│   ├── migrations/                         # Database migrations
│   ├── templates/accounts/                # HTML templates
│   │   ├── register.html                 # User registration
│   │   ├── login.html                    # User login
│   │   ├── dashboard.html                # User/Admin dashboard
│   │   ├── profile.html                  # User profile page
│   │   ├── change_password.html          # Password change
│   │   ├── borrow_history.html           # Borrowing history
│   │   ├── manage_users.html             # User management (Admin)
│   │   ├── approve_user.html             # User approval (Admin)
│   │   ├── issue_book.html               # Issue book (Admin)
│   │   ├── return_book.html              # Return book (Admin)
│   │   ├── pending_approval.html         # Pending approval notice
│   │   └── delete_user.html              # Delete user (Admin)
│   ├── models.py                         # CustomUser, BorrowRecord models
│   ├── views.py                          # Authentication & user management views
│   ├── forms.py                          # Registration, login, profile forms
│   ├── decorators.py                     # Custom decorators (approved_required, staff_required)
│   ├── urls.py                           # URL routing
│   ├── admin.py                          # Django admin configuration
│   └── tests.py                          # Test cases
│
├── books/                                  # Book & document management
│   ├── migrations/                        # Database migrations
│   ├── templates/books/                  # HTML templates
│   │   ├── book_list.html               # List all books
│   │   ├── book_form.html               # Create/Edit book form
│   │   ├── book_confirm_delete.html     # Delete confirmation
│   │   ├── document_list.html           # List all documents
│   │   ├── document_form.html           # Upload/Edit document form
│   │   ├── document_confirm_delete.html # Delete document confirmation
│   │   └── invalid_url.html             # Error page
│   ├── models.py                        # Book, LibraryDocument models
│   ├── views.py                         # CRUD operations for books & documents
│   ├── forms.py                         # Book and LibraryDocument forms
│   ├── urls.py                          # URL routing
│   ├── admin.py                         # Django admin configuration
│   └── tests.py                         # Test cases
│
├── library_project/                       # Main project configuration
│   ├── settings.py                      # Django settings
│   ├── urls.py                          # Main URL configuration
│   ├── wsgi.py                          # WSGI configuration
│   └── asgi.py                          # ASGI configuration
│
├── media/                                 # User-uploaded files
│   ├── library_docs/                    # Documents storage (organized by date)
│   └── profiles/                        # User profile pictures
│
├── static/                                # Static files (CSS, JS, images)
├── templates/
│   ├── base.html                        # Base template for inheritance
│   ├── 403.html                         # Permission denied page
│   ├── 404.html                         # Page not found page
│   ├── 500.html                         # Server error page
│   └── accounts/                        # Account-related templates
│
├── db.sqlite3                            # SQLite database
├── manage.py                             # Django management script
└── README.md                             # This file
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

### Getting Started

1. **Register an Account**
   - Navigate to `/accounts/register/`
   - Fill in your details and submit
   - Wait for admin approval

2. **Login**
   - Go to `/accounts/login/`
   - Enter your credentials
   - You'll be redirected to your dashboard

### User Roles and Permissions

#### Student / Teacher
- View books in the catalog
- Search for books by title, author, or ISBN
- View borrowing history
- View and manage personal profile
- Browse library documents (PDFs, notes, question papers)

#### Librarian
- All student/teacher permissions plus:
- Add new books to the catalog
- Edit existing book details
- Delete books from the catalog
- Issue/return books for users
- Upload and manage library documents
- View dashboard with borrowing activity

#### Admin
- All librarian permissions plus:
- Approve/deny user registrations
- Create new user accounts
- Manage user roles and access
- Delete user accounts
- Delete users
- Full activity monitoring and reporting

### Main Endpoints

#### Authentication
- `/accounts/register/` - User registration
- `/accounts/login/` - User login
- `/accounts/logout/` - User logout
- `/accounts/pending-approval/` - Pending approval notice

#### User Management
- `/accounts/dashboard/` - User dashboard (shows personalized info)
- `/accounts/profile/` - User profile page
- `/accounts/change-password/` - Change password
- `/accounts/borrow-history/` - View borrowing history
- `/accounts/manage-users/` (Admin) - Manage all users
- `/accounts/approve-user/<id>/` (Admin) - Approve user registration
- `/accounts/delete-user/<id>/` (Admin) - Delete user account

#### Book Management
- `/books/` - View all books with search
- `/books/add/` (Librarian/Admin) - Add new book
- `/books/edit/<id>/` (Librarian/Admin) - Edit book details
- `/books/delete/<id>/` (Librarian/Admin) - Delete book

#### Documents
- `/books/documents/` - Browse all documents
- `/books/documents/upload/` (Librarian/Admin) - Upload document
- `/books/documents/edit/<id>/` (Librarian/Admin) - Edit document
- `/books/documents/delete/<id>/` (Librarian/Admin) - Delete document

#### Book Borrowing (Admin/Librarian only)
- `/accounts/issue-book/` - Issue a book to a user
- `/accounts/return-book/` - Mark a book as returned

#### Admin
- `/admin/` - Django admin panel

### Searching Books

1. Navigate to `/books/`
2. Use the search box to search by:
   - Book title
   - Author name
   - ISBN
3. Results are filtered in real-time

### Borrowing Books

**For Users/Students:**
- Request books through your dashboard
- View due dates and fine amounts
- Check your borrowing history

**For Librarians/Admins:**
1. Navigate to `/accounts/issue-book/`
2. Select the user and book
3. Set the due date
4. System automatically creates a borrow record
5. To return: Go to `/accounts/return-book/` and mark as returned

### Managing Library Documents

**Browsing:**
1. Go to `/books/documents/`
2. Filter by:
   - Document type (PDF, Question Papers, Notes, etc.)
   - Department
   - Search by title or subject

**Uploading (Librarian/Admin only):**
1. Click "Upload Document"
2. Fill in document details:
   - Title
   - Document type
   - Subject/Course
   - Department
   - Exam year (for question papers)
3. Select and upload the file
4. Click "Upload"

### Managing Users (Admin only)

1. Navigate to `/accounts/manage-users/`
2. Filter by role or approval status
3. Click on a user to view details
4. Approve, edit, or delete users as needed

### User Profile Management

1. Go to `/accounts/profile/`
2. Update your information:
   - Profile picture
   - Phone number
   - Department
   - Student ID
3. View your account information
4. Change your password from the profile page


## Data Models

### CustomUser Model

Extended Django User model with library-specific features.

| Field | Type | Description |
|-------|------|-------------|
| `role` | CharField | User role: Admin, Librarian, Teacher, Student |
| `phone_number` | CharField | User's contact number |
| `department` | CharField | User's department (e.g., "Computer Science") |
| `student_id` | CharField | Unique student ID (optional, unique) |
| `profile_picture` | ImageField | User's profile picture |
| `is_approved` | BooleanField | Admin approval status for new members |
| `date_of_joining` | DateField | Auto-set account creation date |

**Helper Methods:**
- `is_admin_role`, `is_librarian`, `is_teacher`, `is_student` - Role checkers
- `can_manage_books` - Returns True if Admin or Librarian

### Book Model

| Field | Type | Description |
|-------|------|-------------|
| `title` | CharField | Book title (max 200 characters, indexed) |
| `author` | CharField | Author name (max 200 characters, indexed) |
| `isbn` | CharField | ISBN code (13 characters, unique, indexed) |
| `published_date` | DateField | Date the book was published |
| `quantity` | PositiveIntegerField | Number of copies available (default: 1) |
| `description` | TextField | Book description (optional) |
| `added_by` | ForeignKey | Reference to user who added the book |
| `created_at` | DateTimeField | Timestamp when record was created |
| `updated_at` | DateTimeField | Timestamp when record was last updated |

### BorrowRecord Model

Tracks every borrow/return transaction with automatic fine calculation.

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | Reference to CustomUser |
| `book` | ForeignKey | Reference to Book |
| `status` | CharField | Borrowed, Returned, Overdue, or Reserved |
| `borrowed_date` | DateTimeField | Auto-set when record is created |
| `due_date` | DateField | When the book should be returned |
| `returned_date` | DateTimeField | When book was actually returned (nullable) |
| `fine_amount` | DecimalField | Fine amount in rupees |
| `notes` | TextField | Additional notes (optional) |

**Methods:**
- `calculate_fine()` - Calculates fine at ₹5 per day after due date

### LibraryDocument Model

Store PDFs, question papers, notes, and study materials.

| Field | Type | Description |
|-------|------|-------------|
| `title` | CharField | Document title |
| `doc_type` | CharField | PDF, Question Paper (Current/Previous), Notes, Other |
| `subject` | CharField | Subject/Course name (optional) |
| `department` | CharField | Department name (optional) |
| `year` | PositiveIntegerField | Exam year for question papers (optional) |
| `description` | TextField | Document description (optional) |
| `file` | FileField | Uploaded file (stored in media/library_docs/) |
| `uploaded_by` | ForeignKey | Reference to user who uploaded the document |
| `uploaded_at` | DateTimeField | Auto-set when uploaded |
| `is_public` | BooleanField | Visibility setting (default: True) |

**Properties:**
- `file_extension` - Returns file extension
- `is_pdf` - Returns True if file is PDF

## Admin Panel Features

The Django admin panel (`/admin/`) allows administrators to:

- **User Management**: View, filter, and edit all CustomUser records
- **Book Management**: View, add, edit, and delete books
- **Borrow Records**: Monitor all borrowing transactions
- **Documents**: Manage library documents
- **Approval Status**: Filter users by approval status
- **Advanced Filtering**: Filter by role, department, approval status, etc.

Access the admin panel at `/admin/` with superuser/admin credentials.

## Authentication & Authorization

### Decorators Used

- `@approved_required` - Only approved members can access (enforces `is_approved=True`)
- `@staff_required` - Only Admins and Librarians can access (enforces `can_manage_books`)
- `@admin_required` - Only Admins can access (enforces `is_admin_role`)
- `@login_required` - Only authenticated users can access

### Permission System

```
Public Endpoints:
├── Register
├── Login
└── Pending Approval

Approved Members:
├── Dashboard (personalized view)
├── Profile Management
├── Book List & Search
├── Document Browser
├── Borrow History
└── Borrowing Status

Staff (Admin/Librarian):
├── All Approved Member endpoints
├── Add/Edit/Delete Books
├── Upload/Edit/Delete Documents
├── Issue/Return Books
└── View Activity Dashboard

Admin Only:
├── All Staff endpoints
├── Manage All Users
├── Approve/Deny Registrations
├── Delete User Accounts
└── Create New User Accounts
``
```

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

- Add book categories and genres with filtering
- Implement book reservations system
- Add book cover images and thumbnails
- Export documents list to PDF/CSV
- Email notifications for due dates and overdue books
- SMS notifications for important events
- Implement advanced fine collection system
- Add book recommendations based on history
- Implement barcode/QR code scanning for quick issue/return
- Add librarian notes/comments on books
- Implement book rating and review system
- Add dashboard analytics and reporting
- Implement API for mobile app integration
- Add multi-language support
- Implement automated email reminders for overdue books
- Add book availability calendar
- Implement inter-library book transfer system

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

**Last Updated**: March 2026
