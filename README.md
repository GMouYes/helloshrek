# MovieHub

### Website Demo
[Click HERE & Check Out Our DEMO](http://127.0.0.1:8080)

### What is MovieHub?
MovieHub is a mobile-ready, offline-storage, JS powered HTML5 edited movie rating, data analysis and recommendation system :+1:

### What does MovieHub do?
* Support wildcard search and display over 3,700 movies' details, including:
  - Movie Name, Genre, Publish Year
  - Poster, Video Preview
  - Director(s), Actor(s)
  - Average Rating, etc.
* Support recommendations of:
  - TOP 10 best unseen movies for every different user and:
  - TOP 10 similar unseen similar movies for every specified movie that the user is checking on
* Support tracing each user's watching and rating history
  
### Where does our dataset come from?
We fetched the “MovieLens 1M Dataset” which was released in February 2003 from 
[This Website](https://grouplens.org/datasets/movielens/)
* It generally contains 1 million ratings from 6,000 users on 4,000 movies, in the format of CSV.
* For the data of user rating, this dataset includes mainly: User, Rating and Movie.
* For the data of user info, this data set includes mainly :User, Gender, Age, Zip-code.
<br/>

We have also crawled
[IMDB](https://www.imdb.com)
to get  detail info about movies in the dataset mentioned above for better user experience<br/>
A preview of what's the data looks like is shown below<br/>

<p align="center">
  <img src="dataset0.jpg" height="200"width="400"/><br/>
  <h6 align="center">User Dataset</h6><br/>
</p><br/>

<p align="center">
  <img src="dataset1.png" height="200"width="400"/><br/>
  <h6 align="center">Movie Dataset</h6><br/>
</p><br/>

<p align="center">
  <img src="dataset2.png" height="200"width="400"/><br/>
  <h6 align="center">Rating Dataset</h6><br/>
</p><br/>


![dataset example2](dataset2.png)
![dataset example0](dataset0.jpg)
![dataset example1](dataset1.png)

### Algorithms
We have implemented three recommend algorithms in this project:
  - User based collaborate filtering
  - Item based collaborate filtering
  - SVD (Singular Value Decomposition)
<br/>
Concepts are shown below as graphs:<br\>

![cf0](cf0.png)
![cf1](cf1.png)
![cf2](cf2.png)

### Evaluation
We used Root Mean Squared Error (RMSE) for evaluation:

![RMSE](RMSE.png)

And the evaluation result is:

![ev0](evaluation0.png)
![ev1](evaluation1.png)

### DEMO Implement
We used Python Django as backend to implement our project.
1. Environment Setup: -- Windows 10, Python 3.6.4, mysql 5.7.21,mysql bench 6.3 CE
2. Python Requirement Packages: -- Numpy ,pandas, imdbpie ,Imdbpy, sklearn
3. App start up by: -- Python manage.py runserver 8080, Open in the browser 127.0.0.1:8080

### Website Preview

![pre0](demo0.png)
![pre1](demo1.png)
![pre2](demo2.png)
![pre3](demo3.png)
![pre4](demo4.png)
![pre5](demo5.png)
![pre6](demo6.png)
