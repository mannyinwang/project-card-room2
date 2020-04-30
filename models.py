from config import app, db, migrate, func, or_

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    balance = db.Column(db.Integer)
    photo = db.Column(db.BLOB)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    current_game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=True)  # is null if not currently in a game
    current_game = db.relationship("Game", foreign_keys=[current_game_id], backref="game_users")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Game(db.Model):
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)
    game_type_id = db.Column(db.Integer, db.ForeignKey("game_types.id"), nullable=False) 
    game_type = db.relationship("GameType", foreign_keys=[game_type_id], backref="gametype_games")
    game_status = db.Column(db.Integer)  # 0: waiting, 1: playing, 2: completed
    pot = db.Column(db.Integer)
    current_turn = db.Column(db.Integer)
    num_players = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class GameType(db.Model):
    __tablename__ = "game_types"
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(255))
    time_limit = db.Column(db.Integer)
    min_players = db.Column(db.Integer)
    max_players = db.Column(db.Integer)
    ante = db.Column(db.Integer)
    max_raise = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    total_bet = db.Column(db.Integer)
    result = db.Column(db.Integer)
    turn = db.Column(db.Integer)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    game = db.relationship("Game", foreign_keys=[game_id], backref="game_players")
    player_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    player = db.relationship("User", foreign_keys=[player_id], backref="user_players")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", foreign_keys=[user_id], backref="user_messages")
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=True)  # is null if not in a game while sending message
    game = db.relationship("Game", foreign_keys=[game_id], backref="game_messages")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Card(db.Model):
    __tablename__ = "cards"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)  # 1: ace, 2-10: 2-10, 11: jack, 12: queen, 13: king
    suit = db.Column(db.Integer)  # 1: clubs, 2: diamonds, 3: hearts, 4: spades
    face_up = db.Column(db.Boolean, unique=False, default=False)  # false: card is face down, true: card is face up
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    game = db.relationship("Game", foreign_keys=[game_id], backref="game_cards")
    player_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # is null if in the deck, i.e. not in any player's possession
    player = db.relationship("User", foreign_keys=[player_id], backref="user_cards")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Play(db.Model):
    __tablename__ = "plays"
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.Integer) # 0: fold, 1: call/check, 2: raise [for blackjack... 3: split, 4: double]
    amount = db.Column(db.Integer) # amount of bet if a raise or double
    card_id = db.Column(db.Integer, db.ForeignKey("cards.id"), nullable=True)
    card = db.relationship("Card", foreign_keys=[card_id], backref="card_plays")
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    game = db.relationship("Game", foreign_keys=[game_id], backref="game_plays")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
