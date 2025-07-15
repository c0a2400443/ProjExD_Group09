import pygame
import sys
from enum import Enum

# 初期化
pygame.init()

# 定数
BOARD_SIZE = 8
SQUARE_SIZE = 80
WINDOW_WIDTH = BOARD_SIZE * SQUARE_SIZE
WINDOW_HEIGHT = BOARD_SIZE * SQUARE_SIZE + 100  # 情報表示用のスペース
FPS = 60

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT_COLOR = (255, 255, 0, 128)
SELECTED_COLOR = (0, 255, 0, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class PieceType(Enum):
    PAWN = 1
    ROOK = 2
    KNIGHT = 3
    BISHOP = 4
    QUEEN = 5
    KING = 6

class PieceColor(Enum):
    WHITE = 1
    BLACK = 2

class Piece:
    def __init__(self, piece_type, color, row, col):
        self.type = piece_type
        self.color = color
        self.row = row
        self.col = col
        self.has_moved = False
        
    def get_possible_moves(self, board):
        """駒の可能な動きを取得"""
        moves = []
        if self.type == PieceType.BISHOP:
            # 斜め4方向をチェック（左上, 右上, 左下, 右下）
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                r, c = self.row + dr, self.col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    target = board.get_piece(r, c)
                    if target is None:
                        moves.append((r, c))  # 空きマス
                    elif target.color != self.color:
                        moves.append((r, c))  # 敵の駒を取る
                        break  # 敵の駒の先には進めない
                    else:
                        break  # 味方の駒で止まる
                    r += dr
                    c += dc
        elif self.type == PieceType.PAWN:
            direction = -1 if self.color == PieceColor.WHITE else 1
            start_row = 6 if self.color == PieceColor.WHITE else 1

            if board.get_piece(self.row + direction, self.col) is None:
                moves.append((self.row + direction, self.col))

                if self.row == start_row and board.get_piece(self.row + 2 * direction, self.col) is None:
                    moves.append((self.row + 2 * direction, self.col))

            for dx in [-1, 1]:
                new_row = self.row + direction
                new_col = self.col + dx
                if 0 <= new_col < 8 and 0 <= new_row < 8:
                    target = board.get_piece(new_row, new_col)
                    if target and target.color != self.color:
                        moves.append((new_row, new_col))

            if board.en_passant_target:
                target_row, target_col = board.en_passant_target
                if abs(target_col - self.col) == 1 and target_row == self.row + direction:
                    moves.append((target_row, target_col))

        elif self.type == PieceType.KING:
            directions_k = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0),  (1, 1)]
            for dr, dc in directions_k:
                new_row = self.row + dr
                new_col = self.col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target_piece = board.get_piece(new_row, new_col)
                    if not target_piece or target_piece.color != self.color:
                        moves.append((new_row, new_col))
            if not self.has_moved:
                row = self.row
                # キングサイド（右）
                rook = board.get_piece(row, 7)
                if rook and rook.type == PieceType.ROOK and not rook.has_moved:
                    if board.get_piece(row, 5) is None and board.get_piece(row, 6) is None:
                        moves.append((row, 6))  # キャスリング先（キング）

                # クイーンサイド（左）
                rook = board.get_piece(row, 0)
                if rook and rook.type == PieceType.ROOK and not rook.has_moved:
                    if (board.get_piece(row, 1) is None and
                        board.get_piece(row, 2) is None and
                        board.get_piece(row, 3) is None):
                        moves.append((row, 2))  # キャスリング先（キング）



        elif self.type == PieceType.KNIGHT:
            # ナイトの動き：8方向へのL字移動
            knight_moves = [
                (-2, -1), (-2, +1),
                (-1, -2), (-1, +2),
                (+1, -2), (+1, +2),
                (+2, -1), (+2, +1)
            ]
            for dr, dc in knight_moves:
                new_row = self.row + dr
                new_col = self.col + dc
                if board.is_valid_move(self.row, self.col, new_row, new_col):
                    moves.append((new_row, new_col))

        elif self.type == PieceType.ROOK:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                r, c = self.row + dr, self.col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    target_piece = board.get_piece(r, c)
                    if target_piece is None:
                        moves.append((r, c))
                    elif target_piece.color != self.color:
                        moves.append((r, c))
                        break
                    else:
                        break
                    r += dr
                    c += dc
        elif self.type == PieceType.QUEEN:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                        (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                r, c = self.row + dr, self.col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    target_piece = board.get_piece(r, c)
                    if target_piece is None:
                        moves.append((r, c))
                    elif target_piece.color != self.color:
                        moves.append((r, c))
                        break
                    else:
                        break
                    r += dr
                    c += dc
        # else:
        #     # 暫定的に全マス移動可能（is_valid_moveで敵味方チェックあり）
        #     for row in range(8):
        #         for col in range(8):
        #             if board.is_valid_move(self.row, self.col, row, col):
        #                 moves.append((row, col))
        #     return moves

        # for dr, dc in directions:
        #     r, c = self.row + dr, self.col + dc
        #     while 0 <= r < 8 and 0 <= c < 8:
        #         target_piece = board.get_piece(r, c)
        #         if target_piece is None:
        #             moves.append((r, c))
        #         elif target_piece.color != self.color:
        #             moves.append((r, c))
        #             break
        #         else:
        #             break
        #         r += dr
        #         c += dc

        return moves

    
    def move(self, new_row, new_col):
        """駒を移動"""
        self.row = new_row
        self.col = new_col
        self.has_moved = True
    
    def __str__(self):
        symbols = {
            PieceType.PAWN: "P",
            PieceType.ROOK: "R",
            PieceType.KNIGHT: "N",
            PieceType.BISHOP: "B",
            PieceType.QUEEN: "Q",
            PieceType.KING: "K"
        }
        return symbols[self.type]
    
    def get_display_color(self):
        """駒の表示色を取得"""
        return BLACK if self.color == PieceColor.BLACK else WHITE

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = PieceColor.WHITE
        self.selected_piece = None
        self.selected_pos = None
        self.winner = None
        self.possible_moves = []
        
        self.en_passant_target = None
        self.promotion_pending = False
        self.promotion_piece = None

        self.setup_initial_position()
    
    def setup_initial_position(self):
        """初期配置を設定"""
        # 黒の駒
        piece_order = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
                      PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
        
        for col in range(8):
            # 黒の駒
            self.board[0][col] = Piece(piece_order[col], PieceColor.BLACK, 0, col)
            self.board[1][col] = Piece(PieceType.PAWN, PieceColor.BLACK, 1, col)
            
            # 白の駒
            self.board[7][col] = Piece(piece_order[col], PieceColor.WHITE, 7, col)
            self.board[6][col] = Piece(PieceType.PAWN, PieceColor.WHITE, 6, col)
    
    def get_piece(self, row, col):
        """指定位置の駒を取得"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def set_piece(self, row, col, piece):
        """指定位置に駒を配置"""
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece
    
    def is_valid_move(self, from_row, from_col, to_row, to_col):
        """移動が有効かチェック（基本的な範囲チェック）"""
        if not (0 <= to_row < 8 and 0 <= to_col < 8):
            return False
        
        piece = self.get_piece(from_row, from_col)
        if not piece:
            return False
        
        target_piece = self.get_piece(to_row, to_col)
        if target_piece and target_piece.color == piece.color:
            return False
        
        return True
    
    def make_move(self, from_row, from_col, to_row, to_col):
        piece = self.get_piece(from_row, from_col)
        if not piece or piece.color != self.current_turn:
            return False

        is_en_passant = False
        if piece.type == PieceType.PAWN and self.en_passant_target == (to_row, to_col):
            is_en_passant = True

        if not self.is_valid_move(from_row, from_col, to_row, to_col):
            return False

        #target_pieceを定義
        target_piece = self.get_piece(to_row, to_col)
        
        # キングが取られたら勝敗を設定
        if target_piece and target_piece.type == PieceType.KING:
            self.set_piece(to_row, to_col, piece)
            self.set_piece(from_row, from_col, None)
            piece.move(to_row, to_col)
            self.winner = piece.color  # 勝った側の色
            return True
        

        if is_en_passant:
            self.set_piece(from_row, to_col, None)

        self.set_piece(to_row, to_col, piece)
        self.set_piece(from_row, from_col, None)
        piece.move(to_row, to_col)

        if piece.type == PieceType.PAWN and abs(to_row - from_row) == 2:
            intermediate_row = (from_row + to_row) // 2
            self.en_passant_target = (intermediate_row, from_col)
        else:
            self.en_passant_target = None
        
        # キャスリング時のルーク移動
        if piece.type == PieceType.KING and abs(to_col - from_col) == 2:
            row = from_row
            if to_col == 6:
                # キングサイド
                rook = self.get_piece(row, 7)
                self.set_piece(row, 5, rook)
                self.set_piece(row, 7, None)
                rook.move(row, 5)
            elif to_col == 2:
                # クイーンサイド
                rook = self.get_piece(row, 0)
                self.set_piece(row, 3, rook)
                self.set_piece(row, 0, None)
                rook.move(row, 3)

        # 昇格判定 → 昇格待ちにしてターンは切り替えない
        if piece.type == PieceType.PAWN and ((piece.color == PieceColor.WHITE and to_row == 0) or (piece.color == PieceColor.BLACK and to_row == 7)):
            self.promotion_pending = True
            self.promotion_piece = piece
            # ターン切り替えは昇格完了後に行うため保留
            return True

        # 通常のターン切り替え
        self.current_turn = PieceColor.BLACK if self.current_turn == PieceColor.WHITE else PieceColor.WHITE
        return True
    
    def select_piece(self, row, col):
        """駒を選択"""
        piece = self.get_piece(row, col)
        if piece and piece.color == self.current_turn:
            self.selected_piece = piece
            self.selected_pos = (row, col)
            self.possible_moves = piece.get_possible_moves(self)
            return True
        return False
    
    def deselect_piece(self):
        """駒の選択を解除"""
        self.selected_piece = None
        self.selected_pos = None
        self.possible_moves = []

class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("チェスゲーム")
        self.clock = pygame.time.Clock()
        self.board = ChessBoard()
        # フォントの設定（日本語対応）
        try:
            self.font = pygame.font.Font("msgothic.ttc", 24)  # Windows
        except:
            try:
                self.font = pygame.font.Font("NotoSansCJK-Regular.ttc", 24)  # Linux
            except:
                self.font = pygame.font.Font(None, 24)  # フォールバック
        
        self.piece_font = pygame.font.Font(None, 60)
        self.promotion_choices = [
            PieceType.QUEEN,
            PieceType.ROOK,
            PieceType.BISHOP,
            PieceType.KNIGHT
        ]
        
    def get_board_pos(self, mouse_pos):
        """マウス位置をボード座標に変換"""
        x, y = mouse_pos
        if 0 <= x < WINDOW_WIDTH and 0 <= y < BOARD_SIZE * SQUARE_SIZE:
            col = x // SQUARE_SIZE
            row = y // SQUARE_SIZE
            return row, col
        return None, None
    
    def draw_board(self):
        """チェスボードを描画"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                
                # 選択中のマスをハイライト
                if self.board.selected_pos == (row, col):
                    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    highlight_surface.fill(SELECTED_COLOR)
                    self.screen.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                
                # 可能な移動先をハイライト
                if (row, col) in self.board.possible_moves:
                    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    highlight_surface.fill(HIGHLIGHT_COLOR)
                    self.screen.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
    
    def draw_pieces(self):
        """駒を描画"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece(row, col)
                if piece:
                    # 駒のテキストを描画
                    text_color = piece.get_display_color()
                    # 背景色を設定（見やすくするため）
                    bg_color = WHITE if text_color == BLACK else BLACK
                    
                    text = self.piece_font.render(str(piece), True, text_color)
                    text_rect = text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                    row * SQUARE_SIZE + SQUARE_SIZE // 2))
                    
                    # 背景の円を描画
                    pygame.draw.circle(self.screen, bg_color, text_rect.center, 25)
                    pygame.draw.circle(self.screen, text_color, text_rect.center, 25, 2)
                    
                    self.screen.blit(text, text_rect)
    
    def draw_info(self):
        info_y = BOARD_SIZE * SQUARE_SIZE + 10

        if self.board.winner != None:
            winner_color = "Black" if self.board.winner == PieceColor.WHITE else "White"
            result_text = f"{winner_color} wins!"
            text = self.font.render(result_text, True, RED)
            self.screen.blit(text, (10, info_y))
            return  # 勝敗が決まったら他の表示は不要
        if self.board.promotion_pending:
            # 昇格UI描画
            text = self.font.render("Promotion: Select a piece", True, BLACK)
            self.screen.blit(text, (10, info_y))

            # 駒候補を横に並べて表示
            for i, p_type in enumerate(self.promotion_choices):
                symbol = {
                    PieceType.QUEEN: "Q",
                    PieceType.ROOK: "R",
                    PieceType.BISHOP: "B",
                    PieceType.KNIGHT: "N"
                }[p_type]

                x = 10 + i * 60
                y = info_y + 30

                rect = pygame.Rect(x, y, 50, 50)
                pygame.draw.rect(self.screen, LIGHT_BROWN, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 2)

                text = self.piece_font.render(symbol, True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)

            return  # 昇格中は他の情報は描画しない

        # 通常のターン情報表示は元のコードのまま
        turn_text = f"Current Turn: {'Black' if self.board.current_turn == PieceColor.WHITE else 'White'}"
        text = self.font.render(turn_text, True, BLACK)
        self.screen.blit(text, (10, info_y))
        
        if self.board.selected_piece:
            piece = self.board.selected_piece
            color_name = "White" if piece.color == PieceColor.WHITE else "Black"
            selected_text = f"Selected: {color_name} {str(piece)} at ({piece.row}, {piece.col})"
            text = self.font.render(selected_text, True, BLACK)
            self.screen.blit(text, (10, info_y + 30))
        
    def handle_click(self, mouse_pos):
        """マウスクリックを処理"""
        if self.board.promotion_pending:
            info_y = BOARD_SIZE * SQUARE_SIZE + 40
            x_start = 10
            box_size = 50
            for i, p_type in enumerate(self.promotion_choices):
                rect = pygame.Rect(x_start + i * 60, info_y, box_size, box_size)
                if rect.collidepoint(mouse_pos):
                    # ユーザーが選択した駒に昇格
                    self.board.promotion_piece.type = p_type
                    self.board.promotion_pending = False
                    self.board.promotion_piece = None
                    # 昇格が終わったのでターン切り替え
                    self.board.current_turn = PieceColor.BLACK if self.board.current_turn == PieceColor.WHITE else PieceColor.WHITE
                    self.board.deselect_piece()
                    print(f"Promotion selected: {p_type}")
                    return
            return  # 昇格中はそれ以外のクリックは無視

        # 以下、既存の選択処理
        if self.board.winner:
            return # 勝敗が決まったらクリック操作無効
        
        row, col = self.get_board_pos(mouse_pos)
        if row is not None and col is not None:
            if self.board.selected_piece:
                if (row, col) in self.board.possible_moves:
                    from_row, from_col = self.board.selected_pos
                    if self.board.make_move(from_row, from_col, row, col):
                        print(f"Move made: {from_row},{from_col} -> {row},{col}")
                        print(f"Turn changed to: {self.board.current_turn}")
                        self.board.deselect_piece()
                    else:
                        print("Move failed")
                elif self.board.select_piece(row, col):
                    print(f"Selected piece: {self.board.selected_piece} at ({row}, {col})")
                else:
                    self.board.deselect_piece()
                    print("Deselected piece")
            else:
                if self.board.select_piece(row, col):
                    print(f"Selected piece: {self.board.selected_piece} at ({row}, {col})")
                else:
                    print(f"Cannot select piece at ({row}, {col})")
    
    def run(self):
        """メインゲームループ"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                # 勝敗が決まっていなければクリック処理する
                    if event.button == 1 and not self.board.winner:
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    # ゲーム終了時にRキーでリセット
                    if self.board.winner and event.key == pygame.K_r:
                        self.board = ChessBoard()  # 新しいボードに入れ替え（リセット）
                        print("Game restarted")
            
            # 描画
            self.screen.fill(WHITE)
            self.draw_board()
            self.draw_pieces()
            self.draw_info()

            # 勝敗決定後にリスタートの案内表示
            if self.board.winner:
                restart_text = self.font.render("Press R to restart", True, BLUE)
                self.screen.blit(restart_text, (10, WINDOW_HEIGHT - 40))
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# メイン実行
if __name__ == "__main__":
    game = ChessGame()
    game.run()


