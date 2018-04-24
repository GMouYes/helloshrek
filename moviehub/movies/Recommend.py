#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 18:24:12 2018
Last modified on Thu Apr 19 20:30 2018

@author: GMou
"""

# =============================================================================
# This python file will read the csv document and generate recommendations
# =============================================================================

import numpy as NP
import pandas as PD
#import time

class Recommend(object):
# =============================================================================
#     defining variables and structures
#     userlist and movielist will take care of mapping of id to index
#     top_num_return controls number of returning items
#     top_similar defines the most # of domain for calculation
#     eliminate threshold will delete vectors with too little infos
# =============================================================================
    def __init__(self):
        self._userlist = []
        self._movielist = []
        self._top_num_return = 10
        self._top_similar = 100
        self._eliminate_threshold = 7

# =============================================================================
#     reads the file to the dataset and form it into a matrix
#     fill in mapping relations into two lists
#     return the matrix
# =============================================================================
    def readfiles(self, path):
        dataset = PD.read_csv(path)
        self._userlist=sorted(dataset.userId.unique().tolist())
        self._movielist=sorted(dataset.movieId.unique().tolist())
        new_dataset = dataset.pivot('userId', 'movieId',\
                                    'rating').fillna(0).astype(float).values
        return new_dataset

# =============================================================================
#     main function for doing recommendations
#     returns the results to main in a list
#     id is a list, in the shape of [userid, movieid]
#     if choice==1, then recommend top # unseen best rating movie
#     if choice==2, then recommend top # unseen most similar movie
# =============================================================================
    def do_rec(self, path, id, choice):
        if id[0] < 0:
            return 'ERROR! Invalid input! IDs should be non negative!\n'

        user_rating = self.readfiles(path)
        if id[0] not in self._userlist:
                return 'ERROR! Cannot find such a user\n'

        nonzero = NP.count_nonzero(user_rating, axis = 0) > self._eliminate_threshold
        new_rating = user_rating[:, nonzero]
        self._movielist = sorted(list(NP.array(self._movielist)[nonzero]))
        movie_num = len(self._movielist)
#        user_num = len(self._userlist)
        temp = new_rating.copy()

        # nonzero values subtract their average
        pre_sim = NP.transpose(new_rating)
        temp_mean = NP.sum(new_rating, axis = 0)/NP.count_nonzero(new_rating, axis = 0)
        for i in range(movie_num):
            # minus the mean of rating to the nonzero rating each item
            pre_sim[i][pre_sim[i]!=0] -= temp_mean[i]

        from sklearn.metrics.pairwise import cosine_similarity
        from scipy import sparse
        sim = cosine_similarity(sparse.csr_matrix(pre_sim))

        # force change a film's own similarity to 0, forbid its misuse
        NP.fill_diagonal(sim,0)


# =============================================================================
#        Recommend top unseen films for the user
#        when choice is 1, only userid is used
# =============================================================================
        if choice == 1:
            # extract most similar ones to extrapolate missing ratings
            # first get the most similar ones' index
            ind = NP.argpartition(sim, (-self._top_similar))[:,\
                                 (-self._top_similar):]

            signal = self._userlist.index(id[0])
            for i in range(movie_num):
#                print(i)
#                print(self._movielist[i])
                if temp[signal][i] == 0:
                    temp[signal][i] = NP.average(new_rating[signal,ind[i]],\
                        weights = sim[i,ind[i]])

            final_list = []
            ind_temp = NP.argsort(temp[signal])
            j = movie_num - 1
            count_temp = 0

            while j >= 0 and count_temp < self._top_num_return:
                if new_rating[signal][ind_temp[j]] == 0:
                    final_list.append(self._movielist[ind_temp[j]])
                    count_temp += 1
                j -= 1

            return final_list

# =============================================================================
#         Recommend top # similar unseen films for a movie
#         when choice is 2, both id is used
# =============================================================================
        if choice == 2:
            if int(id[1]) < 0:
                return 'ERROR! Invalid input! IDs should be non negative!\n'
            if id[1] not in self._movielist:
                    return 'ERROR! Cannot find this movie or not able to analyze\n'
            signal0 = self._userlist.index(id[0])
            signal1 = self._movielist.index(id[1])
            ind = NP.argsort(sim[signal1])

            final_list = []
            j = movie_num - 1
            count_temp = 0

            while j >= 0 and count_temp < self._top_num_return:
                if new_rating[signal0][ind[j]] == 0:
                    final_list.append(self._movielist[ind[j]])
                    count_temp += 1
                j -= 1
            return final_list
