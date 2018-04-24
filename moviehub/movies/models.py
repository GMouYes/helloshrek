from django.db import models
import os
# Create your models here.
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import math
import datetime
import shelve
class Movie(models.Model):
    Name=models.CharField(max_length=300)
    Year=models.CharField(max_length=5)
    Plot=models.CharField(max_length=1500)
    Genre=models.CharField(max_length=250)
    Imdb_rating=models.FloatField(default=0.0)
    rating_Count=models.IntegerField(default=0,null=True)
    Plot_outline=models.CharField(max_length=1000,default=None)
    Actor=models.CharField(max_length=250,default=None,null=True,blank=True)
    Director=models.CharField(max_length=300,default=None,null=True)
    Poster=models.FileField()
    Watched=models.BooleanField(default=False)
    trailer=models.CharField(max_length=150,default=None,null=True,blank=True)

    def rating_count(self):
        return self.rating_set.count()

    def sorted_ratings(self):
        rank_list = [(r['movie_id'], r['rating']) for r in self.rating_set.values()]
        return sorted(rank_list, key=lambda x: x[1], reverse=True)

    def avg_rating(self):
        ratings = [r['rating'] for r in self.rating_set.values()]
        num = self.rating_count()
        if num <= 0:
            return 0
        return sum(ratings) / num

    def __str__(self):
        return self.Name
def validate_movie_rating(value):
    if not 1 <= value <= 5:
        raise ValidationError("Rating must be between 1 and 5.")

class Rater(models.Model):
    age = models.IntegerField(default=0,null=True)
    gender = models.CharField(max_length=1,default=None)
    job = models.IntegerField(default=0,null=True)
    zip_code = models.CharField(max_length=255,default=None)
    user = models.OneToOneField(User,null=True,on_delete=models.CASCADE)

    # def rating_count(self):
    #     return self.rating_set.count()

    def avg_rating(self):
        ratings = [r['rating'] for r in self.rating_set.values()]
        num = self.rating_set.count()
        if num <= 0:
            return 0
        return num,sum(ratings) / num

    # def top_unseen(self, n=2):
    #     # all_movies = Movie.objects.all()
    #     # my_movies = self.my_movies()
    #     ratings = Rating.top_rated(n=None) # Sorted by rating
    #     # seen = self.rating_set
    #     # return unseen[:n]
    #     return [r.movie for r in ratings if r.movie not in self.my_movies()]

    def my_ratings(self):
        return Rating.objects.filter(rater=self.id)

    def my_movies(self):
        return [r.movie for r in self.my_ratings()]

    def ratings_vector(self):
        movies = Movie.objects.all().order_by('pk')
        vector = [0 for m in movies]
        for i in range(len(vector)):
            if movies[i] in self.my_movies():
                vector[i] = self.my_ratings().filter(movie=movies[i])[0].rating
        return vector

    @classmethod
    def create_users_for_raters(cls):
        for rater in Rater.objects.all():
            user = User.objects.create(
                username='user' + str(rater.id).zfill(5),
                password='password',
                # ^^ This method won't work -- need to use set_password()!
                email=str(rater.id) + '@example.com',
            )
            user.set_password('password')
            user.save()
            rater.user = user
            rater.save()

    def __str__(self):
        return self.id
class Rating(models.Model):
    rater = models.ForeignKey(Rater,on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[validate_movie_rating])
    time_added = models.CharField(max_length=250,default=None) # FIXME: Fixed (remove parens)
    # time_modified = models.DateTimeField(default=timezone.now) # FIXME: use auto_now_add instead?
    review = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = (('rater', 'movie'),)
    @classmethod
    def top_rated(cls, n=2):
        ratings = sorted(cls.objects.all(), key=lambda x: x.rating, reverse=True)
        # ratings = [(r.id, r.rating) for r in rating_objs]
        return ratings[:n] if n else ratings


    def __str__(self):
        return '{} - {}'.format('*' * self.rating, self.movie.Name)
