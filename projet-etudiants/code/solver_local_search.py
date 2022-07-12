# Myriam KIRIAKOS 1888929
# Marco NOVAES 2166579

import random
from eternity_puzzle import NORTH, SOUTH, WEST, EAST
import copy
import time

def solve_local_search(eternity_puzzle):
    """
    Local search solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """

    def generate_initial_solution():
        """
        Random solution such that the corner pieces are placed randomly in the corner positions and the same applies to the edge pieces and internal pieces.  
        :return: an initial solution      
        """
        # Create format solution with an additional external perimeter fill with (0, 0, 0, 0) 
        size = eternity_puzzle.board_size
        bigSize = size + 2
        pieces = eternity_puzzle.piece_list
        solution = [[(0, 0, 0, 0) if (i == 0 or j == 0 or i == bigSize-1 or j == bigSize-1) else None for i in range(bigSize)] for j in range(bigSize)] 
        limits = (1,size)

        # Split pieces in 3 lists (corners, edges and interns) + shuffle
        corners = []
        edges = []
        interns = []
        for piece in pieces:
            if piece.count(0) == 0:
                interns.append(piece)
            elif piece.count(0) == 1:
                edges.append(piece)
            else:
                corners.append(piece)
        random.shuffle(corners)
        random.shuffle(edges)
        random.shuffle(interns)
                
        # Create random solution
        for i in range(1, size+1):
            for j in range(1, size+1):
                if i in limits and j in limits: #corner
                    solution[i][j] = corners.pop()
                elif i in limits or j in limits: #edge
                    solution[i][j] = edges.pop()
                else: # intern
                    solution[i][j] = interns.pop()

        return solution

    ### INITIALISATION ###

    start_time = time.time()  
    size = eternity_puzzle.board_size
    timeLimit = 10
    random.seed(1)

    # Initialisation for bestScore and bestSolution
    solution = generate_initial_solution()
    flatSolution = [pos for piece in solution for pos in piece if pos != (0,0,0,0)]
    bestSolution = flatSolution
    bestScore = eternity_puzzle.get_total_n_conflict(flatSolution)

    # Bool to stop search if optimal solution (zero conflicts) is found
    isOptimal = False

    ### (RE)START SEARCH ###
    while round((time.time() - start_time) / 60,2) < timeLimit and not isOptimal:

        # Initialisation    
        solution = generate_initial_solution()
        flatSolution = [pos for piece in solution for pos in piece if pos != (0,0,0,0)]
        bestLocalScore = eternity_puzzle.get_total_n_conflict(flatSolution)
        if bestLocalScore < bestScore:
            bestScore = bestLocalScore
            bestSolution = flatSolution

        ### LOCAL SEARCH ###
        count = 0
        limitIterNoImprovement = 5000
        while count < limitIterNoImprovement and round((time.time() - start_time) / 60,2) < timeLimit and not isOptimal:
            count += 1

            # Random selection of 2 pieces
            coord1 = (random.randint(1, size), random.randint(1, size))
            coord2 = (random.randint(1, size), random.randint(1, size))
            piece1 = solution[coord1[0]][coord1[1]]
            piece2 = solution[coord2[0]][coord2[1]]
        
            # Try all the possible changes (4*4*2=32) and choose the best one
            # 4 rotation for piece1, 4 rotation for piece2, bool for swap/no-swap pieces 
            mutableSolution = copy.deepcopy(solution)
            rotations_piece1 = eternity_puzzle.generate_rotation(piece1)
            rotations_piece2 = eternity_puzzle.generate_rotation(piece2)
            for i in range(4): #turn piece1
                for j in range(4): #turn piece2
                    for k in range(2): #swap pieces1 <-> piece2
                        if k:
                            mutableSolution[coord1[0]][coord1[1]] = rotations_piece1[i]
                            mutableSolution[coord2[0]][coord2[1]] = rotations_piece2[j]
                        else:
                            mutableSolution[coord1[0]][coord1[1]] = rotations_piece2[j]
                            mutableSolution[coord2[0]][coord2[1]] = rotations_piece1[i]
                        
                        # Update if better local solution is found
                        flatmutableSolution = [pos for piece in mutableSolution for pos in piece if pos != (0,0,0,0)]
                        currentScore = eternity_puzzle.get_total_n_conflict(flatmutableSolution)
                        if currentScore < bestLocalScore:
                            bestLocalScore = currentScore
                            solution = copy.deepcopy(mutableSolution)
                            count = 0

            # Update if better global solution is found
            if bestLocalScore < bestScore:
                flatSolution = [pos for piece in solution for pos in piece if pos != (0,0,0,0)]
                bestScore = bestLocalScore
                bestSolution = flatSolution
                if bestScore == 0:
                    isOptimal = True
                    break
                                   
    return bestSolution, bestScore


