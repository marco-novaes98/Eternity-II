# Myriam KIRIAKOS 1888929
# Marco NOVAES 2166579

from eternity_puzzle import NORTH, SOUTH, WEST, EAST
import random

def solve_heuristic(eternity_puzzle):
    """
    Heuristic solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """
    def get_conflict_one_piece(i, j, solution):
        """
        Get the number of conflict for position [i,j] in `solution`
        :param i: line of the piece
        :param j: column of the piece
        :return: number of conflict for one position [i,j] in `solution` + list of the color involved in each conflicts
        """
        n_conflict = 0
        colors_in_conflict = []

        # The first condition in if statements is to ignore non-assigned neighboors

        if solution[i+1][j] and solution[i][j][NORTH] != solution[i+1][j][SOUTH]:
            n_conflict+=1
            colors_in_conflict.append(solution[i][j][NORTH])

        if solution[i-1][j] and solution[i][j][SOUTH] != solution[i-1][j][NORTH]:
            n_conflict+=1
            colors_in_conflict.append(solution[i][j][SOUTH])
        
        if solution[i][j+1] and solution[i][j][EAST] != solution[i][j+1][WEST]:
            n_conflict+=1
            colors_in_conflict.append(solution[i][j][EAST])

        if solution[i][j-1] and solution[i][j][WEST] != solution[i][j-1][EAST]:
            n_conflict+=1
            colors_in_conflict.append(solution[i][j][WEST])

        return n_conflict, colors_in_conflict

    def calculate_color_stat(conflict_color, colors):
        """
        Calculate the `color_stat_piece` for `conflict_color`. 
            `color_stat_piece` is the product of the frequency (calculated with `colors`) of each colour in `conflict_color`.
        :param conflict_color: list of the color involved in each conflicts for a piece
        :param colors: dictionary with the cardinality of each colour for the remaining pieces
        :return: `color_stat_piece`
        """
        color_stat_piece = 1.
        numberOfAllRemainingEdges = sum(colors.values())
        for c in conflict_color:
            color_stat_piece *= float(colors[c]) / numberOfAllRemainingEdges
        return color_stat_piece

    def dealing_with_piece(solution, piece, i, j, n_less_conflict, piece_less_conflict, color_stat_less_conflict, colors):
        """
        Check if `piece` is better than `piece_less_conflict`. A piece is considered better than another one if it has less conflicts. 
            In case of a tie, the piece with the minimum color_stat (see calculate_color_stat) is considered better.
        :param solution: current solution (list of list)
        :param piece: current piece
        :param i: x coordinate of the position to fill
        :param j: y coordinate of the position to fill
        :param n_less_conflict: current minimum number of conflicts for position [i,j] using the remaining pieces
        :param piece_less_conflict: current best piece 
        :param color_stat_less_conflict: color_stat (see calculate_color_stat) of `piece_less_conflict`
        :param colors: dictionary with the cardinality of each colour for the remaining pieces
        """
        solution[i][j] = piece
        has_piece_changed = False
        n_conflict_for_this_piece, conflict_colors = get_conflict_one_piece(i, j, solution)
        color_stat_piece = calculate_color_stat(conflict_colors, colors)

        # `piece` is the new best option because it has less conflicts than all previous options
        if n_conflict_for_this_piece < n_less_conflict:
            n_less_conflict = n_conflict_for_this_piece
            piece_less_conflict = piece
            has_piece_changed = True
            color_stat_less_conflict = color_stat_piece

        elif n_conflict_for_this_piece == n_less_conflict:

            # `piece` is the new best option because, among the pieces with less conflicts, the colours of its conflicts involve uncommon color
            if color_stat_piece < color_stat_less_conflict:
                piece_less_conflict = piece
                has_piece_changed = True
                color_stat_less_conflict = color_stat_piece

        return piece_less_conflict, color_stat_less_conflict, n_less_conflict, has_piece_changed

    def choose_piece(i, j, solution, colors, pieces):
        """
        Assign a piece to position [i,j] (criteria defined in dealing_with_piece() header)
        :param i: x coordinate of the position to fill
        :param j: y coordinate of the position to fill
        :param solution: current solution (list of list)
        :param colors: dictionary with the cardinality of each colour for the remaining pieces
        :param pieces: list of remaining pieces
        """
        # Minimum number of conflicts for position [i,j] using the remaining pieces. 
        # Initialised to 5 (upper bound) and the value will be reduced when testing all possibilities
        n_less_conflict = 5 
        chosen_piece = None
        color_stat = 1.
        index_to_remove = None
        for index, piece in enumerate(pieces):
            # Get list with the 4 possibles values for a piece apllying rotations
            all_rotation_for_piece = eternity_puzzle.generate_rotation(piece)
            for possible_rotation in all_rotation_for_piece:
                # Check if `possible_rotation` is the best choice (criteria defined in dealing_with_piece() header)
                chosen_piece, color_stat, n_less_conflict, has_piece_changed = dealing_with_piece(solution, possible_rotation, i, j, 
                                                                                n_less_conflict, chosen_piece, color_stat
                                                                                , colors)
                if has_piece_changed:
                    index_to_remove = index

        solution[i][j] = chosen_piece
        pieces.pop(index_to_remove)
        
    def add_corners(coord_corners, solution, colors, pieces):
        """
        Assign a piece to each corner
        :param coord_corners: list with the coordinates of the corners of the current perimeter (from outside to inside)
        :param solution: current solution (list of list)
        :param colors: dictionary with the cardinality of each colour for the remaining pieces
        :param pieces: list of remaining pieces
        """
        # Check if perimeter of size 1
        if coord_corners[0] == coord_corners[1]: 
            choose_piece(coord_corners[0][0], coord_corners[0][1], solution, colors, pieces)
        else:
            for edge in coord_corners:
                choose_piece(edge[0], edge[1], solution, colors, pieces)

    def add_edges(coord_corners, solution, colors, pieces):
        """
        Assign a piece to each case in the current perimeter (execept corners)
        :param coord_corners: list with the coordinates of the corners of the current perimeter (from outside to inside)
        :param solution: current solution (list of list)
        :param colors: dictionary with the cardinality of each colour for the remaining pieces
        :param pieces: list of remaining pieces
        """
        size = coord_corners[1][1] - coord_corners[0][1] - 1
        # Loop to cover the 4 sides of the current perimeter (execept corners)
        for inc in range(1, size+1):
            choose_piece(coord_corners[0][0], coord_corners[0][1] + inc, solution, colors, pieces)
            choose_piece(coord_corners[1][0] + inc, coord_corners[1][1], solution, colors, pieces)
            choose_piece(coord_corners[2][0], coord_corners[2][1] - inc, solution, colors, pieces)
            choose_piece(coord_corners[3][0] - inc, coord_corners[3][1], solution, colors, pieces)

    def update_corners(coord_corners):
        """
        Once the current perimeter has been filled, `coord_corners` is updated to point the next perimeter (one case inwards with respect to the current perimeter)
        :param coord_corners: list with the coordinates of the corners of the current perimeter
        """
        coord_corners[0] = [coord_corners[0][0] + 1, coord_corners[0][1] + 1]
        coord_corners[1] = [coord_corners[1][0] + 1, coord_corners[1][1] - 1]
        coord_corners[2] = [coord_corners[2][0] - 1, coord_corners[2][1] - 1]
        coord_corners[3] = [coord_corners[3][0] - 1, coord_corners[3][1] + 1]


    ### INITIALISATION ###
    random.seed(1)
    n = eternity_puzzle.board_size
    pieces = eternity_puzzle.piece_list
    flatten = [pos for piece in pieces for pos in piece]
    m = n + 2
    colors = {}
    coord_corners = [[1, 1], [1, n], [n, n], [n, 1]]
    notFinished = True

    # Count the number of pieces of each colour
    for i in range(eternity_puzzle.n_color):
        colors[i] = flatten.count(i)

    #Create format solution with an additional external perimeter fill with (0, 0, 0, 0) 
    solution = [[(0, 0, 0, 0) if (i == 0 or j == 0 or i == m-1 or j == m-1) else None for i in range(m)] for j in range(m)] 

    ### SOLUTION CONSTRUCTION (GREEDY HEURISTIC) ###
    while notFinished:
        add_corners(coord_corners, solution, colors, pieces)
        # Check if the solution is complete
        if coord_corners[1][1] - coord_corners[0][1] >= 2:
            add_edges(coord_corners, solution, colors, pieces)
            update_corners(coord_corners)
        else:
            notFinished = False
    
    # remove the border and flatten to fit the formatting solution
    solution = [pos for piece in solution for pos in piece if pos != (0,0,0,0)]
    return solution, eternity_puzzle.get_total_n_conflict(solution)


