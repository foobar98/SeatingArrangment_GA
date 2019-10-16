import random
import matplotlib.pyplot as plt
import operator
import copy

# Function to generate a valid seating arrangement
def generatePermutation(row,col,persons):
    ini = []
    for i in range(1,persons+1):
        ini.append(i)

    random.shuffle(ini)
    arr = [ini[i:i+row] for i in range(0,len(ini),row)]
    return arr

# Function to generate initial population of size POP_SIZE
def generateInitialPopulation(POP_SIZE,row,col,persons):
    population = []
    for i in range(POP_SIZE):
        population.append(generatePermutation(row,col,persons))
    return population

# Function to calculate fitness of a solution
def getFitness(individual,happiness):
    f = 0
    # Define direction arrays
    dx = [1,-1,0,0,1,1,-1,-1]
    dy = [0,0,1,-1,1,-1,1,-1]

    row = len(individual)
    col = len(individual[0])

    # Loop over every person in arrangement and calculate sum of Cumulative Happiness Factor (CHF) for each
    for i in range(row):
        for j in range(col):
            val = individual[i][j]
            chf = 0.0
            # Taking into account persons seated at all 8 directions
            for k in range(8):
                ni = i+dy[k]
                nj = j+dx[k]
                if ni>=0 and ni<row and nj>=0 and nj<col:
                    neighbour = individual[ni][nj]
                    if k>3:
                        chf += happiness[val-1][neighbour-1]/1.414
                    else:
                        chf += happiness[val-1][neighbour-1]
            # Add CHF of person to overall fitness
            f += chf
    
    return f

# Selection function
def selectParent(population):
    size = len(population)

    # Randomly select 2 solutions from mating pool
    idx1 = random.randint(0,size-1)
    idx2 = random.randint(0,size-1)
    
    # Apply tournament selection method to select parent
    r = random.uniform(0,1)
    if r<0.75:
        if population[idx1][1]>population[idx2][1]:
            return population[idx1][0]
        else:
            return population[idx2][0]
    else:
        if population[idx1][1]>population[idx2][1]:
            return population[idx2][0]
        else:
            return population[idx1][0]

# Crossover function
def crossover(parent1,parent2):
    row = len(parent1)
    col = len(parent1[0])

    # Randomly generate a crossover point
    cpI = random.randint(0,row-1)
    cpJ = random.randint(0,col-1)

    # Generate offsprings by Horizontal Substring Crossover Method
    child1 = []
    for i in range(cpI):
        child1.append(parent1[i])
    rowMid = []
    for j in range(cpJ+1):
        rowMid.append(parent1[cpI][j])
    for j in range(cpJ+1,col):
        rowMid.append(parent2[cpI][j])
    child1.append(rowMid)
    for i in range(cpI+1,row):
        child1.append(parent2[i])

    child2 = []
    for i in range(cpI):
        child2.append(parent2[i])
    rowMid = []
    for j in range(cpJ+1):
        rowMid.append(parent2[cpI][j])
    for j in range(cpJ+1,col):
        rowMid.append(parent1[cpI][j])
    child2.append(rowMid)
    for i in range(cpI+1,row):
        child2.append(parent1[i])

    # Return generated offsprings
    return (child1,child2)

# Function to perform mutation
def mutate(individual):
    row = len(individual)
    col = len(individual[0])

    # Choose 2 points randomly and swap their values
    idx1 = random.randint(0,row*col-1)
    idx2 = random.randint(0,row*col-1)
    i1 = idx1//col
    i2 = idx2//col
    j1 = idx1%col
    j2 = idx2%col

    individual[i1][j1],individual[i2][j2] = individual[i2][j2],individual[i1][j1]

# Function to check if a solution is valid permuation of integers or not
def checkSolution(individual,persons):
    # Calculate frequency of occurence of each person
    freq = [0]*persons
    for row in individual:
        for val in row:
            freq[val-1] += 1

    for i in range(persons):
        if freq[i]!=1:
            return False    
    return True

def main():
    # Define variables
    X = []
    Y = []
    best = []
    bestFitness = -100000

    # Define parameters
    POP_SIZE = 2000
    NO_GEN = 50
    MUTATION_PROB = 0.03

    # Take input from text file
    with open('input.txt') as f:
        persons = int(next(f))
        # Dimensions of seating layout
        row,col = [int(x) for x in next(f).split()]
        # Happiness matrix
        happiness = []
        for line in f:
            happiness.append([int(x) for x in line.split()])

    # Generate initial population
    population = generateInitialPopulation(POP_SIZE,row,col,persons)
    weightedPopulation = []

    # Loop through number of generations
    for generation in range(NO_GEN):
        weightedPopulation.clear()

        # Calculate ftiness of each individual in current population and store
        for individual in population:
            fitness = getFitness(individual,happiness)
            new_ind = copy.deepcopy(individual)
            weightedPopulation.append((new_ind,fitness))

        # Store population in descending order of fitness
        weightedPopulation.sort(key=operator.itemgetter(1),reverse=True)

        population.clear()

        # Send top 10% solutions to the next generation without any change (Elitism)
        for i in range(POP_SIZE//10):
            new_list = copy.deepcopy(weightedPopulation[i][0])
            population.append(new_list)

        # Fill the rest of the population from the current mating pool
        while len(population)<POP_SIZE:
            # Select 2 parent for mating
            parent1 = selectParent(weightedPopulation)
            parent2 = selectParent(weightedPopulation)

            # Do crossover to generate offsprings
            child1,child2 = crossover(parent1,parent2)
            
            # Mutate offsprings with probability = MUTATION_PROB
            k = random.uniform(0,1)
            if k<MUTATION_PROB:
                mutate(child1)
                mutate(child2)

            # If offsprings generated are valid, add it to population for next generation
            if checkSolution(child1,persons):
                population.append(child1)

            if checkSolution(child2,persons):
                population.append(child2)

        # Print best solution from current generation
        currBestSolution = weightedPopulation[0][0]
        currBestFitness = weightedPopulation[0][1]
        print("Generation", generation+1, ":", currBestSolution, ",", currBestFitness)

        # Store current best for graphical analysis
        X.append(generation+1)
        Y.append(currBestFitness)

        # Check if current best is better than best solution uptill now
        if currBestFitness>bestFitness:
            best = currBestSolution
            bestFitness = currBestFitness

    # Output best arrangement obtained after NO_GEN number of generations
    print()
    print("Best seating arrangement after",NO_GEN,"generations: ")
    for row in best:
        print(*row,sep=" ")
    print("With happiness score:",bestFitness)

    # Plot graph mapping generation with its corresponding best solution fitness
    plt.plot(X,Y,'bo-')
    plt.xlabel('Generation')
    plt.ylabel('Fitness Score')
    plt.title('Best Fitness: %d' % bestFitness)
    plt.show()

main()
