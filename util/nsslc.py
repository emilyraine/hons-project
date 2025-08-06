import math 
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist 
import numpy as np
from deap import tools
import types


archive = [] 
history = []
novelty_threshold = 0.1 # try with 6.0
novelty_floor = 0.07 # try with 0.25
time_out = 0
add_queue = []
prev_centroids = None

def nsslc_select(population, pop_size, generation, kSS, lmbda, nLC, nNS, nSS, h, timeout_limit): 

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
        distances_sorted = sorted(dist for j, dist in indexed_distances)

        # Calculate Novelty Score (eq 1) - compute novelty for each descriptor in current population
        k_ns = min(nNS, len(distances_sorted))
        novelty = sum(distances_sorted[:k_ns])/float(k_ns)
        novelty_scores.append(novelty)

        # Add members to Novelty Archive A
        # if individual has a novelty score above a fluctuating threshold then is added to novelty archive
        if novelty > novelty_threshold:
            archive.append(ind)
            add_queue.append(ind)

        # Calculate Local Competition 
        indexed = sorted(indexed_distances, key = lambda pair: pair[1]) 
        lc_score = 0
        k_lc = min(nLC, len(indexed))
        for b in range(k_lc):
            if(ind.fitness.values[0] > search_fitnesses[indexed[b][0]]):
                lc_score += 1

        local_competition_scores.append(lc_score)

    # Calculate Surprise Score (eq 3)
    # Update surprise model
    surprise_scores = update_surprise_model(population, h, kSS, nSS)

    # Calculate Novelty-Surprise Score (eq 4)
    novelty_surprise_scores = [(lmbda*n + (1 - lmbda)*s) for n, s in zip(novelty_scores, surprise_scores)]

    # Select using NSGAII
    selected = select_nsga2(novelty_surprise_scores, local_competition_scores, pop_size, population)
    
    # archive threshold is fluctuating
    adjust_novelty_threshold(generation, timeout_limit)

    return selected




def select_nsga2(ns_scores, lc_scores, pop_size, population):
    clones = []
    for index, (ns, lc) in enumerate(zip(ns_scores, lc_scores)):
        clone = types.SimpleNamespace()
        clone.fitness = types.SimpleNamespace()
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
    n_samples = history_combined.shape[0]

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
  
    distances = cdist(descriptors, predictions )
    surprise_scores = []
    for i in range(len(population)):
        distances_to_predictions = np.sort(distances[i])
        m = min(nSS, len(distances_to_predictions))
        score = sum(distances_to_predictions[:m])/float(m)
        surprise_scores.append(score)
    
    return surprise_scores


def adjust_novelty_threshold(gen, timeout_limit):
    global novelty_threshold, novelty_floor, time_out, add_queue
    added = len(add_queue)
    if added == 0:
        time_out += 1
    else:
        time_out = 0

    # Lower threshold if archive stagnant
    if time_out >= timeout_limit:
        novelty_threshold = max(novelty_threshold * 0.95, novelty_floor)
        time_out = 0

    # Raise threshold if too many additions
    if added > 4: #make this in proportion to the size of pop
        novelty_threshold *= 1.2

    add_queue.clear()