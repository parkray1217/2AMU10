#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

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
                    # I assume now that TabooMove contains all previously considered taboo_moves as well,
                    # have to check this tomorrow. If it turns out that taboo_moves only contain the
                    # taboo moves for the current round, then I have to alter this function
                    # Also if gamestate.moves contains all taboo moves (so also from this round), I can
                    # do the checking of (i) and (iv) simultaneously by just looking at gamestate.moves
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
        pass

    # Function that looks for the best move using (a variant of) minimax
    def compute_best_move(self, game_state: GameState) -> None:

        N = game_state.board.N

        for moves in game_state.taboo_moves:
            if moves in game_state.moves:
                print('yes')
            else:
                print('no')
        # if i can distinguish between taboo and regular made moves, i need to alter (iv)

        all_legal_moves = self.find_all_legal_moves(N, game_state)
        self.propose_move(random.choice(all_legal_moves))

        print('taboo moves:', game_state.taboo_moves)
        for move in all_legal_moves:
            print('Move: ({},{}) -> {}'.format(move.i+1, move.j+1, move.value))

        while True:
            time.sleep(0.2)
            self.propose_move(random.choice(all_legal_moves))
