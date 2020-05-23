import json
import requests
from geopy.geocoders import Nominatim
import numpy as np
import matplotlib.pyplot as plt
from copy import copy
import folium
from folium.plugins import BeautifyIcon

def pipeline_model(addresses, metric):
    geolocator = Nominatim(user_agent="rickchaves")
    address_names = addresses 

    address_coordinates = {i:[geolocator.geocode(k).latitude, geolocator.geocode(k).longitude] for i,k in enumerate(address_names)}
    address_distances_dict = save_distances(address_names, address_coordinates, metric)
    current_generation = create_generation(list(address_coordinates.keys()), address_distances_dict, population=500)
    _ , best_guess = evolve_to_solve(current_generation, 100, 150, 70, 0.5, 3, 5, address_distances_dict, verbose=True)
    map = plot_map(geolocator, best_guess, address_coordinates, address_names)
    #map.save('map.html')
    return map
    

def get_distance(address_1, address_2, address_coordinates, metric, API_KEY='Wo4TQp6dReCezt0qVyIlSgAWTfex3lzUtcRcw0DN-uM', mode='fastest', vehicle='car', traffic='disabled'):
    """
    Given two address, this calculates this distance between them
    """
    c1 = address_coordinates[address_1]
    c2 = address_coordinates[address_2]
    request_template = f'https://route.ls.hereapi.com/routing/7.2/calculateroute.json?apiKey={API_KEY}&waypoint0=geo!{c1[0]},{c1[1]}&waypoint1=geo!{c2[0]},{c2[1]}&mode={mode};{vehicle};traffic:{traffic}'
    
    r = requests.get(request_template)
    request_json = json.loads(r.text)
    
    if metric == 'distance':
        distance = request_json['response']['route'][0]['summary']['distance']/1000
    elif metric == 'time':
        distance = request_json['response']['route'][0]['summary']['travelTime']/60
    return distance

def save_distances(addresses, coordinates, metric):
    distances_dict = {}
    l = len(addresses)
    for i in range(l):
        for j in range(l):
            if i != j:
                distances_dict[(i, j)] = get_distance(i, j, coordinates, metric)
    return distances_dict

def create_guess(addresses):
    """
    Creates a possible route between all adresses, returning to the original.
    Input: List of Adr
    """
    guess = copy(addresses)
    np.random.shuffle(guess)
    while guess[0] != 0:
        np.random.shuffle(guess)
    guess.append(guess[0])
    return list(guess)

def plot_address(address_coordinates, annotate=True):
    """
    Makes a plot of all addresses.
    Input: address_coordinates; dictionary of all addresses and their coordinates in (x,y) format
    """
    names = []
    x = []
    y = []
    plt.figure(dpi=250)
    for ix, coord in address_coordinates.items():
        names.append(ix)
        x.append(coord[0])
        y.append(coord[1])
        if annotate:
            plt.annotate(ix, xy=(coord[0], coord[1]), xytext=(20, -20),
                        textcoords='offset points', ha='right', va='bottom',
                        bbox=dict(boxstyle='round,pad=0.5', fc='w', alpha=0.5),
                        arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))
    plt.scatter(x,y,c='r',marker='o')

def plot_guess(address_coordinates, guess, guess_in_title=True):
    """
    Takes the coordinates of the cities and the guessed path and
    makes a plot connecting the cities in the guessed order
    Input:
    city_coordinate: dictionary of city id, (x,y)
    guess: list of ids in order
    """
    plot_address(address_coordinates)
    for ix, _ in enumerate(guess[:-1]):
        x = [address_coordinates[guess[ix]][0],address_coordinates[guess[ix+1]][0]]
        y = [address_coordinates[guess[ix]][1],address_coordinates[guess[ix+1]][1]]
        if ix == 0:
            plt.plot(x,y,'g--',lw=1)
        elif ix == len(guess)-2:
            plt.plot(x,y,'r--',lw=1)
        else:
            plt.plot(x,y,'c--',lw=1)
    plt.scatter(address_coordinates[guess[0]][0],address_coordinates[guess[0]][1], marker='x', c='b')
    if guess_in_title:
        plt.title("Current Guess: [%s]"%(','.join([str(x) for x in guess])))
    else:
        print("Current Guess: [%s]"%(','.join([str(x) for x in guess])))

def create_generation(addresses, address_distances_dict, population=100):
    """
    Makes a list of guessed adress orders given a list of address IDs.
    Input:
    adresses: list of address ids
    population: how many guesses to make
    """
    generation = [create_guess(addresses) for _ in range(population)]
    return generation

def distance_between_address(address_1, address_2, address_distances_dict, API_KEY='Wo4TQp6dReCezt0qVyIlSgAWTfex3lzUtcRcw0DN-uM', mode='fastest', vehicle='car', traffic='disabled'):

    """
    Given two address, this calculates this distance between them
    """
    
    return address_distances_dict[(address_1, address_2)]

def fitness_score(guess, address_distances_dict):
    """
    Loops through the adresses in the guesses order and calculates
    how much distance the path would take to complete a loop.
    Lower is better.
    """
    score = 0
    for ix, address_id in enumerate(guess[:-1]):
        score += distance_between_address(address_id, guess[ix+1], address_distances_dict)
    return score

def check_fitness(guesses, address_distances_dict):
    """
    Goes through every guess and calculates the fitness score. 
    Returns a list of tuples: (guess, fitness_score)
    """
    fitness_indicator = []
    for guess in guesses:
        fitness_indicator.append((guess, fitness_score(guess, address_distances_dict)))
    
    return fitness_indicator

def get_breeders_from_generation(guesses, address_distances_dict, take_best_N=10, take_random_N=5, verbose=False, mutation_rate=0.1):

    """
    This sets up the breeding group for the next generation. You have
    to be very careful how many breeders you take, otherwise your
    population can explode. These two, plus the "number of children per couple"
    in the make_children function must be tuned to avoid exponential growth or decline!
    """
    # First, get the top guesses from last time
    fit_scores = check_fitness(guesses, address_distances_dict)
    sorted_guesses = sorted(fit_scores, key=lambda x: x[1]) # sorts so lowest is first, which we want
    new_generation = [x[0] for x in sorted_guesses[:take_best_N]]
    best_guess = new_generation[0]
    
    if verbose:
        # If we want to see what the best current guess is!
        print(best_guess)
    
    # Second, get some random ones for genetic diversity
    for _ in range(take_random_N):
        ix = np.random.randint(len(guesses))
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

def evolve_to_solve(current_generation, max_generations, take_best_N, take_random_N,
                    mutation_rate, children_per_couple, print_every_n_generations, address_distances_dict, verbose=False):
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
        breeders, best_guess = get_breeders_from_generation(current_generation, address_distances_dict, 
                                                            take_best_N=take_best_N, take_random_N=take_random_N, 
                                                            verbose=is_verbose, mutation_rate=mutation_rate)
        fitness_tracking.append(fitness_score(best_guess, address_distances_dict))
        current_generation = make_children(breeders, children_per_couple=children_per_couple)
    return fitness_tracking, best_guess

def plot_map(geolocator, best_guess, address_coordinates, address_names):
    location = geolocator.geocode("Rio de Janeiro, RJ, Brazil")
    m = folium.Map(location = [location.latitude, location.longitude], zoom_start = 11)


    for ix,i in enumerate(best_guess[:-1]):
        colors = dict()

        if ix == 0:
            colors[ix] = '#000000'
        else:
            if ix==1:
                colors[ix] = '#2ca02c'
            elif ix== len(best_guess)-2:
                colors[ix] = '#d62728'
            else:
                colors[ix] = '#17becf'

        icon_number = BeautifyIcon(
            border_color=colors[ix],
            text_color='#000000',
            number=ix,
            iconSize = [30,30],
            inner_icon_style='margin-top:10;'
        )

        folium.Marker(
            location=[address_coordinates[i][0], address_coordinates[i][1]],
            tooltip=address_names[i],
            icon=icon_number
        ).add_to(m)

    return m