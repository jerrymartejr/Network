from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    body = models.CharField(max_length=3000)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")

    # https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} posted: '{self.body}' on {self.timestamp.strftime('%b %d %Y, %I:%M %p')}"


class Following(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")

    def __str__(self):
        return f"{self.follower} follows {self.followed}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return f"{self.user} likes {self.post}"

