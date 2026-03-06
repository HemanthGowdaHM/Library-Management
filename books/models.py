import qrcode
import io
import requests
from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone


class Book(models.Model):
    title          = models.CharField(max_length=200, db_index=True)
    author         = models.CharField(max_length=200, db_index=True)
    isbn           = models.CharField(max_length=13, unique=True, db_index=True)
    published_date = models.DateField()
    quantity       = models.PositiveIntegerField(default=1)
    description    = models.TextField(blank=True)

    # ── NEW: Cover image (auto-fetched from Google Books API) ──
    cover_image    = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    cover_url      = models.URLField(blank=True)          # cached external URL fallback

    # ── NEW: QR code image ──
    qr_code        = models.ImageField(upload_to='book_qrcodes/', blank=True, null=True)

    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    added_by       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='books_added',
    )

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} — {self.author}"

    @property
    def available_copies(self):
        return self.quantity

    @property
    def is_available(self):
        return self.quantity > 0

    @property
    def cover(self):
        """Return best available cover: uploaded → external URL → None."""
        if self.cover_image:
            return self.cover_image.url
        if self.cover_url:
            return self.cover_url
        return None

    def fetch_cover_from_google(self):
        """Auto-fetch book cover from Google Books API using ISBN."""
        if self.cover_image or not self.isbn:
            return False
        try:
            url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{self.isbn}"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            items = data.get('items', [])
            if not items:
                return False
            image_links = items[0].get('volumeInfo', {}).get('imageLinks', {})
            # Prefer high-res thumbnail
            img_url = (
                image_links.get('extraLarge') or
                image_links.get('large')      or
                image_links.get('medium')     or
                image_links.get('thumbnail')
            )
            if img_url:
                # Upgrade to HTTPS and request larger size
                img_url = img_url.replace('http://', 'https://').replace('&zoom=1', '&zoom=0')
                img_resp = requests.get(img_url, timeout=8)
                if img_resp.status_code == 200:
                    fname = f"cover_{self.isbn}.jpg"
                    self.cover_image.save(fname, ContentFile(img_resp.content), save=False)
                    return True
                else:
                    # Store URL as fallback (no download)
                    self.cover_url = img_url
                    return True
        except Exception:
            pass
        return False

    def generate_qr_code(self):
        """Generate a QR code image encoding the book's detail URL."""
        try:
            book_url = f"{settings.SITE_URL}/books/{self.pk}/"
            qr = qrcode.QRCode(
                version=2,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(book_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#1a1a2e", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            fname = f"qr_{self.pk}.png"
            self.qr_code.save(fname, ContentFile(buf.getvalue()), save=False)
            return True
        except Exception:
            return False

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        changed = False
        if is_new or not self.cover_image:
            if self.fetch_cover_from_google():
                changed = True
        if is_new or not self.qr_code:
            if self.generate_qr_code():
                changed = True
        if changed:
            # Save again only for file fields
            Book.objects.filter(pk=self.pk).update(
                cover_image=self.cover_image,
                cover_url=self.cover_url,
                qr_code=self.qr_code,
            )


class Reservation(models.Model):
    """Student reserves a book that is currently out of stock."""

    class Status(models.TextChoices):
        PENDING   = 'PENDING',   'Pending'
        NOTIFIED  = 'NOTIFIED',  'Notified'
        FULFILLED = 'FULFILLED', 'Fulfilled'
        CANCELLED = 'CANCELLED', 'Cancelled'
        EXPIRED   = 'EXPIRED',   'Expired'

    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    book       = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    status     = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    notified_at= models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)   # 48h window to collect

    class Meta:
        ordering = ['created_at']
        unique_together = ['user', 'book', 'status']   # one active reservation per book per user

    def __str__(self):
        return f"{self.user.username} → {self.book.title} [{self.status}]"

    @property
    def queue_position(self):
        """How many people are ahead in queue for this book."""
        return Reservation.objects.filter(
            book=self.book,
            status=Reservation.Status.PENDING,
            created_at__lt=self.created_at,
        ).count() + 1

    def notify(self):
        """Mark as notified — book is now available for this person."""
        self.status = self.Status.NOTIFIED
        self.notified_at = timezone.now()
        self.expires_at  = timezone.now() + timezone.timedelta(hours=48)
        self.save()


class LibraryDocument(models.Model):
    """PDFs, question papers, notes and study material."""

    class DocType(models.TextChoices):
        PDF           = 'PDF',           'PDF / E-Book'
        QUESTION_CURR = 'QUESTION_CURR', 'Question Paper (Current Year)'
        QUESTION_PREV = 'QUESTION_PREV', 'Question Paper (Previous Year)'
        NOTES         = 'NOTES',         'Notes / Study Material'
        OTHER         = 'OTHER',         'Other'

    title       = models.CharField(max_length=200)
    doc_type    = models.CharField(max_length=20, choices=DocType.choices, default=DocType.PDF)
    subject     = models.CharField(max_length=100, blank=True)
    department  = models.CharField(max_length=100, blank=True)
    year        = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    file        = models.FileField(upload_to='library_docs/%Y/%m/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documents_uploaded',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_public   = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.get_doc_type_display()} — {self.title}"

    @property
    def file_extension(self):
        import os
        _, ext = os.path.splitext(self.file.name)
        return ext.lower()

    @property
    def is_pdf(self):
        return self.file_extension == '.pdf'