import argparse
import grpc
from typing import Iterable, Optional
from concurrent import futures
import threading
import tic_tac_toe_pb2_grpc as ttt_grpc
import tic_tac_toe_pb2 as ttt

games = {}

def get_winner(moves: Iterable[ttt.Move]):
    winning_combinations = (
        (1, 2, 3), (4, 5, 6), (7, 8, 9),  # Rows
        (1, 4, 7), (2, 5, 8), (3, 6, 9),  # Cols
        (1, 5, 9), (3, 5, 7),             # Diagonals
    )

    x_moves = []
    o_moves = []

    for move in moves:
        if move.mark == ttt.MARK_CROSS:
            x_moves.append(move.cell)
        elif move.mark == ttt.MARK_NOUGHT:
            o_moves.append(move.cell)

    for combination in winning_combinations:
        if all((cell in x_moves) for cell in combination):
            return ttt.MARK_CROSS
        if all((cell in o_moves) for cell in combination):
            return ttt.MARK_NOUGHT

    return None


class TicTacToeServicer(ttt_grpc.TicTacToeServicer):
    """
    Implements the gRPC service for Tic Tac Toe game.
    """

    def __init__(self):
        self._lock = threading.Lock()

    def CreateGame(self, request: ttt.CreateGameRequest, context):
        """
        Creates a new Tic Tac Toe game.

        Args:
            request (ttt.CreateGameRequest): The request object containing game creation parameters.
            context: The gRPC context object.

        Returns:
            ttt.Game: The created game object.
        """
        with self._lock:
            game = ttt.Game(id=len(games) + 1, is_finished=False)
            games[game.id] = game
            print(f"Created game()")
            return game

    def GetGame(self, request: ttt.GetGameRequest, context):
        """
        Retrieves a Tic Tac Toe game.

        Args:
            request (ttt.GetGameRequest): The request object containing the game ID.
            context: The gRPC context object.

        Returns:
            ttt.Game: The retrieved game object.
        """
        with self._lock:
            game = games.get(request.game_id)

            if game is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Game not found.")
                return game

            print(f"Get game(game_id={request.game_id})")
            return game

    def MakeMove(self, request: ttt.MakeMoveRequest, context):
        """
        Makes a move in a Tic Tac Toe game.

        Args:
            request (ttt.MakeMoveRequest): The request object containing the move details.
            context: The gRPC context object.

        Returns:
            ttt.Game: The updated game object after the move.
        """
        with self._lock:
            game = games.get(request.game_id)

            if game is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Game not found.")
                return game

            if 1 > request.move.cell > 9:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Move out of range.")
                return game

            if game.is_finished:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("Game is already finished.")
                return game

            if game.turn != request.move.mark:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(f"It's not your turn.")
                return game

            if request.move in game.moves:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(f"Cell already occupied.")
                return game

            if request.move.mark == ttt.MARK_CROSS:
                print(f"Make move(game_id={request.game_id}, move=Move(mark=X, cell={request.move.cell}))")
            else:
                print(f"Make move(game_id={request.game_id}, move=Move(mark=O, cell={request.move.cell}))")

            game.moves.append(request.move)

            if game.turn == 0:
                game.turn = 1
            else:
                game.turn = 0

            if get_winner(game.moves) != None:
                game.is_finished = True
                game.winner = get_winner(game.moves)

            if len(game.moves) == 9:
                game.is_finished = True

            games[request.game_id] = game

            return game


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="Port of the Tic-Tac-Toe server.", type=int)
    port = parser.parse_args().port

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    ttt_grpc.add_TicTacToeServicer_to_server(TicTacToeServicer(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")

    try:
        print(f"Server listening on 0.0.0.0:{port}...")
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":

    try:
        main()
    except grpc.RpcError as e:
        print(f"gRPC error (code={e.code()}): {e.details()}")
    except KeyboardInterrupt:
        print("Exiting...")
