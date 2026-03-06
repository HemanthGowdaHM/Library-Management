from django.db import models
from django.conf import settings


class BookReview(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    book    = models.ForeignKey('books.Book', on_delete=models.CASCADE, related_name='reviews')
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating  = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    title   = models.CharField(max_length=120, blank=True)
    body    = models.TextField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # ✅ Make sure this line exists in your model:
    likes   = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_reviews',
        blank=True
    )

    class Meta:
        ordering = ['-created']
        unique_together = ['book', 'user']

    def __str__(self):
        return f"{self.user.username} → {self.book.title} ({self.rating}★)"

    @property
    def like_count(self):
        return self.likes.count()



class ReadingList(models.Model):
    owner       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reading_lists')
    title       = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_public   = models.BooleanField(default=True)
    books       = models.ManyToManyField('books.Book', blank=True, related_name='reading_lists')
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return f"{self.owner.username}: {self.title}"

class Discussion(models.Model):
    book      = models.ForeignKey('books.Book', on_delete=models.CASCADE,
                                   related_name='discussions', null=True, blank=True)
    document  = models.ForeignKey('books.LibraryDocument', on_delete=models.CASCADE,
                                   related_name='discussions', null=True, blank=True)
    author    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='discussions')
    title     = models.CharField(max_length=200)
    body      = models.TextField(max_length=2000)
    created   = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)
    views     = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_pinned', '-created']

    def __str__(self):
        return self.title

    @property
    def reply_count(self):
        return self.replies.count()


class DiscussionReply(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='replies')
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body       = models.TextField()
    created    = models.DateTimeField(auto_now_add=True)
    likes      = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_replies')

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"Reply by {self.author} on {self.discussion}"

    @property
    def like_count(self):
        return self.likes.count()


class StudyRoom(models.Model):
    book        = models.ForeignKey('books.Book', on_delete=models.CASCADE,
                                     related_name='study_rooms', null=True, blank=True)
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rooms_created')
    name        = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    members     = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='study_rooms')
    is_private  = models.BooleanField(default=False)
    created     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()


class StudyNote(models.Model):
    room    = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='notes')
    author  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body    = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    is_pinned = models.BooleanField(default=False)
    likes     = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_notes')

    class Meta:
        ordering = ['created']

    @property
    def like_count(self):
        return self.likes.count()