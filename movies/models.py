from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')

    def __str__(self):
        return str(self.id) + ' - ' + self.name

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reported = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
    
class MovieRating(models.Model):
    choicesRating = [(1, 'Thumbs Up'),(0, 'Thumbs Down')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    thumb = models.IntegerField(choices=choicesRating)
    class Meta:
        unique_together = ('user', 'movie')
    def __str__(self):
        return f"{self.user.username} - {self.movie.name} - {'Up' if self.thumb else 'Down'}"