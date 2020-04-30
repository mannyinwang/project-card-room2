from flask import flash
from config import bcrypt, re, EMAIL_REGEX, PWD_REGEX, socketio, app, db, migrate, func, or_
from flask_socketio import SocketIO
from random import seed, randint, shuffle
from models import User, Game, Player, Message, Card, GameType, Play

starting_balance = 10000

def addUser(user_name, email, password, confirm):
    user_added = False
    if len(user_name) == 0:
        flash("Please enter user name.")
    elif not EMAIL_REGEX.match(email):    # test whether a field matches the pattern
        flash("Invalid email address.")
    elif not re.search(PWD_REGEX, password): 
        flash("Password must be 6-20 characters and contain one or more of each of: a number, uppercase letter, lower case letter, and special symbol.")
    elif password != confirm:
        flash("Password confirmation does not match.")
    else: 
        # check if email address already exists
        result = User.query.filter_by(email=email).first()
        if result:
            flash("Account already exists.")
        else:
            # add new member
            new_user = User(user_name=user_name, email=email, password=bcrypt.generate_password_hash(password), balance=starting_balance, wins=0, losses=0, current_game_id=None)
            db.session.add(new_user)
            db.session.commit()
            flash("New user added.")
            user_added = True
    return user_added

def loginUser(email, password):
    user_id = False
    user = User.query.filter_by(email=email).first()
    if user:
        if bcrypt.check_password_hash(user.password, password):
            user_id = user.id
        else:
            flash("Login failed.")
    else:
        flash("Unknown user.")
    return user_id

def getUser(user_id):
    user = User.query.get(user_id)
    return user

def getActiveGames():
    # get game info for all active games, i.e. with game_status == 0 or 1
    # game_status: 0 if waiting, 1 if playing, 2 if completed
    # returns game info (game_id, game_status, pot, game_name, time_limit, min_players, max_players, ante, max_raise) in the form of an array of dictionaries
    active_games = Game.query.filter_by(game_status = 0).all() # | (game_status = 1)).all()
    return active_games  # return game info

def getGameTypes():
    # get info for available game types 
    # returns game type info (game_name, time_limit, min_players, max_players, ante, max_raise) in the form of an array of dictionaries
    game_types = GameType.query.all()
    return game_types  # return game types

def getGameIDFromUserID(user_id):
    game_id = Player.query.filter_by(player_id=user_id).first().game_id
    return game_id

def getGame(game_id):
    # get game info for game_id
    # returns game info (game_id, game_status, pot, game_name, time_limit, min_players, max_players, ante, max_raise) in the form a dictionary
    game = Game.query.get(game_id)
    return game

def getPlayers(game_id):
    players = Player.query.filter_by(game_id=game_id)
    return players

def getCards(game_id, player_id):
    cards = Card.query.filter_by(game_id=game_id, player_id=player_id)
    return cards

def getMessages(game_id, user_id):
    messages = Message.query.filter_by(game_id=game_id, user_id=user_id)
    return messages

def getPlayersWithCardsAndMessages(game_id):
    players = getPlayers(game_id)
    for player in players:
        player['cards'] = getCards(game_id, player['id'])
        messages = getMessages(game_id, player['id'])
        if messages:
            player['message'] = messages[0]
        else:
            player['message'] = False
    return players

def DUMMYgetGame(game_id):
    game = {}
    game['game_id'] = 1
    game['game_status'] = 1
    game['pot'] = 200
    game['game_name'] = '5-Card Stud'
    game['time_limit'] = 30
    game['current_turn'] = 0
    game['num_players'] = 4
    game['min_players'] = 4
    game['max_players'] = 4
    game['ante'] = 10
    game['max_raise'] = 50
    players = [{},{},{}]
    players[0] = {}
    players[0]['user_id'] = 1
    players[0]['user_name'] = "Mary"
    players[0]['balance'] = 7000
    players[0]['photo'] = False
    players[0]['message'] = 'Hi All!'
    players[0]['cards'] = [{},{},{},{},{}]
    players[0]['cards'][0] = {'number': 5, 'suit': 1, 'face_up': 1}
    players[0]['cards'][1] = {'number': 10, 'suit': 1, 'face_up': 1}
    players[0]['cards'][2] = {'number': 1, 'suit': 2, 'face_up': 0}
    players[0]['cards'][3] = {'number': 7, 'suit': 3, 'face_up': 0}
    players[0]['cards'][4] = {'number': 11, 'suit': 4, 'face_up': 0}
    players[1] = {}
    players[1]['user_id'] = 2
    players[1]['user_name'] = "Joe"
    players[1]['balance'] = 5000
    players[1]['photo'] = False
    players[1]['message'] = 'Hi!'
    players[1]['cards'] = [{},{},{},{}]
    players[1]['cards'][0] = {'number': 11, 'suit': 1, 'face_up': 1}
    players[1]['cards'][1] = {'number': 12, 'suit': 2, 'face_up': 1}
    players[1]['cards'][2] = {'number': 1, 'suit': 1, 'face_up': 1}
    players[1]['cards'][3] = {'number': 6, 'suit': 4, 'face_up': 0}
    players[2] = {}
    players[2]['user_id'] = 3
    players[2]['user_name'] = "Elizabeth"
    players[2]['balance'] = 3000
    players[2]['photo'] = False
    players[2]['message'] = "Hey losers!"
    players[2]['cards'] = [{},{},{},{},{}]
    players[2]['cards'][0] = {'number': 3, 'suit': 1, 'face_up': 1}
    players[2]['cards'][1] = {'number': 5, 'suit': 2, 'face_up': 1}
    players[2]['cards'][2] = {'number': 1, 'suit': 2, 'face_up': 0}
    players[2]['cards'][3] = {'number': 1, 'suit': 3, 'face_up': 0}
    players[2]['cards'][4] = {'number': 1, 'suit': 4, 'face_up': 0}
    return game, players

def createNewGame(game_type_id):
    new_game = Game(game_type_id=game_type_id, game_status=0, pot=0, current_turn=0, num_players=0)
    db.session.add(new_game)
    db.session.commit()
    return new_game.id

def getNumPlayers(game_id):
    num_players = Game.query.get(game_id).num_players
    return num_players

def addToNumPlayers(game_id, adder):
    num_players = getNumPlayers(game_id)
    Game.query.get(game_id).num_players = num_players + adder
    db.session.commit()
    return num_players + adder

def addPlayerToGame(user, game_id):
    # add user to players for game_id
    new_player = Player(result=0, total_bet=0, turn=0, game_id=game_id, player_id = user.id)
    db.session.add(new_player)
    db.session.commit()
    num_players = addToNumPlayers(game_id, 1)
    # update users.current_game_id to game_id
    user.current_game_id = game_id
    db.session.commit()
    return num_players

def startGame(game_id):
    # change games.game_status to 1 and set starting current_turn
    game = getGame(game_id)
    game.game_status = 1 # 0 = waiting, 1 = playing, 2 = completed
    game.current_turn = 1
    db.session.commit()
    # ante up players and set players' turns (i.e. positions at table)
    players = getPlayers(game_id)
    num_players = getNumPlayers(game_id)
    turns = list(range(1,num_players+1))
    shuffle(turns)
    i = 0
    for player in players:
        user = User.query.get(player.player_id)
        makeBet(user, game, game.game_type.ante)
        player.turn = turns[i]
        i += 1
    db.session.commit()
    # create card deck
    for number in range(1,14): # 13 numbers, 1 = Ace, 11 = Jack, 12 = Queen, 13 = King
        for suit in range(1,5):  # 4 suits: 1 = Spades, 2 = Hearts, 3 = Diamonds, 4 = Clubs
            new_card = Card(number=number, suit=suit, face_up=0, game_id=game_id)
            db.session.add(new_card)
    db.session.commit()
    return True

def getCardsInDeck(game_id):
    cards = Game.query.get(game_id).game_cards
    return cards

def dealCard(game_id, user_id, face_up):
    # randomly pick card from remaining undealt cards in deck
    cards = getCardsInDeck(game_id)
    card_id = cards[randint(0, len(cards)-1)]['card_id']
    # deal card to user
    card = Card.query.get(card_id)
    card.player_id = user_id
    card.face_up = face_up
    db.session.commit()
    return

def makeBet(user, game, amount):
    # deduct amount from user's balance
    user.balance = user.balance - amount
    # add amount to game's pot
    game.pot = game.pot + amount
    # add amount to players' total_bet
    player = Player.query.filter_by(game_id=game.id, player_id=user.id).first()
    player.total_bet = player.total_bet + amount
    db.session.commit()
    return

def getTopWinLossRecords(num_of_players):
    return False

def getTopBettors(num_of_players):
    return False

def gameFold(user, game_id):
    return False

def gameLeave(user, game_id):
    # remember to change users.current_game_id
    return False

def gameCall(user, game_id):
    return False

def gameRaise(user, game_id, raise_amount):
    return False

def gameMessage(user, game_id, message):
    return False
