#!/usr/bin/python

import sys
import json
import socket
import math
import copy
import random



weights = {
  "corner": 100000,
  "middle": 20,
  "edge_pieces": 20,
  "corner_adjacents": 100000,
  "number_of_chips": 10
}

def evalulate_board(player, board, current_player, turn):
  evaluation = 0

  # add corner weights
  if board[0][0] == current_player:
    evaluation += weights["corner"]
  elif board[0][7] == current_player:
    evaluation += weights["corner"]
  elif board[7][0] == current_player:
    evaluation += weights["corner"]
  elif board[7][7] == current_player:
    evaluation += weights["corner"]

  # count non-corner edges
  for i in range(1, 7):
    if board[0][i] == current_player:
      evaluation += weights["edge_pieces"]
    elif board[i][0] == current_player:
      evaluation += weights["edge_pieces"]
    elif board[i][7] == current_player:
      evaluation += weights["edge_pieces"]
    elif board[7][i] == current_player:
      evaluation += weights["edge_pieces"]

  if turn < 20:
      # check middle four pieces of the on_board
      if board[3][3] == current_player:
        evaluation += weights["middle"]
      elif board[3][4] == current_player:
        evaluation += weights["middle"]
      elif board[4][3] == current_player:
        evaluation += weights["middle"]
      elif board[4][4] == current_player:
        evaluation += weights["middle"]

  if turn > 20:
    player_num_chips = 0
    opponent_num_chips = 0
    for row in range(0, 8):
      for column in range(0, 8):
        if board[row][column] == current_player:
          player_num_chips += 1
        elif board[row][column] == get_opponent(current_player):
          opponent_num_chips += 1
    evaluation += (player_num_chips - opponent_num_chips) * weights["number_of_chips"]



  if board[0][1] == current_player:
    evaluation -= weights["corner_adjacents"]
  elif board[1][0] == current_player:
    evaluation -= weights["corner_adjacents"]
  elif board[1][1] == current_player:
    evaluation -= weights["corner_adjacents"]
  elif board[6][0] == current_player:
    evaluation -= weights["corner_adjacents"]
  elif board[1][7] == current_player:
    evaluation -= weights["corner_adjacents"]
  elif board[1][6] == current_player:
    evaluation -= weights["corner_adjacents"]
  elif board[6][1] == current_player:
    evaluation -= weights["corner_adjacents"]
  elif board[7][1] == current_player:
    evaluation -= weights["corner_adjacents"]
  elif board[6][1] == current_player:
    evaluation -= weights["corner_adjacents"]
  elif board[7][6] == current_player:
    evaluation -= weights["corner_adjacents"]
  elif board[6][7] == current_player:
    evaluation -= weights["corner_adjacents"]
  elif board[6][6] == current_player:
    evaluation -= weights["corner_adjacents"]

  #return a positive or negative
  #depending on whos turn it is in the board state
  if player == current_player:
    return evaluation
  return evaluation * -1


def get_move(player, board, turn, max_turn_time):
  result = minimax(player, board, 5, player, turn, -math.inf, math.inf)
  print('Eval Score:', result[1])
  return result[0]

# Minimax
# Returns tuple (move, score)
def minimax(player, board, depth, current_player, turn, alpha, beta):
  # Maximize our players move
  maximizing_player = player == current_player
  # Get the valid moves
  valid_moves = get_valid_moves(current_player, board)
  # Base case
  if (not valid_moves or depth == 0):
      return ([0, 0], evalulate_board(player, board, current_player, turn))

  best_move = [-1, -1]
  best_score = 0
  if maximizing_player:
    best_score = -math.inf
  else:
    best_score = math.inf


  # Recursive step
  if maximizing_player: # Me - maximize
    for move in valid_moves:
      # Make the move
      # Flip the tiles - need to optimize this
      tiles_to_flip = is_valid_move(current_player, board, move)
      for tile in tiles_to_flip:
        board[tile[0]][tile[1]] = current_player
      # Set our tile
      board[move[0]][move[1]] = current_player

      # Check the reults
      result = minimax(player, board, depth - 1, get_opponent(current_player), turn, alpha, beta)
      # Update our best score and move
      if result[1] > best_score:
        best_move = move
        best_score = result[1]

      # Reset the tiles
      for tile in tiles_to_flip:
        board[tile[0]][tile[1]] = get_opponent(current_player)
      # Set our tile
      board[move[0]][move[1]] = 0

      # Alpha
      alpha = max(alpha, result[1])
      if beta <= alpha:
          break
  else: # Opponent - minimize
    for move in valid_moves:
      # Make the move
      # Flip the tiles - need to optimize this
      tiles_to_flip = is_valid_move(current_player, board, move)
      for tile in tiles_to_flip:
        board[tile[0]][tile[1]] = current_player
      # Set our tile
      board[move[0]][move[1]] = current_player

      result = minimax(player, board, depth - 1, get_opponent(current_player), turn + 1, alpha, beta)
      if result[1] < best_score:
        best_move = move
        best_score = result[1]

      # Reset the tiles
      for tile in tiles_to_flip:
        board[tile[0]][tile[1]] = get_opponent(current_player)
      # Set our tile
      board[move[0]][move[1]] = 0

      # Beta
      beta = min(beta, result[1])
      if beta <= alpha:
          break

  # Return the best move and score that we found
  return (best_move, best_score)

def make_move(current_player, board, move):
  # Flip the tiles - need to optimize this
  for tile in is_valid_move(current_player, board, move):
    board[tile[0]][tile[1]] = current_player
  # Set our tile
  board[move[0]][move[1]] = current_player

def on_board(move):
  return move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7

def is_valid_move(current_player, board, move):
  # Check if move can be made
  if board[move[0]][move[1]] != 0:
      return []

  tiles_to_flip = []
  for x_dir, y_dir in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
    x = move[0] + x_dir
    y = move[1] + y_dir
    # While we are still on the board an opponent tiles
    while on_board([x, y]) and board[x][y] == get_opponent(current_player):
      x += x_dir
      y += y_dir
      # If our next move is me, return the tiles to flip
      if on_board([x, y]) and board[x][y] == current_player:
        # iterate back and add append to tiles_to_flip
        x -= x_dir
        y -= y_dir
        while not ([x, y] == move):
          tiles_to_flip.append([x, y])
          x -= x_dir
          y -= y_dir
        break

  return tiles_to_flip



def get_opponent(player):
  if player == 1:
    return 2
  return 1

def get_valid_moves(current_player, board):
  valid_moves = []
  for row in range(0, 8):
    for column in range(0, 8):
      if is_valid_move(current_player, board, [row, column]):
        valid_moves.append([row, column])
  random.shuffle(valid_moves)
  return valid_moves










def prepare_response(move):
  response = '{}\n'.format(move).encode()
  print('sending {!r}'.format(response))
  return response

if __name__ == "__main__":
  port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 1337
  host = sys.argv[2] if (len(sys.argv) > 2 and sys.argv[2]) else socket.gethostname()

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.connect((host, port))
    turn = 0
    while True:
      print(turn)
      data = sock.recv(1024)
      if not data:
        print('connection to server closed')
        break
      json_data = json.loads(str(data.decode('UTF-8')))
      board = json_data['board']
      max_turn_time = json_data['maxTurnTime']
      player = json_data['player']

      move = get_move(player, board, turn, max_turn_time)
      response = prepare_response(move)
      sock.sendall(response)
      turn += 2
  finally:
    sock.close()
