#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from math import inf
import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    # Function that returns a list of all legal moves for a given position
    def find_all_legal_moves(self, N, game_state: GameState):
        # For a move to be declared legal, the following conditions cannot be satisfied:
        # (i) The cell of the proposed move is already filled in
        # (ii) The proposed value is not in range 1,...,N
        # (iii) Executing the proposed move would violate C0
        # (iv) The Proposed Move has previously been declared Taboo

        # Initialize list for all possible moves
        all_moves = []

        # For the sake of clarity I'm gonna write the nested for loop in a more expanded way
        # compared to the one provided in team10_A0/sudokuai.py
        for i in range(N):
            for j in range(N):
                # loop over all possible cells
                for value in range(1, N+1):  # loop over all possible values
                    # Because I loop with range(1,N+1) (so exluding N+1), (ii) cannot occur
                    # so does not have to be checked
                    if game_state.board.get(i, j) != SudokuBoard.empty:
                        continue  # if (i) -> this move cannot be allowed

                    # (iv)
                    # If a move has been considered taboo, don't consider this move
                    if TabooMove(i, j, value) in game_state.taboo_moves:
                        continue

                    # do (iii) last, save a lot of hassle
                    # check relative position in block
                    m = game_state.board.m
                    n = game_state.board.n
                    cells_above = i % m
                    cells_below = m - cells_above
                    # the value of cell_below is actually 1 too high for what the name suggests,
                    # but this is intentional for looping correctly in the next part
                    cells_left = j % n
                    cells_right = n - cells_left  # same story as cells_below

                    # check if value already exists in block, if so -> go to next possible move
                    legal = True
                    for check_i_block in range(i-cells_above, i+cells_below):
                        for check_j_block in range(j-cells_left, j+cells_right):
                            if game_state.board.get(check_i_block, check_j_block) == value:
                                legal = False

                    if not legal:
                        continue

                    # check if value already exists in row
                    for check_i_rows in [x for x in range(N) if x not in range(i-cells_above, i+cells_below)]:
                        if game_state.board.get(check_i_rows, j) == value:
                            legal = False
                            break

                    if not legal:
                        continue

                    # check if value already exists in column
                    for check_j_cols in [x for x in range(N) if x not in range(j-cells_left, j+cells_right)]:
                        if game_state.board.get(i, check_j_cols) == value:
                            legal = False
                            break

                    if legal:
                        all_moves.append(Move(i, j, value))

        return all_moves

    # Evaluate function for a given game state, returns numerical score

    def evaluation_function(self, game_state: GameState):
        # for now, just return random int
        return random.randint(-5, 5)

    # implementation of minimax, using alpha-beta-pruning
    def alpha_beta_pruning(self, N, game_state: GameState, depth, alpha, beta, isMaximizing, played_move=None):

        # get all legal moves for current state
        all_legal_moves = self.find_all_legal_moves(N, game_state)

        if depth == 0 or not all_legal_moves:
            # if we are at the specified depth or there are no more possible moves to play,
            # evaluate the board position
            evaluation_score = self.evaluation_function(game_state)
            # print("Score: {}, Move: {}, alpha: {}, beta: {}".format(
            #     evaluation_score, played_move, alpha, beta))
            return {'move': played_move, 'score': evaluation_score}

        if isMaximizing:
            # so the first option will always be better
            maxEval = {'move': 'default', 'score': -inf}
            # recursively go through all children (child = board with legal move played)
            # alpha and beta keep track of the best moves that can be played on other parts
            # of the tree. If it is impossible to score better in the current part of the
            # tree (from maximizing player's perspective), the search is stopped, and we
            # look at the next region where there is still the possibility for improvement
            for next_move in all_legal_moves:
                child = game_state
                # perform next move
                child.board.put(next_move.i, next_move.j, next_move.value)
                # get leaf-node evaluation score linked to this child as 'score',
                # and keep track of what move this child represents in 'move'
                child_evaluation = self.alpha_beta_pruning(
                    N, child, depth-1, alpha, beta, False, next_move)
                child_eval_score = child_evaluation['score']
                # update maxEval if this child leads to a leaf node with higher score
                if child_eval_score >= maxEval['score']:
                    maxEval = child_evaluation
                # keep track of highest score on this side of the tree
                if child_eval_score >= alpha:
                    alpha = child_eval_score
                # if our opponent will certainly choose our sibling, stop searching here
                if beta <= alpha:
                    break

            # This next if statement is there to decide what to return in ['move']
            # if we are at the root node, then return the move of our favorite child (so e.g. (0,0) -> 1)
            # if we are not at the root node return the move we represent ourselves.
            # This is done to keep track of which move we should be playing when we get back to the top of the tree
            if played_move:
                # print("Score: {}, Move: {}, alpha: {}, beta: {}".format(
                #     maxEval['score'], played_move, alpha, beta))
                return {'move': played_move, 'score': maxEval['score']}
            else:
                # print("Score: {}, Move: {}, alpha: {}, beta: {}".format(
                #     maxEval['score'], maxEval['move'], alpha, beta))
                return maxEval

        # recurively go through all children (child = board with legal move played)
        # alpha and beta keep track of the best moves that can be played on other parts
        # of the tree. If it is impossible to score better in the current part of the
        # tree (from minimizing player's perspective), the search is stopped, and we
        # look at the next region where there is still the possibility for improvement
        else:
            minEval = {'move': 'default', 'score': inf}
            for next_move in all_legal_moves:
                child = game_state
                # perform next move
                child.board.put(next_move.i, next_move.j, next_move.value)
                # get leaf-node evaluation score linked to this child as 'score',
                # and keep track of what move this child represents in 'move'
                child_evaluation = self.alpha_beta_pruning(
                    N, child, depth-1, alpha, beta, True, next_move)
                child_eval_score = child_evaluation['score']
                # update minEval if this child leads to a leaf node with lower score
                if child_eval_score <= minEval['score']:
                    minEval = child_evaluation
                # keep track of lowest score on this side of the tree
                if child_eval_score <= minEval['score']:
                    beta = child_eval_score
                # if our opponent will certainly choose our sibling, stop searching here
                if beta <= alpha:
                    break

            # This next if statement is there to decide what to return in ['move']
            # if we are at the root node, then return the move of our favorite child (so e.g. (0,0) -> 1)
            # if we are not at the root node return the move we represent ourselves.
            # This is done to keep track of which move we should be playing when we get back to the top of the tree
            if played_move:
                # print("Score: {}, Move: {}, alpha: {}, beta: {}".format(
                #     minEval['score'], played_move, alpha, beta))
                return {'move': played_move, 'score': minEval['score']}
            else:
                # print("Score: {}, Move: {}, alpha: {}, beta: {}".format(
                #     minEval['score'], minEval['move'], alpha, beta))
                return minEval

    # Function that looks for the best move using (a variant of) minimax
    def compute_best_move(self, game_state: GameState) -> None:

        N = game_state.board.N

        # I want to include something like iterative deepening to go to lower and lower depths
        # but for now this suffices
        best_move = self.alpha_beta_pruning(
            N, game_state, 5, -inf, inf, True)['move']

        self.propose_move(best_move)

        while True:
            time.sleep(0.2)
            self.propose_move(best_move)
