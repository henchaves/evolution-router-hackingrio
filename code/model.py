import json
import requests
from geopy.geocoders import Nominatim
import numpy as np
import matplotlib.pyplot as plt
from copy import copy
import folium
from folium.plugins import BeautifyIcon

#OK
def pipeline_model(addresses, shops_names, n_shops, metric):
    '''
    addresses -> todos os endereços (origem, lojas, entregas)
    shops_names -> nome das lojas (lojas, entregas)
    n_shops -> quantidade de lojas
    metric -> métrica para calcular o resultado (distancia ou tempo)
    
    '''
    geolocator = Nominatim(user_agent="rickchavesmm")

    coordinates = {i:[geolocator.geocode(k).latitude, geolocator.geocode(k).longitude] for i,k in enumerate(addresses)}

    coordinates_keys = list(coordinates.keys())

    shop_dict = create_shop_dict(shops_names, n_shops)
    
    metric_results = save_distances(addresses, coordinates, metric)
    
    current_generation = create_generation(coordinates_keys, shop_dict, population=500)
    
    _ , best_guess = evolve_to_solve(current_generation, metric_results, 100, 150, 70, 0.01, 3, 5, verbose=False)
    
    m = plot_map(geolocator, best_guess[:-1], coordinates, addresses, shops_names, n_shops)
    m.save('map.html')
    return m

#OK
def create_shop_dict(shops_names, n_shops):
    list_shops = shops_names[:n_shops]
    list_deliveries = shops_names[n_shops:]
    shop_dict = {}

    for i,v in enumerate(list_shops):
        shop_dict[i+1] = []
        for j,w in enumerate(list_deliveries):
            if v == w:
                shop_dict[i+1].append(j+n_shops+1)
    return shop_dict

#OK
def get_distance(address_1, address_2, coordinates, metric, API_KEY='Wo4TQp6dReCezt0qVyIlSgAWTfex3lzUtcRcw0DN-uM', mode='fastest', vehicle='car', traffic='enabled'):
    """
    Given two address, this calculates the selected metric between then
    """
    c1 = coordinates[address_1]
    c2 = coordinates[address_2]
    request_template = f'https://route.ls.hereapi.com/routing/7.2/calculateroute.json?apiKey={API_KEY}&waypoint0=geo!{c1[0]},{c1[1]}&waypoint1=geo!{c2[0]},{c2[1]}&mode={mode};{vehicle};traffic:{traffic}'
    
    r = requests.get(request_template)
    request_json = json.loads(r.text)
    
    if metric == 'distance':
        result = request_json['response']['route'][0]['summary']['distance']/1000
    elif metric == 'time':
        result = request_json['response']['route'][0]['summary']['travelTime']/60
    return result

#OK
def save_distances(addresses, coordinates, metric):
    metric_results = {}
    l = len(addresses)
    for i in range(l):
        for j in range(l):
            if i != j:
                metric_results[(i, j)] = get_distance(i, j, coordinates, metric)
    return metric_results

#OK
def distance_between_address(address_1, address_2, metric_results, API_KEY='Wo4TQp6dReCezt0qVyIlSgAWTfex3lzUtcRcw0DN-uM', mode='fastest', vehicle='car', traffic='disabled'):
    """
    Given two address, this calculates this distance between them
    """
    
    return metric_results[(address_1, address_2)]

#OK
def create_guess(coordinates_keys, shop_dict):
    """
    Creates a possible route between all adresses, returning to the original.
    Input: List of Adr
    """
    guess = copy(coordinates_keys)
    np.random.shuffle(guess)

    while True:
        if guess[0] != 0 or check_key_and_values(guess[1:], shop_dict) == False:
            np.random.shuffle(guess)
        else:
            break
    guess.append(guess[0])
    return list(guess)

#OK
def check_key_and_values(lista, dicionario):
    """
        Dada uma lista, e um dicionario, retorne True se as keys do dicionario vem antes de algum elemento
        
    """
    for id_key, id_values in dicionario.items():
        index_key = lista.index(id_key)
        for id_value in id_values:
            index_value = lista.index(id_value)
            if index_key > index_value:
                return False
    return True

#OK
def create_generation(coordinates_keys, shop_dict, population=100):
    """
    Makes a list of guessed adress orders given a list of address IDs.
    Input:
    adresses: list of address ids
    population: how many guesses to make
    """
    generation = [create_guess(coordinates_keys, shop_dict) for _ in range(population)]
    return generation

#OK
def fitness_score(guess, metric_results):
    """
    Loops through the adresses in the guesses order and calculates
    how much distance the path would take to complete a loop.
    Lower is better.
    """
    score = 0
    for ix, address_id in enumerate(guess[:-2]):
    #Editado aqui
    #for ix, address_id in enumerate(guess[:-1]):
        score += distance_between_address(address_id, guess[ix+1], metric_results)
    return score

#OK
def check_fitness(guesses, metric_results):
    """
    Goes through every guess and calculates the fitness score. 
    Returns a list of tuples: (guess, fitness_score)
    """
    fitness_indicator = []
    for guess in guesses:
        fitness_indicator.append((guess, fitness_score(guess, metric_results)))
    
    return fitness_indicator

#OK
def get_breeders_from_generation(guesses, metric_results, take_best_N=10, take_random_N=5, verbose=False, mutation_rate=0.1):
    """
    This sets up the breeding group for the next generation. You have
    to be very careful how many breeders you take, otherwise your
    population can explode. These two, plus the "number of children per couple"
    in the make_children function must be tuned to avoid exponential growth or decline!
    """
    # First, get the top guesses from last time
    fit_scores = check_fitness(guesses, metric_results)
    sorted_guesses = sorted(fit_scores, key=lambda x: x[1]) # sorts so lowest is first, which we want
    new_generation = [x[0] for x in sorted_guesses[:take_best_N]]
    best_guess = new_generation[0]
    
    if verbose:
        # If we want to see what the best current guess is!
        print(best_guess)
    
    # Second, get some random ones for genetic diversity
    for _ in range(take_random_N):
        #ix = np.random.randint(len(guesses))
        ix = np.random.randint(len(guesses)-1)
        new_generation.append(guesses[ix])
        
    # No mutations here since the order really matters.
    # If we wanted to, we could add a "swapping" mutation,
    # but in practice it doesn't seem to be necessary
    
    np.random.shuffle(new_generation)
    return new_generation, best_guess

def make_child(parent1, parent2):
    """ 
    Take some values from parent 1 and hold them in place, then merge in values
    from parent2, filling in from left to right with addresses that aren't already in 
    the child. 
    """
    list_of_ids_for_parent1 = list(np.random.choice(parent1, replace=False, size=len(parent1)//2))
    child = [-99 for _ in parent1]
    
    for ix in list_of_ids_for_parent1:
        child[ix] = parent1[ix]
    for ix, gene in enumerate(child):
        if gene == -99:
            for gene2 in parent2:
                if gene2 not in child:
                    child[ix] = gene2
                    break
    
    child[-1] = child[0]
    return child

def make_children(old_generation, children_per_couple=1):
    """
    Pairs parents together, and makes children for each pair. 
    If there are an odd number of parent possibilities, one 
    will be left out. 
    
    Pairing happens by pairing the first and last entries. 
    Then the second and second from last, and so on.
    """
    mid_point = len(old_generation)//2
    next_generation = [] 
    
    for ix, parent in enumerate(old_generation[:mid_point]):
        for _ in range(children_per_couple):
            next_generation.append(make_child(parent, old_generation[-ix-1]))
    return next_generation

def evolve_to_solve(current_generation, metric_results, max_generations, take_best_N, take_random_N,
                    mutation_rate, children_per_couple, print_every_n_generations, verbose=False):
    """
    Takes in a generation of guesses then evolves them over time using our breeding rules.
    Continue this for "max_generations" times.
    Inputs:
    current_generation: The first generation of guesses
    max_generations: how many generations to complete
    take_best_N: how many of the top performers get selected to breed
    take_random_N: how many random guesses get brought in to keep genetic diversity
    mutation_rate: How often to mutate (currently unused)
    children_per_couple: how many children per breeding pair
    print_every_n_geneartions: how often to print in verbose mode
    verbose: Show printouts of progress
    Returns:
    fitness_tracking: a list of the fitness score at each generations
    best_guess: the best_guess at the end of evolution
    """
    fitness_tracking = []
    for i in range(max_generations):
        if verbose and not i % print_every_n_generations and i > 0:
            print("Generation %i: "%i, end='')
            print(len(current_generation))
            print("Current Best Score: ", fitness_tracking[-1])
            is_verbose = True
        else:
            is_verbose = False
        breeders, best_guess = get_breeders_from_generation(current_generation, metric_results, 
                                                            take_best_N=take_best_N, take_random_N=take_random_N, 
                                                            verbose=is_verbose, mutation_rate=mutation_rate)
        fitness_tracking.append(fitness_score(best_guess, metric_results))
        current_generation = make_children(breeders, children_per_couple=children_per_couple)
    return fitness_tracking, best_guess

#OK
def plot_map(geolocator, best_guess, coordinates, addresses, shops_names, n_shops):
    #location = geolocator.geocode("Rio de Janeiro, RJ, Brazil")
    m = folium.Map(location = [-22.9385, -43.4060], zoom_start = 11)
    
    for ix,i in enumerate(best_guess):
        popup = 'None'
        color = '#000000'
    
        if ix == 0:
            popup = folium.Popup('Origem')
            color ='#000000'
        elif i > 0 and i <= n_shops:
            popup = folium.Popup('{}a Parada<br>Abastecimento na Loja {}'.format(ix, shops_names[i-1]), max_width=200)
            color = '#2ca02c'
        else:
            popup = folium.Popup('{}a Parada<br>Entrega da Loja {}'.format(ix, shops_names[i-1]), max_width=200)
            color = '#BA3CC2'
    
        icon_number = BeautifyIcon(
        border_color=color,
        text_color='#000000',
        number=ix,
        icon_size=[30,30],
        inner_icon_style='margin_top:10;')

        folium.Marker(
        location=[coordinates[i][0], coordinates[i][1]],
        popup=popup,
        tooltip=addresses[i],
        icon=icon_number).add_to(m)
        
    return m