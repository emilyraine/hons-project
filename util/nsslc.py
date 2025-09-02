import math 
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist 
import numpy as np
from deap import creator, tools
import heapq
import sys

archive = [] 
history = []
novelty_initialised = False
novelty_threshold = None
novelty_floor = None
time_out = 0
add_queue = []
prev_centroids = None

def nsslc_select(population, pop_size, lmbda, nLC, nNS, nSS, h, timeout_limit, kSS): 

    # evaluate offspring
    search_pool = population + archive
    search_descriptors = [individual.features for individual in search_pool]
    search_fitnesses = [individual.fitness.values[0] for individual in search_pool]
  
    indiv_to_index = {id(ind): i for i, ind in enumerate(search_pool)}

    local_competition_scores = []
    novelty_scores = []

    for ind in population:
        current_descriptor = ind.features
        true_index = indiv_to_index[id(ind)]
        indexed_distances = [(j, math.dist(current_descriptor, desc_j)) for j, desc_j in enumerate(search_descriptors) if j != true_index]

        # Calculate Novelty Score
        k_ns = min(nNS, len(indexed_distances))
        distances_sorted = heapq.nsmallest(k_ns, (dist for j, dist in indexed_distances))
        novelty = np.mean(distances_sorted)
        novelty_scores.append(novelty)

        # Individual added to novelty archive if its novelty score is above the novelty threshold
        if novelty_initialised:
            if novelty > novelty_threshold:
                archive.append(ind)
                add_queue.append(ind)

        # Calculate Local Competition 
        lc_score = 0
        k_lc = min(nLC, len(indexed_distances))
        indexed = heapq.nsmallest(k_lc, indexed_distances, key = lambda pair: pair[1] )
        lc_score = sum(1 for j,dist in indexed if ind.fitness.values[0] > search_fitnesses[j])/float(k_lc)

        local_competition_scores.append(lc_score)
    
    # Generation 1: initialise Novelty Threshold and Novelty Floor
    if not novelty_initialised:
        initialise_novelty(novelty_scores, population)

    # Calculate Surprise Scores and update the surprise model
    surprise_scores = update_surprise_model(population, h, kSS, nSS)

    # Calculate Novelty-Surprise Scores
    novelty_surprise_scores = [(lmbda*n + (1 - lmbda)*s) for n, s in zip(novelty_scores, surprise_scores)]

    # Select using NSGAII
    selected = select_nsga2(novelty_surprise_scores, local_competition_scores, pop_size, population)
    
    # adjust novelty threshold
    adjust_novelty_threshold(timeout_limit)

    return selected


def initialise_novelty(novelty_scores, population):
    global novelty_threshold, novelty_floor, novelty_initialised, archive, add_queue
    sorted_indices = np.argsort(novelty_scores)[::-1]
    sorted_novelty = [novelty_scores[i] for i in sorted_indices]
    top_ten = sorted_novelty[9]
    top_ten_indices = sorted_indices[:10]
    for i in top_ten_indices:
        archive.append(population[i])
        add_queue.append(population[i])
    novelty_threshold = math.nextafter(top_ten, float("-inf")) 
    top_20 = sorted_novelty[19]
    novelty_floor = math.nextafter(top_20, float("-inf"))
    novelty_initialised = True


def select_nsga2(ns_scores, lc_scores, pop_size, population):
    clones = []
    for index, (ns, lc) in enumerate(zip(ns_scores, lc_scores)):
        clone = creator.Individual([])
        clone.fitness.weights = (1.0, 1.0)
        clone.fitness.values = (ns, lc)        
        clone.pop_index = index
        clones.append(clone)

    selected_clones = tools.selNSGA2(clones, k = pop_size) 
    selected = [population[clone.pop_index] for clone in selected_clones]
    return selected


def update_surprise_model(population, h, kSS, nSS):
    global history, prev_centroids
    descriptors = np.vstack([individual.features for individual in population])
    history.append(descriptors)
    if (len(history) > h):
        history.pop(0) # remove the descriptors of the oldest generation

    history_combined = np.vstack(history)

    # seed from last generation if available, else random
    if prev_centroids is None:
        km = KMeans(n_clusters = kSS, init = "random", n_init = 1)
    else:
        km = KMeans(n_clusters = kSS, init = prev_centroids, n_init = 1)
    
    km.fit(history_combined)
    centroids = km.cluster_centers_

    if len(history) <= 1 or prev_centroids is None:
        predictions = centroids
    else:
        predictions = centroids + (centroids - prev_centroids)

    # store for next generation
    prev_centroids = centroids
  
    distances = cdist(descriptors, predictions)
    surprise_scores = []
    for i in range(len(population)):
        m = min(nSS, len(distances[i]))
        distances_to_predictions = np.partition(distances[i], m-1)[:m]
        score = distances_to_predictions.mean()
        surprise_scores.append(score)
    
    return surprise_scores


def adjust_novelty_threshold(timeout_limit):
    global novelty_threshold, novelty_floor, time_out, add_queue
    added = len(add_queue)
    if added == 0:
        time_out += 1
    else:
        time_out = 0

    # Lower threshold if archive growth stagnates
    if time_out >= timeout_limit:
        novelty_threshold = max(novelty_threshold * 0.95, novelty_floor)
        time_out = 0

    # Raise threshold if too many additions
    if added > 4:
        novelty_threshold *= 1.2

    add_queue.clear()