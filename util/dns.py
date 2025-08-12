import math
import heapq

# Dominated Novelty Search

# Compute the dominated novelty score (average distance to the k-nearest-fitter solutions) for each individual 
# Select and return the top pop_size individuals ranked by highest dominated novelty score

def dns_select(population, pop_size, k):
    # Fitness values and descriptor lists
    descriptors = [individual.features for individual in population]
    fitnesses = [individual.fitness.values[0] for individual in population]

    num_individuals = len(population) 
    dns_scores = [0.0] * num_individuals
    
    # Compute DNS scores for every individual
    for ind in range(num_individuals):
        ind_fitness = fitnesses[ind]
        fitter_individuals = [x for x in range(num_individuals) if fitnesses[x] > ind_fitness]
        if len(fitter_individuals) == 0:
            dns_scores[ind] = math.inf
        else:
            distances = [math.dist(descriptors[ind], descriptors[j]) for j in fitter_individuals]
            m = min(k, len(distances)) 
            if m == 0:
                dns_scores[ind] = math.inf
            else:
                nearest = heapq.nsmallest(m, distances)
                dns_scores[ind] = sum(nearest)/len(nearest)

    indexed_scores = []
    for i in range(num_individuals):
        indexed_scores.append((i, dns_scores[i]))
    sorted_indexed_scores = sorted(indexed_scores, key = lambda pair: pair[1], reverse = True) 
    ranked = []
    for index, score in sorted_indexed_scores:
        ranked.append(index)
    selected_indices = ranked[:pop_size] 
    selected = [population[i] for i in selected_indices]
    return selected