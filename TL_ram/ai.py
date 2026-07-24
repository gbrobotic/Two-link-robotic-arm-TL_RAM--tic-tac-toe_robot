# ============================================================
# ai.py
# 5x5 Tic-Tac-Toe AI
# Ported from ESP32 version
# ============================================================

EMPTY = ' '

# Human = Red Piece
HUMAN = 'X'

# Robot = Blue Piece
ROBOT = 'O'


def Winner(board):

    # Horizontal
    for i in range(5):
        for j in range(2):
            p = board[i][j]
            if p != EMPTY and \
               p == board[i][j+1] and \
               p == board[i][j+2] and \
               p == board[i][j+3]:
                return p

    # Vertical
    for i in range(2):
        for j in range(5):
            p = board[i][j]
            if p != EMPTY and \
               p == board[i+1][j] and \
               p == board[i+2][j] and \
               p == board[i+3][j]:
                return p

    # Diagonal \
    for i in range(2):
        for j in range(2):
            p = board[i][j]
            if p != EMPTY and \
               p == board[i+1][j+1] and \
               p == board[i+2][j+2] and \
               p == board[i+3][j+3]:
                return p

    # Diagonal /
    for i in range(2):
        for j in range(3,5):
            p = board[i][j]
            if p != EMPTY and \
               p == board[i+1][j-1] and \
               p == board[i+2][j-2] and \
               p == board[i+3][j-3]:
                return p

    return EMPTY
def evaluate(board):

    winner = Winner(board)

    if winner == ROBOT:
        return 10000

    if winner == HUMAN:
        return -10000

    score = 0

    # ---- Horizontal ----
    for i in range(5):
        for j in range(2):

            robot = 0
            human = 0

            for k in range(4):

                if board[i][j+k] == ROBOT:
                    robot += 1

                elif board[i][j+k] == HUMAN:
                    human += 1

            if robot > 0 and human > 0:
                continue

            if robot == 3:
                score += 100
            elif robot == 2:
                score += 10

            if human == 3:
                score -= 100
            elif human == 2:
                score -= 10

    # ---- Vertical ----
    for i in range(2):
        for j in range(5):

            robot = 0
            human = 0

            for k in range(4):

                if board[i+k][j] == ROBOT:
                    robot += 1

                elif board[i+k][j] == HUMAN:
                    human += 1

            if robot > 0 and human > 0:
                continue

            if robot == 3:
                score += 100
            elif robot == 2:
                score += 10

            if human == 3:
                score -= 100
            elif human == 2:
                score -= 10

    # ---- Diagonal \ ----
    for i in range(2):
        for j in range(2):

            robot = 0
            human = 0

            for k in range(4):

                if board[i+k][j+k] == ROBOT:
                    robot += 1

                elif board[i+k][j+k] == HUMAN:
                    human += 1

            if robot > 0 and human > 0:
                continue

            if robot == 3:
                score += 100
            elif robot == 2:
                score += 10

            if human == 3:
                score -= 100
            elif human == 2:
                score -= 10

    # ---- Diagonal / ----
    for i in range(2):
        for j in range(3,5):

            robot = 0
            human = 0

            for k in range(4):

                if board[i+k][j-k] == ROBOT:
                    robot += 1

                elif board[i+k][j-k] == HUMAN:
                    human += 1

            if robot > 0 and human > 0:
                continue

            if robot == 3:
                score += 100
            elif robot == 2:
                score += 10

            if human == 3:
                score -= 100
            elif human == 2:
                score -= 10

    # Center preference
    if board[2][2] == ROBOT:
        score += 50

    elif board[2][2] == HUMAN:
        score -= 50

    return score
# ============================================================
# Utility Functions
# ============================================================

def isValidPos(row, col):
    return 0 <= row < 5 and 0 <= col < 5
def countThreats(board, player):

    threats = 0

    # Horizontal
    for i in range(5):
        for j in range(2):

            cnt = 0
            emp = 0

            for k in range(4):

                if board[i][j+k] == player:
                    cnt += 1
                elif board[i][j+k] == EMPTY:
                    emp += 1

            if cnt == 3 and emp == 1:
                threats += 1

    # Vertical
    for i in range(2):
        for j in range(5):

            cnt = 0
            emp = 0

            for k in range(4):

                if board[i+k][j] == player:
                    cnt += 1
                elif board[i+k][j] == EMPTY:
                    emp += 1

            if cnt == 3 and emp == 1:
                threats += 1

    # Diagonal \
    for i in range(2):
        for j in range(2):

            cnt = 0
            emp = 0

            for k in range(4):

                if board[i+k][j+k] == player:
                    cnt += 1
                elif board[i+k][j+k] == EMPTY:
                    emp += 1

            if cnt == 3 and emp == 1:
                threats += 1

    # Diagonal /
    for i in range(2):
        for j in range(3,5):

            cnt = 0
            emp = 0

            for k in range(4):

                if board[i+k][j-k] == player:
                    cnt += 1
                elif board[i+k][j-k] == EMPTY:
                    emp += 1

            if cnt == 3 and emp == 1:
                threats += 1

    return threats
def findWinningMove(board, player):

    for i in range(5):
        for j in range(5):

            if board[i][j] == EMPTY:

                board[i][j] = player

                if Winner(board) == player:

                    board[i][j] = EMPTY
                    return (i, j)

                board[i][j] = EMPTY

    return None
def findForkMove(board, player):

    for i in range(5):
        for j in range(5):

            if board[i][j] == EMPTY:

                board[i][j] = player

                if countThreats(board, player) >= 2:

                    board[i][j] = EMPTY
                    return (i, j)

                board[i][j] = EMPTY

    return None
# ============================================================
# Candidate Move Generation
# ============================================================

def getCandidates(board):

    candidates = []

    hasPlayed = False

    visited = [[False for _ in range(5)] for _ in range(5)]

    for i in range(5):
        for j in range(5):

            if board[i][j] != EMPTY:

                hasPlayed = True

                for di in range(-1, 2):
                    for dj in range(-1, 2):

                        ni = i + di
                        nj = j + dj

                        if (
                            isValidPos(ni, nj)
                            and board[ni][nj] == EMPTY
                            and not visited[ni][nj]
                        ):

                            visited[ni][nj] = True
                            candidates.append((ni, nj))

    if not hasPlayed:
        candidates.append((2, 2))

    return candidates
def minimax(board, depth, isMax, alpha, beta):

    winner = Winner(board)

    if winner == ROBOT:
        return 10000 + depth

    if winner == HUMAN:
        return -10000 - depth

    # Draw
    hasEmpty = False

    for row in board:
        if EMPTY in row:
            hasEmpty = True
            break

    if not hasEmpty:
        return 0

    if depth == 0:
        return evaluate(board)

    candidates = getCandidates(board)

    if len(candidates) == 0:
        return 0

    if isMax:

        best = -20000

        for i, j in candidates:

            board[i][j] = ROBOT

            score = minimax(
                board,
                depth - 1,
                False,
                alpha,
                beta
            )

            board[i][j] = EMPTY

            best = max(best, score)
            alpha = max(alpha, score)

            if beta <= alpha:
                break

        return best

    else:

        best = 20000

        for i, j in candidates:

            board[i][j] = HUMAN

            score = minimax(
                board,
                depth - 1,
                True,
                alpha,
                beta
            )

            board[i][j] = EMPTY

            best = min(best, score)
            beta = min(beta, score)

            if beta <= alpha:
                break

        return best
# ============================================================
# Find Best Move
# ============================================================

def FindBestMove(board):

    # 1. Winning Move
    move = findWinningMove(board, ROBOT)
    if move is not None:
        return move

    # 2. Block Human Win
    move = findWinningMove(board, HUMAN)
    if move is not None:
        return move

    # 3. Take Center
    if board[2][2] == EMPTY:
        return (2, 2)

    # 4. Create Fork
    move = findForkMove(board, ROBOT)
    if move is not None:
        return move

    # 5. Block Human Fork
    move = findForkMove(board, HUMAN)
    if move is not None:
        return move

    # 6. Minimax
    candidates = getCandidates(board)

    bestScore = -20000
    bestMove = None

    depth = 3

    for i, j in candidates:

        board[i][j] = ROBOT

        score = minimax(
            board,
            depth,
            False,
            -20000,
            20000
        )

        board[i][j] = EMPTY

        if score > bestScore:

            bestScore = score
            bestMove = (i, j)

    # Fallback
    if bestMove is None:

        for i in range(5):
            for j in range(5):

                if board[i][j] == EMPTY:
                    return (i, j)

    return bestMove