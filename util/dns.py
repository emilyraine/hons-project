import math
# Dominated Novelty Search

# Compute the dominated novelty score (average distance to the k-nearest-fitter solutions) for each individual 
# Select and return the top pop_size individuals ranked by highest dominated novelty score

def dns_select(population, pop_size, k):
    # All fitness values and descriptor lists
    fitnesses = []
    descriptors = []
    for individual in population:
        fitness_value = individual.fitness.values[0]
        fitnesses.append(fitness_value)
        descriptor_list = individual.features
        descriptors.append(descriptor_list)
    
    num_individuals = len(population) 
    dns_scores = [0.0] * num_individuals
    
    # Compute DNS scores for every individual
    for ind in range(num_individuals):
        ind_fitness = fitnesses[ind]
        fitter_individuals = []
        for x in range(num_individuals):
            if fitnesses[x] > ind_fitness:
                fitter_individuals.append(x)
        if len(fitter_individuals) == 0:
            dns_scores[ind] = math.inf
        else:
            distances = []
            for j in fitter_individuals:
                dist = math.dist(descriptors[ind], descriptors[j])
                distances.append(dist)

            distances.sort() 
            m = min(k, len(distances)) 
            dns_scores[ind] = sum(distances[:m])/float(m)

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