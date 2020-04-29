from flask import flash
from config import bcrypt, re, EMAIL_REGEX, PWD_REGEX, socketio, app, db, func
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
        email = User.query.get(email)
        if email:
            flash("Account already exists.")
        else:
            # add new member
            mySQL = connectToMySQL(mySQLdb)
            query = "INSERT INTO users (user_name, email, password, balance, wins, losses, current_game_id, created_at, updated_at) VALUES (%(un)s, %(em)s, %(pwd)s, %(b)s, %(w)s, %(l)s, NULL, NOW(), NOW());"
            data = {
                'un': user_name,
                'em': email,
                'pwd': bcrypt.generate_password_hash(password),
                'b': starting_balance,
                'w': 0, # zero wins
                'l': 0  # zero losses
            }
            mySQL.query_db(query, data)
            flash("New user added.")
            user_added = True
    return user_added

def loginUser(email, password):
    user_id = False
    mySQL = connectToMySQL(mySQLdb)
    query = "SELECT id, password FROM users WHERE email = %(em)s;"
    data = {
        'em': email
    }
    result = mySQL.query_db(query, data)
    if result:
        if bcrypt.check_password_hash(result[0]['password'], password):
            user_id = result[0]['id']
        else:
            flash("Login failed.")
    else:
        flash("Unknown user.")
    return user_id

def getUser(user_id):
    # get user info from user_id
    # returns user info (id, user_name, balance, photo) in the form of a dictonary
    # returns False if user not registered
    # TO DO will need to update to get win/loss record from games_players table
    mySQL = connectToMySQL(mySQLdb)
    query = "SELECT id, user_name, email, balance, photo, wins, losses, current_game_id FROM users WHERE id = %(id)s;"
    data = {
        'id': user_id
    }
    result = mySQL.query_db(query, data)
    if result:
        return result[0]  # return user info
    else:
        return False  # user not in database

def getActiveGames():
    # get game info for all active games, i.e. with game_status == 0 or 1
    # game_status: 0 if waiting, 1 if playing, 2 if completed
    # returns game info (game_id, game_status, pot, game_name, time_limit, min_players, max_players, ante, max_raise) in the form of an array of dictionaries
    mySQL = connectToMySQL(mySQLdb)
    query = "SELECT games.id as game_id, game_status, pot, game_name, time_limit, min_players, max_players, ante, max_raise FROM games JOIN game_types ON game_types.id = games.id WHERE game_status = 0 OR game_status = 1;"
    result = mySQL.query_db(query)
    return result  # return game info

def getGameTypes():
    # get info for available game types 
    # returns game type info (game_name, time_limit, min_players, max_players, ante, max_raise) in the form of an array of dictionaries
    mySQL = connectToMySQL(mySQLdb)
    query = "SELECT id, game_name, time_limit, min_players, max_players, ante, max_raise FROM game_types;"
    result = mySQL.query_db(query)
    return result  # return game types

def getGameIDFromUserID(user_id):
    mySQL = connectToMySQL(mySQLdb)
    query = "SELECT game_id FROM games_players WHERE player_id = %(p)s;"
    data = {
        'p': user_id
    }
    result = mySQL.query_db(query, data)
    return result[0]['game_id']

def getGame(game_id):
    # get game info for game_id
    # returns game info (game_id, game_status, pot, game_name, time_limit, min_players, max_players, ante, max_raise) in the form a dictionary
    mySQL = connectToMySQL(mySQLdb)
    query = "SELECT games.id AS game_id, game_status, pot, current_turn, num_players, game_name, time_limit, min_players, max_players, ante, max_raise FROM games JOIN game_types ON games.game_type_id = game_types.id WHERE games.id = %(g)s;"
    data = {
        'g': game_id
    }
    games = mySQL.query_db(query, data)
    return games[0]

def getPlayers(game_id):
    mySQL = connectToMySQL(mySQLdb)
    query = "SELECT users.id as id, user_name, balance, photo, wins, losses, total_bet, turn FROM games_players JOIN users ON games_players.player_id = users.id WHERE games_players.game_id = %(g)s;"
    data = {
        'g': game_id
    }
    players = mySQL.query_db(query, data)
    return players

def getCards(game_id, player_id):
    mySQL = connectToMySQL(mySQLdb)
    query = "SELECT id AS card_id, number, suit, face_up FROM cards WHERE game_id = %(g)s AND player_id = %(p)s;"
    data = {
        'g': game_id,
        'p': player_id
    }
    cards = mySQL.query_db(query, data)
    return cards

def getMessages(game_id, user_id):
    mySQL = connectToMySQL(mySQLdb)
    query = "SELECT id AS message_id, message FROM messages WHERE game_id = %(g)s AND user_id = %(u)s ORDER BY created_at DESC;"
    data = {
        'g': game_id,
        'u': user_id
    }
    messages = mySQL.query_db(query, data)
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
    mySQL = connectToMySQL(mySQLdb)
    query = "INSERT INTO games (game_type_id, game_status, pot, current_turn, num_players, created_at, updated_at) VALUES (%(gt)s, %(gs)s, %(p)s, %(t)s, %(n)s, NOW(), NOW());"
    data = {
        'gt': game_type_id,
        'gs': 0, # 0 = waiting, 1 = playing, 2 = completed
        'p': 0, # empty pot until ante at game start
        't': 0, # zero until random at game start
        'n': 0  # no players
    }
    game_id = mySQL.query_db(query, data)
    return game_id

def getNumPlayers(game_id):
    mySQL = connectToMySQL(mySQLdb)
    query = "SELECT COUNT(id) as num_players FROM games_players WHERE game_id = %(g)s GROUP BY game_id;"
    data = {
        'g': game_id
    }
    result = mySQL.query_db(query, data)
    if result:
        return result[0]['num_players']
    else:
        return 0

def addToNumPlayers(game_id, adder):
    num_players = getNumPlayers(game_id)
    mySQL = connectToMySQL(mySQLdb)
    query = "UPDATE games SET num_players = %(n)s, updated_at = NOW() WHERE id = %(g)s;"
    data = {
        'n': num_players + adder,
        'g': game_id
    }
    mySQL.query_db(query, data)
    return num_players + adder

def addPlayerToGame(user, game_id):
    # add user to games_players for game_id
    mySQL = connectToMySQL(mySQLdb)
    query = "INSERT INTO games_players (result, total_bet, turn, game_id, player_id, created_at, updated_at) VALUES (%(r)s, %(tb)s, %(t)s, %(g)s, %(p)s, NOW(), NOW());"
    data = {
        'r': 0, # 0 = not played, 1 = lost, 2 = won
        'tb': 0, # zero bets so far
        't': 0, # will set the players position or turn when game starts
        'g': game_id,
        'p': user['id']
    }
    mySQL.query_db(query, data)
    num_players = addToNumPlayers(game_id, 1)
    # update users.current_game_id to game_id
    mySQL = connectToMySQL(mySQLdb)
    query = "UPDATE users SET current_game_id = %(g)s WHERE id = %(id)s;"
    data = {
        'g': game_id,
        'id': user['id']
    }
    return num_players

def startGame(game_id):
    # change games.game_status to 1 and set starting current_turn
    game = getGame(game_id)
    mySQL = connectToMySQL(mySQLdb)
    query = "UPDATE games SET game_status = %(gs)s, current_turn = %(t)s, updated_at = NOW() WHERE id = %(gid)s;"
    data = {
        'gs': 1, # 0 = waiting, 1 = playing, 2 = completed
        't': 1,
        'gid': game_id
    }
    mySQL.query_db(query, data)
    # ante up players
    players = getPlayers(game_id)
    for player in players:
        makeBet(player, game, game['ante'])
    # set players' turns (i.e. positions at table)
    turns = list(range(1,len(players)+1))
    shuffle(turns)
    for i in range(len(players)):
        mySQL = connectToMySQL(mySQLdb)
        query = "UPDATE games_players SET turn = %(t)s, updated_at = NOW() WHERE player_id = %(pid)s AND game_id = %(gid)s;"
        data = {
            't': turns[i],
            'pid': players[i]['id'],
            'gid': game_id
        }
        mySQL.query_db(query, data)
    # create card deck
    for number in range(1,14): # 13 numbers, 1 = Ace, 11 = Jack, 12 = Queen, 13 = King
        for suit in range(1,5):  # 4 suits: 1 = Spades, 2 = Hearts, 3 = Diamonds, 4 = Clubs
            mySQL = connectToMySQL(mySQLdb)
            query = "INSERT INTO cards (number, suit, face_up, game_id, player_id, created_at, updated_at) VALUES (%(n)s, %(s)s, %(f)s, %(g)s, NULL, NOW(), NOW());"
            data = {
                'n': number,
                's': suit,
                'f': 0, # face down
                'g': game_id
            }
            mySQL.query_db(query, data)
    return True

def getCardsInDeck(game_id):
    mySQL = connectToMySQL(mySQLdb)
    query = "SELECT id as card_id, number, suit, face_up FROM cards WHERE game_id = %(g)s AND player_id = 0;"
    data = {
        'g': game_id
    }
    cards = mySQL.query_db(query, data)
    return cards

def dealCard(game_id, user_id, face_up):
    # randomly pick card from remaining undealt cards in deck
    cards = getCardsInDeck(game_id)
    card_id = cards[randint(0, len(cards)-1)]['card_id']
    # deal card to user
    mySQL = connectToMySQL(mySQLdb)
    query = "UPDATE cards (player_id, face_up, updated_at) VALUES (%(p)s, %(f)s, NOW()) WHERE id = %(c)s;"
    data = {
        'p': user_id,
        'f': face_up,
        'c': card_id
    }
    mySQL.query_db(query, data)
    return

def makeBet(user, game, amount):
    # deduct amount from user's balance
    mySQL = connectToMySQL(mySQLdb)
    query = "UPDATE users SET balance = %(b)s, updated_at = NOW() WHERE id = %(id)s;"
    print(user)
    data = {
        'b': user['balance'] - amount,
        'id': user['id']
    }
    mySQL.query_db(query, data)
    # add amount to game's pot
    mySQL = connectToMySQL(mySQLdb)
    query = "UPDATE games SET pot = %(p)s, updated_at = NOW() WHERE id = %(g)s;"
    data = {
        'p': game['pot'] + amount,
        'g': game['game_id']
    }
    mySQL.query_db(query, data)
    # add amount to players' total_bet
    mySQL = connectToMySQL(mySQLdb)
    query = "SELECT total_bet FROM games_players WHERE game_id = %(g)s AND player_id = %(p)s;"
    data = {
        'g': game['game_id'],
        'p': user['id']
    }
    result = mySQL.query_db(query, data)
    total_bet = result[0]['total_bet']
    mySQL = connectToMySQL(mySQLdb)
    query = "UPDATE games_players SET total_bet = %(t)s, updated_at = NOW() WHERE game_id = %(g)s AND player_id = %(p)s;"
    data = {
        't': total_bet + amount,
        'g': game['game_id'],
        'p': user['id']
    }
    mySQL.query_db(query, data)
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
