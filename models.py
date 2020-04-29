from config import app, db, func

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    balance = dB.Column(db.Integer)
    photo = dB.Column(db.BLOB)
    wins = dB.Column(db.Integer)
    losses = dB.Column(db.Integer)
    current_game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=True)  # is null if not currently in a game
    current_game = db.relationship("Game", foreign_keys=[game_id], backref="game_users")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Game(db.Model):
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)
    game_type_id = db.Column(db.Integer, db.ForeignKey("game_types.id"), nullable=False) 
    game_status = dB.Column(db.Integer)  # 0: waiting, 1: playing, 2: completed
    pot = dB.Column(db.Integer)
    current_turn = dB.Column(db.Integer)
    num_players = dB.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class GameType(db.Model):
    __tablename__ = "game_types"
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(255))
    time_limit = dB.Column(db.Integer)
    min_players = dB.Column(db.Integer)
    max_players = dB.Column(db.Integer)
    ante = dB.Column(db.Integer)
    max_raise = dB.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    total_bet = dB.Column(db.Integer)
    result = dB.Column(db.Integer)
    turn = dB.Column(db.Integer)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    game = db.relationship("Game", foreign_keys=[game_id], backref="game_players")
    player_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    player = db.relationship("User", foreign_keys=[user_id], backref="user_players")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    message = dB.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", foreign_keys=[user_id], backref="user_messages")
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=True)  # is null if not in a game while sending message
    game = db.relationship("Game", foreign_keys=[game_id], backref="game_messages")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Card(db.Model):
    __tablename__ = "cards"
    id = db.Column(db.Integer, primary_key=True)
    number = dB.Column(db.Integer)  # 1: ace, 2-10: 2-10, 11: jack, 12: queen, 13: king
    suit = dB.Column(db.Integer)  # 1: clubs, 2: diamonds, 3: hearts, 4: spades
    face_up = dB.Column(db.Boolean, unique=False, default=False)  # false: card is face down, true: card is face up
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    game = db.relationship("Game", foreign_keys=[game_id], backref="game_cards")
    player_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # is null if in the deck, i.e. not in any player's possession
    player = db.relationship("User", foreign_keys=[user_id], backref="user_cards")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Play(db.Model):
    __tablename__ = "plays"
    id = db.Column(db.Integer, primary_key=True)
    action = dB.Column(db.Integer) # 0: fold, 1: call/check, 2: raise [for blackjack... 3: split, 4: double]
    amount = dB.Column(db.Integer) # amount of bet if a raise or double
    card_id = db.Column(db.Integer, db.ForeignKey("cards.id"), nullable=True)
    card = db.relationship("Card", foreign_keys=[game_id], backref="card_plays")
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    game = db.relationship("Game", foreign_keys=[game_id], backref="game_plays")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
