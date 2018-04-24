
# -- coding: utf-8 --
# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Movie,Rating,Rater
from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import threading
import os
import re
import time
from .task import sendmail,movie_rec,add #import tasks.py sendmail def

def get_youtube_link(movie):
    query = quote_plus(movie.Name)
    f =urlopen('https://www.youtube.com/results?search_query='+query+'+trailer').read()
    soup=BeautifulSoup(f,'lxml')
    item = soup.find_all('ol',{'class':'item-section'})
    for itm in item:
        a = item[0].find_all('a',{'class':'yt-uix-sessionlink'})[0]
    a = re.findall('=(.*)',a.get('href'))
    print (a)
    link= 'http://www.youtube.com/embed/'+a[0]
    movie.trailer=link
    movie.save()

def top_rated(cls):
    movies = sorted(cls, key=lambda x: x.Imdb_rating, reverse=True)
    return movies
def toprate(movielist):
    movielist1=[movie for movie in movielist if movie.Imdb_rating]
    movielist1=[movie for movie in movielist if movie.rating_Count and movie.rating_Count>10000]
    movielist1=top_rated(movielist1)
    movie_rem=list(set(movielist).difference(set(movielist1)))
    movielist=[*movielist1,*movie_rem]
    return movielist

def top_viewed(cls):
    movies = sorted(cls, key=lambda x: x.rating_Count, reverse=True)
    return movies

def topview(movielist):

    movielist1=[movie for movie in movielist if movie.Imdb_rating]
    movielist1=[movie for movie in movielist if movie.rating_Count and movie.rating_Count>10000]
    movielist1=top_viewed(movielist1)
    movie_rem=list(set(movielist).difference(set(movielist1)))
    movielist=[*movielist1,*movie_rem]
    return movielist

def index(request):
    if 'user' in request.session and request.user.is_authenticated:
        movielist=Movie.objects.all()
        movielist=toprate(movielist)
        rater=Rater.objects.get(user=request.user)
        ratings=Rating.objects.filter(rater=rater)
        movie_wathed=rater.my_movies()
        for movie in movielist:
            if movie in movie_wathed:
                movie.Watched= True
                movie.save()
        if len(movielist)>11:
            paginator = Paginator(movielist, 12) # Show 4 movies per page
            page = request.GET.get('page')
            movies = paginator.get_page(page)
            return render(request,'main.html',{'movies':movies})
    return render(request,'login.html')

def rater(request):
    if 'user' in request.session and request.user.is_authenticated:
        rater=Rater.objects.get(user=request.user)
        ratings=Rating.objects.filter(rater=rater)
        movielist=rater.my_movies()
        for movie in movielist:
            movie.Watched= True
            movie.save()
        if len(movielist)>3:
            paginator = Paginator(movielist, 4) # Show 4 movies per page
            page = request.GET.get('page')
            movies = paginator.get_page(page)
            res={'rater':rater,'movies':movies}
        return render(request,'profile.html',res)
    return render(request,'login.html')

def remove_year_name(movies):
    try:
        if movies:
            for movie in movies:
                if movie.Name.count('('):
                    il=movie.Name.index('(')
                    ir=movie.Name.index(')')+1
                    movie.Name=movie.Name[:il]+movie.Name[ir:]
                    movie.save()
    except:
        pass
    return

def rec_movie(request):
    if 'user' in request.session and request.user.is_authenticated:
        rater=Rater.objects.get(user=request.user)
        print(request.user.id)
        ratings=Rating.objects.filter(rater=rater)
        from .Recommend import Recommend
        recommend = Recommend()
        idarg=[]
        idarg.append(request.user.id)
        returnlist = recommend.do_rec('D:/moviehub/ml-1m/ratings.csv',idarg, 1)
        print(returnlist)
        rec_movies=[get_object_or_404(Movie,id=id) for id in returnlist ]
        if len(rec_movies)>3:
            paginator = Paginator(rec_movies,4) # Show 4 movies per page
            page = request.GET.get('page')
            movies = paginator.get_page(page)
        # print(len(rec_movies))
        # print(returnlist)
        # rating_count,rating_avg=rater.avg_rating()
            res={'rater':rater,'movies':movies}
            return render(request,'recommend.html',res)
    return render(request,'login.html')


def logged_in(request):
    if 'user' in request.session and request.user.is_authenticated:
        movielist=Movie.objects.all()
        movielist=toprate(movielist)
        if len(movielist)>7:
            paginator = Paginator(movielist, 8) # Show 4 movies per page
            page = request.GET.get('page')
            movies = paginator.get_page(page)
            return render(request,'main.html',{'movies':movies})
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        if not User.objects.filter(username=username).exists():
            return render(request,'login.html',{'error_message':'Please Register First'})
        user=authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                request.session['user']=username
                movielist=Movie.objects.all()
                movielist=toprate(movielist)
                if len(movielist)>7:
                    paginator = Paginator(movielist, 8) # Show 4 movies per page
                    page = request.GET.get('page')
                    movies = paginator.get_page(page)
                    return render(request,'main.html',{'movies':movies})
            else:
                return render(request,'login.html',{'error_message':'Your Account Has Been Suspended'})
        return render(request,'login.html',{'error_message':'Wrong Credentials'})
    return render(request,'login.html')

def register(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        rep_password=request.POST['rep_password']
        e_mail=request.POST['email']
        if User.objects.filter(email=e_mail).exists():
            return render(request,'register.html',{'error_message':'E-mail already registered'})
        elif User.objects.filter(username=username).exists():
            return render(request,'register.html',{'error_message':'Username not available'})
        elif(password!=rep_password):
            return render(request,'register.html',{'error_message':'Passwords Dont match'})
        else:
            user=User(username=username,email=e_mail)
            user.set_password(password)
            user.save()
            user=authenticate(username=username,password=password)
            login(request,user)
            request.session['user']=username
            movielist=Movie.objects.all()
            movielist=toprate(movielist)
            if len(movielist)>7:
                paginator = Paginator(movielist, 8) # Show 4 movies per page
                page = request.GET.get('page')
                movies = paginator.get_page(page)

                return render(request,'main.html',{'movies':movies})
    return render(request,'register.html')


def log_out(request):
    if 'user' in request.session:
        del request.session['user']
        logout(request)
        return redirect('logged_in')

def detail(request,movie_id):
    if not request.user.is_authenticated:
        return redirect('logged_in')
    threadobj= threading.Thread(target=get_youtube_link,args=[])
    movie=get_object_or_404(Movie,id=movie_id)


    # from imdbpie import Imdb
    # imdb = Imdb()
    # data=imdb.search_for_title(movie.Name)
    # info=imdb.get_title(data[0]['imdb_id'])
    # info1=imdb.get_title_credits(data[0]['imdb_id'])
    path="D:/moviehub/moviehub/media/"

    if movie.Name.count('(')>1:
        il=movie.Name.index('(')
        ir=movie.Name.index(')')+1
        movie.Name=movie.Name[:il]+movie.Name[ir:]
    filename=movie.Name.replace(":", "_").replace(" ","_")+".jpg"
    if not movie.Poster or (not os.path.exists(path+filename)):
        from imdb import IMDb
        ia=IMDb()
        movielist = ia.search_movie(movie.Name)[0]
        m  = ia.get_movie(movielist.movieID)
        from imdbpie import Imdb
        from urllib.request import urlretrieve
        imdb = Imdb()
        data=imdb.search_for_title(movie.Name)
        try:
            info=imdb.get_title(data[0]['imdb_id'])
        except:
            pass
        try:
            imgurl=info['base']['image']['url']
            urlretrieve(imgurl,path+filename)
            movie.Poster.name = filename
        except:
            try:
                imgurl=m['cover url']
                urlretrieve(imgurl,path+filename)
                movie.Poster.name = filename
            except:
                pass

        movie.Year=m['year']
        try:
            movie.Plot_outline=' '.join(m['plot outline'].split()[:50])+'...'
        except:
            pass
        try:
            movie.Plot=m['plot'][0]
        except:
            pass
        try:
            movie.Imdb_rating=m['rating']
        except:
            pass
        try:
            movie.rating_Count=int(m['votes'])
        except:
            pass
        try:
            movie.Director=','.join([d['name'] for d in m['director']])
        except:
            pass
        try:
            movie.Actor=','.join([casting['name'] for casting in m['cast'][:4]])
        except:
            pass

    # movie.Year=info['base']['year']
    # movie.Plot_outline=info['plot']['outline']['text']
    # movie.Plot=info['plot']['summaries'][0]['text']
    # movie.Imdb_rating=info['ratings']['rating']
    # movie.rating_Count=info['ratings']['ratingCount']
    # movie.Director=info1['credits']['director'][0]['name']
    movie.save()

    if not movie.trailer:
        try:
            get_youtube_link(movie)
        except:
            pass
    rater=Rater.objects.get(user=request.user)
    if movie in rater.my_movies():
        rating=Rating.objects.get(rater=rater,movie=movie)
        your_rating=rating.rating
        comment=rating.review
    else:
        your_rating="You haven\'t rated the movie."
        comment="You haven\'t commented the movie."
    from .Recommend import Recommend
    recommend = Recommend()
    idarg=[]
    idarg.append(request.user.id)
    idarg.append(movie.id)
    returnlist = recommend.do_rec('D:/moviehub/ml-1m/ratings.csv',idarg, 2)
    print(returnlist)
    rec_movies=[get_object_or_404(Movie,id=id) for id in returnlist ]
    if len(rec_movies)>3:
        paginator = Paginator(rec_movies, 4) # Show 4 movies per page
        page = request.GET.get('page')
        movies = paginator.get_page(page)
    # movies1=movie_rec.delay(request.user.id,movie.id)
    # print(movies1)
    res={'movie':movie,'rating':your_rating,'rater':rater,'comment':comment,'movies':movies}
    return render(request,'details.html',res)

def get_movie_detail(movie):

    path="D:/moviehub/moviehub/media/"
    if movie.Name.count('(')>1:
        il=movie.Name.index('(')
        ir=movie.Name.index(')')+1
        movie.Name=movie.Name[:il]+movie.Name[ir:]
    filename=movie.Name.replace(":", "_").replace(" ","_")+".jpg"

    if not movie.Poster or (not os.path.exists(path+filename)):
        movie.Poster.name = filename
        from imdb import IMDb
        ia=IMDb()

        movielist = ia.search_movie(movie.Name)[0]
        m  = ia.get_movie(movielist.movieID)
        from imdbpie import Imdb
        from urllib.request import urlretrieve
        imdb = Imdb()
        data=imdb.search_for_title(movie.Name)
        info=imdb.get_title(data[0]['imdb_id'])
        try:
            imgurl=info['base']['image']['url']
            urlretrieve(imgurl,path+filename)
        except:
            try:
                imgurl=m['cover url']
                urlretrieve(imgurl,path+filename)
            except:
                pass

        movie.Year=m['year']
        try:
            movie.Plot_outline=' '.join(m['plot outline'].split()[:50])+'...'
        except:
            pass
        try:
            movie.Plot=m['plot'][0]
        except:
            pass
        try:
            movie.Imdb_rating=m['rating']
        except:
            pass
        try:
            movie.rating_Count=int(m['votes'])
        except:
            pass
        try:
            movie.Director=','.join([d['name'] for d in m['director']])
        except:
            pass
        try:
            movie.Actor=','.join([casting['name'] for casting in m['cast'][:4]])
        except:
            pass



    # movie.Year=info['base']['year']
    # movie.Plot_outline=info['plot']['outline']['text']
    # movie.Plot=info['plot']['summaries'][0]['text']
    # movie.Imdb_rating=info['ratings']['rating']
    # movie.rating_Count=info['ratings']['ratingCount']
    # movie.Director=info1['credits']['director'][0]['name']
    movie.save()

    # if not movie.trailer:
    #     try:
    #         get_youtube_link(movie)
    #     except:
    #         pass


def search_movie(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            if not request.POST['search']:
                return redirect('logged_in')
            rater=Rater.objects.get(user=request.user)
            ratings=Rating.objects.filter(rater=rater)
            movie_wathed=rater.my_movies()
            if '-w' in request.POST['search']:
                Q=re.findall('(.*)\s+-w',request.POST['search'])
                if not Q:
                    movielist=Movie.objects.all()
                    movielist=toprate(movielist)
                    for movie in movielist:
                        if movie in movie_wathed:
                            movie.Watched= True
                            movie.save()
                    paginator = Paginator(movielist, 8) # Show 4 movies per page
                    page = request.GET.get('page')
                    movies = paginator.get_page(page)
                    return render(request,'main.html',{"movies":movies})
                else:
                    Q=Q[0]
                    list1=Movie.objects.filter(Name__icontains=Q)
                    list2=Movie.objects.filter(Year__icontains=Q)
                    list3=Movie.objects.filter(Genre__icontains=Q)
                    list4=Movie.objects.filter(Director__icontains=Q)
            else:
                Q=request.POST['search']
                list1=Movie.objects.filter(Name__icontains=Q)
                list2=Movie.objects.filter(Year__icontains=Q)
                list3=Movie.objects.filter(Genre__icontains=Q)
                list4=Movie.objects.filter(Director__icontains=Q)
            movielist=list(set(list1)^set(list2)^set(list3)^set(list4))
            for movie in movielist:
                if movie in movie_wathed:
                    movie.Watched= True
                    movie.save()
            if(movielist):
                paginator = Paginator(movielist, 8) # Show 4 movies per page
                page = request.GET.get('page')
                movies = paginator.get_page(page)
                return render(request,'main.html',{"movies":movies})
            movies=[]
            return render(request,'main.html',{"movies":movies})
    return redirect('logged_in')



def Watched(request,movie_id):
    if request.user.is_authenticated:
        movie=get_object_or_404(Movie,id=movie_id)
        if movie.Watched:
            movie.Watched=False
        else:
            movie.Watched=True
        movie.save()
    return redirect('logged_in')

def Watched_stay(request,movie_id):
    if request.user.is_authenticated:
        movie=get_object_or_404(Movie,id=movie_id)
        if movie.Watched:
            movie.Watched=False
        else:
            movie.Watched=True
        movie.save()
        return render(request,'details.html',{'movie':movie})


    return redirect('logged_in')
