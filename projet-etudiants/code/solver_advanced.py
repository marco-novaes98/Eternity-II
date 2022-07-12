# Myriam KIRIAKOS 1888929
# Marco NOVAES 2166579

import copy
import time
import random
import numpy as np
from eternity_puzzle import NORTH, SOUTH, WEST, EAST

def solve_advanced(eternity_puzzle):
    """
    Your solver for the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """
   
    def get_conflict_one_piece(i, j, solution):
        """
        Get the number of conflict for position [i,j] in `solution`
        :param i: line of the piece
        :param j: column of the piece
        :return: number of conflict for one position [i,j] in `solution` 
        """
        n_conflict = 0

        # The first condition in if statements is to ignore non-assigned neighboors

        if solution[i+1][j] and solution[i][j][NORTH] != solution[i+1][j][SOUTH]:
            n_conflict+=1

        if solution[i-1][j] and solution[i][j][SOUTH] != solution[i-1][j][NORTH]:
            n_conflict+=1
        
        if solution[i][j+1] and solution[i][j][EAST] != solution[i][j+1][WEST]:
            n_conflict+=1

        if solution[i][j-1] and solution[i][j][WEST] != solution[i][j-1][EAST]:
            n_conflict+=1

        return n_conflict

    def choose_piece(i, j, solution, pieces):
        """
        Assign a piece to position [i,j] (criteria defined in dealing_with_piece() header)
        :param i: x coordinate of the position to fill
        :param j: y coordinate of the position to fill
        :param solution: current solution (list of list)
        :param pieces: list of remaining pieces
        """
        # Minimum number of conflicts for position [i,j] using the remaining pieces. 
        # Initialised to 4 (upper bound) and the value will be reduced when testing all possibilities
        n_less_conflict = 5
        best_pieces = []
        for index, piece in enumerate(pieces):

            # Get list with the 4 possibles values for a piece applying rotations
            all_rotation_for_piece = eternity_puzzle.generate_rotation(piece)
            for rotatedPiece in all_rotation_for_piece:
                # Check if `rotatedPiece` is the best choice (criteria defined in dealing_with_piece() header)
                solution[i][j] = rotatedPiece
                currentNbConflicts = get_conflict_one_piece(i, j, solution)

                if currentNbConflicts < n_less_conflict:
                    best_pieces = [(index, rotatedPiece)]
                    n_less_conflict = currentNbConflicts
                
                elif currentNbConflicts == n_less_conflict:
                    best_pieces.append(((index, rotatedPiece)))
        
        chosen_index, chosen_piece = random.choice(best_pieces)
        solution[i][j] = chosen_piece
        pieces.pop(chosen_index)
        
    def add_corners(coord_corners, solution, pieces):
        """
        Assign a piece to each corner
        :param coord_corners: list with the coordinates of the corners of the current perimeter (from outside to inside)
        :param solution: current solution (list of list)
        :param pieces: list of remaining pieces
        """
        # Check if perimeter of size 1
        if coord_corners[0] == coord_corners[1]: 
            choose_piece(coord_corners[0][0], coord_corners[0][1], solution, pieces)
        else:
            for edge in coord_corners:
                choose_piece(edge[0], edge[1], solution, pieces)

    def add_edges(coord_corners, solution, pieces):
        """
        Assign a piece to each case in the current perimeter (execept corners)
        :param coord_corners: list with the coordinates of the corners of the current perimeter (from outside to inside)
        :param solution: current solution (list of list)
        :param pieces: list of remaining pieces
        """
        size = coord_corners[1][1] - coord_corners[0][1] - 1
        # Loop to cover the 4 sides of the current perimeter (execept corners)
        for inc in range(1, size+1):
            choose_piece(coord_corners[0][0], coord_corners[0][1] + inc, solution, pieces)
            choose_piece(coord_corners[1][0] + inc, coord_corners[1][1], solution, pieces)
            choose_piece(coord_corners[2][0], coord_corners[2][1] - inc, solution, pieces)
            choose_piece(coord_corners[3][0] - inc, coord_corners[3][1], solution, pieces)

    def update_corners(coord_corners):
        """
        Once the current perimeter has been filled, `coord_corners` is updated to point the next perimeter (one case inwards with respect to the current perimeter)
        :param coord_corners: list with the coordinates of the corners of the current perimeter
        """
        coord_corners[0] = [coord_corners[0][0] + 1, coord_corners[0][1] + 1]
        coord_corners[1] = [coord_corners[1][0] + 1, coord_corners[1][1] - 1]
        coord_corners[2] = [coord_corners[2][0] - 1, coord_corners[2][1] - 1]
        coord_corners[3] = [coord_corners[3][0] - 1, coord_corners[3][1] + 1]

    def generate_initial_solution():
        """
        Generate a dreedy randomized initial solution
        :return: an initial solution
        """
        ### INITIALISATION ###
        n = eternity_puzzle.board_size
        pieces = copy.copy(eternity_puzzle.piece_list)
        m = n + 2
        coord_corners = [[1, 1], [1, n], [n, n], [n, 1]]
        notFinished = True

        #Create format solution with an additional external perimeter fill with (0, 0, 0, 0) 
        solution = [[(0, 0, 0, 0) if (i == 0 or j == 0 or i == m-1 or j == m-1) else None for i in range(m)] for j in range(m)] 

        ### SOLUTION CONSTRUCTION (GREEDY HEURISTIC) ###
        while notFinished:
            add_corners(coord_corners, solution, pieces)
            # Check if the solution is complete
            if coord_corners[1][1] - coord_corners[0][1] >= 2:
                add_edges(coord_corners, solution, pieces)
                update_corners(coord_corners)
            else:
                notFinished = False
        
        # remove the border and flatten to fit the formatting solution
        solution = [pos for piece in solution for pos in piece if pos != (0,0,0,0)]
        return solution, eternity_puzzle.get_total_n_conflict(solution)

    def repair_choose_piece(removedIdxs, solution, pieces):
        """
        Assign a piece that generate the minimum number of conflicts to position `k` 
        :param removedIdxs: list of indexes of the cases to fill
        :param solution: current solution (list of list)
        :param pieces: list of remaining pieces
        """
        for k in removedIdxs:
            # Minimum number of conflicts for position `k` using the remaining pieces. 
            # Initialised to 5 (upper bound) and the value will be reduced while testing all possibilities
            n_less_conflict = 5
            optimalMatchFound = False
            for index, piece in enumerate(pieces):

                # Get list with the 4 possibles values for a piece applying rotations
                all_rotation_for_piece = eternity_puzzle.generate_rotation(piece)
                random.shuffle(all_rotation_for_piece) # Add some diversity
                for rotatedPiece in all_rotation_for_piece:
                    # Check if `rotatedPiece` is one of the best choices (criteria defined in header)
                    solution[k] = rotatedPiece
                    currentNbConflicts = eternity_puzzle.get_local_n_conflict(k, solution)

                    if currentNbConflicts < n_less_conflict:
                        best_piece = (index, rotatedPiece)
                        n_less_conflict = currentNbConflicts
                        # If a non-conflicting piece is found, the search is stopped
                        if currentNbConflicts == 0:
                            pieces.pop(index)
                            optimalMatchFound = True # Bool to handle when a non-conflicting piece is found
                            break
                if optimalMatchFound:
                    break # Force to move to the next index 

            # Update variables with the best non-optimal piece found
            if not optimalMatchFound:        
                chosen_index, chosen_piece = best_piece
                solution[k] = chosen_piece
                pieces.pop(chosen_index)

    def destroy(solution, nbWorst, nbRandom):
        """
        De-assign `nbWorst` + `nbRandom` pieces from `solution`
        :param solution: current solution 
        :param nbWorst: number of pieces to be de-assigned by selecting the pieces with the most conflicts first
        :param nbRandom: number of pieces to be de-assigned by selecting randomly
        :return : destroyed solution, list of indexes of de-assigned cases, list of de-assigned pieces
        """
        ### Selection of `nbWorst` worst pieces ###
        if nbWorst != 0:
            listConflicts = np.empty(eternity_puzzle.n_piece)
            for index, piece in enumerate(solution):
                np.put(listConflicts, index, eternity_puzzle.get_local_n_conflict(index, solution))
            idxWorst = set(np.argpartition(listConflicts, -nbWorst)[-nbWorst:])
        else:
            idxWorst = set()

        ### Selection of `nbRandom` random pieces ###
        # Make sure that `idxWorst` and `idxRandom` are disjoint sets
        randomCandidates = set(range(eternity_puzzle.n_piece)) - idxWorst 
        idxRandom = random.sample(randomCandidates, nbRandom)

        ### Generate variables to return ###
        idxWorst = list(idxWorst)
        removedIdxs = idxWorst + idxRandom
        removedPieces = [solution[idx] for idx in removedIdxs]
        initDestroyedSolution = copy.copy(solution)
        for idx in removedIdxs:
            # -1 is a neutral value, it can't generate a conflict in function `get_local_n_conflict()`
            initDestroyedSolution[idx] = (-1, -1, -1, -1)
        
        return initDestroyedSolution, removedIdxs, removedPieces

    ### INITIALISATION ###
    start_time = time.time()  
    random.seed(1)
    isOptimal = False # Bool to stop search if optimal solution (zero conflicts) is found
    bestSolution = None
    bestScore = 1000 # init to upper bound
    solution = None

    # Hyperparameters
    timeLimit = 60
    if eternity_puzzle.board_size == 4: # Instance A
        proportionWorst = 0.15
        proportionRandom = 0.15
        limitIterNoImprovement = 150
        nbRepairIter = 150
    elif eternity_puzzle.board_size == 7: # Instance B
        proportionWorst = 0.075
        proportionRandom = 0.15
        limitIterNoImprovement = 75
        nbRepairIter = 75
    elif eternity_puzzle.board_size == 8: # Instance C
        proportionWorst = 0.075
        proportionRandom = 0.075
        limitIterNoImprovement = 75
        nbRepairIter = 75
    elif eternity_puzzle.board_size == 9: # Instance D
        proportionWorst = 0.075
        proportionRandom = 0.15
        limitIterNoImprovement = 150
        nbRepairIter = 75
    elif eternity_puzzle.board_size == 10: # Instance E
        proportionWorst = 0.15
        proportionRandom = 0.075
        limitIterNoImprovement = 150
        nbRepairIter = 150
    elif eternity_puzzle.board_size == 16: # Instance complet
        proportionWorst = 0.075
        proportionRandom = 0.075
        limitIterNoImprovement = 75
        nbRepairIter = 75
    else: # Unknown instance
        proportionWorst = 0.075
        proportionRandom = 0.075
        limitIterNoImprovement = 75
        nbRepairIter = 75

    nbWorst = round(eternity_puzzle.n_piece*proportionWorst)
    nbRandom = round(eternity_puzzle.n_piece*proportionRandom)
    
    ### RESTART ###
    nbRestart = 0
    while round((time.time() - start_time) / 60,2) < timeLimit and not isOptimal:
        nbRestart += 1

        ### GENERATE INITIAL SOLUTION (GRASP) ###
        solution, nbConflicts = generate_initial_solution()
        
        ### LOCAL SEARCH (LNS) ###
        destroyIter = 0
        bestScoreRestart = eternity_puzzle.get_total_n_conflict(solution)
        while destroyIter < limitIterNoImprovement and round((time.time() - start_time) / 60,2) < timeLimit and not isOptimal:
            destroyIter += 1

            ### DESTROY ###
            initDestroyedSolution, removedIdxs, removedPieces = destroy(solution, nbWorst, nbRandom)

            ### REPAIR ###
            for repairIter in range(nbRepairIter):

                # Init and shuffle
                destroyedSolution = copy.copy(initDestroyedSolution)
                localRemovedPieces = copy.copy(removedPieces)
                random.shuffle(localRemovedPieces)
                if repairIter != 0:
                    random.shuffle(removedIdxs)

                # Repair solution
                repair_choose_piece(removedIdxs, destroyedSolution, localRemovedPieces)
                
                # Check if the repaired solution is a local upgrade
                localScore = eternity_puzzle.get_total_n_conflict(destroyedSolution)
                if localScore < bestScoreRestart:
                    bestScoreRestart = localScore
                    solution = copy.copy(destroyedSolution)
                    destroyIter = 0
     
        
        # Check if the local search has found a better global solution
        if bestScoreRestart < bestScore:
            bestSolution = solution
            bestScore = bestScoreRestart
            # Stop search if optimal solution is founds
            if bestScore == 0:
                isOptimal = True

    return bestSolution, bestScore        
