#coding:utf-8
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from .models import Movie,Rating,Rater
import time
from moviehub import celery_app
import time
from .Recommend import Recommend
@celery_app.task
def sendmail(email):
    print('start send email to %s' % email)
    time.sleep(5) #休息5秒
    print('success')
    return email

@celery_app.task
def add(x):
    a=0
    for i in range(x):
            a += i
    time.sleep(5) #休息5秒
    print(a)
    return a

@celery_app.task
def movie_rec(userid,movieid):
    from multiprocessing import current_process
    try:
        current_process()._config
    except AttributeError:
        current_process()._config = {'semprefix': '/mp'}

    recommend = Recommend()
    idarg=[]
    idarg.append(userid)
    idarg.append(movieid)
    returnlist = recommend.do_rec('D:/moviehub/ml-1m/ratings.csv',idarg, 2)
    import json
    json.dump(returnlist)
    print(json.dump(returnlist))
    # rec_movies=[get_object_or_404(Movie,id=id) for id in returnlist ]
    # if len(rec_movies)>3:
    #     paginator = Paginator(rec_movies, 4) # Show 4 movies per page
    #     page = request.GET.get('page')
    #     movies = paginator.get_page(page)
    return json.dump(returnlist)
