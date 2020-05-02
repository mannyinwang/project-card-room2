from flask import flash
from config import bcrypt, re, EMAIL_REGEX, PWD_REGEX, socketio, db, or_
from random import seed, randint, shuffle
from models import User, Game, Player, Message, Card, GameType, GameRound
from datetime import datetime

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

def getUserTurn(game_id, user_id):
    player = Player.query.filter_by(game_id=game_id, player_id=user_id).first()
    if player:
        return player.turn
    else:
        return False

def getActiveGames():
    # get game info for all active games, i.e. with game_status == 0 or 1
    # game_status: 0 if waiting, 1 if playing, 2 if completed
    # returns game info (game_id, game_status, pot, game_name, time_limit, min_players, max_players, ante, max_raise) in the form of an array of dictionaries
    active_games = Game.query.filter(or_(Game.game_status == 0, Game.game_status ==1)).all()
    return active_games  # return game info

def getGameTypes():
    # get info for available game types 
    # returns game type info (game_name, time_limit, min_players, max_players, ante, max_raise) in the form of an array of dictionaries
    game_types = GameType.query.all()
    return game_types  # return game types

def getGameIDFromUserID(user_id):
    user = User.query.get(user_id)
    game = Game.query.get(user.current_game_id)
    if game:
        return game.id
    else:
        return False

def getGameInfo(user, game):
    players = getPlayers(game.id)
    cards = getCards(game.id, user.id)
    gameInfo = {}
    gameInfo['user'] = {}
    gameInfo['user']['user_name'] = user.user_name
    gameInfo['user']['turn'] = getUserTurn(game.id, user.id)
    gameInfo['game'] = {}
    gameInfo['game']['id'] = game.id
    gameInfo['game']['game_name'] = game.game_type.game_name
    gameInfo['game']['game_status'] = game.game_status
    gameInfo['game']['ante'] = game.game_type.ante
    gameInfo['game']['round_num'] = game.round_num
    gameInfo['game']['pot'] = game.pot
    gameInfo['game']['current_turn'] = game.current_turn
    gameInfo['game']['max_raise'] = game.game_type.max_raise
    gameInfo['game']['time_limit'] = game.game_type.time_limit
    gameInfo['game']['num_players'] = getNumPlayers(game.id)
    gameInfo['players'] = []
    for player in players:
        playerInfo = {}
        playerInfo['user_name'] = player.player.user_name
        playerInfo['balance'] = player.player.balance
        playerInfo['total_bet'] = player.total_bet
        playerInfo['turn'] = player.turn
        playerInfo['result'] = player.result
        playerInfo['cards'] = []
        cards = Card.query.filter_by(player_id=player.player_id, game_id=game.id).order_by(Card.updated_at)
        for card in cards:
            cardInfo = {}   
            cardInfo['face_up'] = card.face_up
            if card.face_up:
                cardInfo['number'] = card.number
                cardInfo['suit'] = card.suit
            else:
                cardInfo['number'] = 0
                cardInfo['suit'] = 0
            playerInfo['cards'].append(cardInfo)
        message = Message.query.filter_by(player_id=player.player_id, game_id=game.id).order_by(Message.created_at.desc()).first()
        if message:
            playerInfo['message'] = message.message
        gameInfo['players'].append(playerInfo)
    gameInfo['cards'] = []
    cards = Card.query.filter_by(player_id=user.id, game_id=game.id).order_by(Card.updated_at)
    for card in cards:
        cardInfo = {}
        cardInfo['number'] = card.number
        cardInfo['suit'] = card.suit
        cardInfo['face_up'] = card.face_up
        gameInfo['cards'].append(cardInfo)

    return gameInfo

def getGame(game_id):
    # get game info for game_id
    # returns game info (game_id, game_status, pot, game_name, time_limit, min_players, max_players, ante, max_raise) in the form a dictionary
    game = Game.query.get(game_id)
    return game

def getGameMinPlayers(game):
    return game.game_type.min_players

def getPlayers(game_id):
    players = Player.query.filter_by(game_id=game_id)
    return players

def getCards(game_id, player_id):
    cards = Card.query.filter_by(game_id=game_id, player_id=player_id)
    return cards

def getMessages(game_id, player_id):
    result = Message.query.filter_by(game_id=game_id, player_id=player_id).order_by(Message.created_at.desc()).first()
    if result: 
        return result.message
    else:
        return False

def createNewGame(game_type_id):
    new_game = Game(game_type_id=game_type_id, game_status=0, pot=0, current_turn=0, num_players=0)
    db.session.add(new_game)
    db.session.commit()
    return new_game.id

def getNumPlayers(game_id):
    num_players = Game.query.get(game_id).num_players
    return num_players

def getNumActivePlayers(game_id):
    num_active_players = Player.query.filter_by(game_id=game_id, result=1).count()
    return num_active_players

def addToNumPlayers(game_id, adder):
    num_players = getNumPlayers(game_id)
    Game.query.get(game_id).num_players = num_players + adder
    db.session.commit()
    return num_players + adder

def addPlayerToGame(user, game_id):
    # if user is already in game, cannot add
    if user.current_game_id == None:
        # check if user was previously a player in the game
        player = Player.query.filter_by(game_id=game_id, player_id=user.id).first()
        if player:  # player was previously in the game
            player.result = 0  # set to 0 for waiting
            db.session.commit()
        else:
            # add user to players for game_id
            new_player = Player(result=0, total_bet=0, turn=0, game_id=game_id, player_id = user.id)
            db.session.add(new_player)
            db.session.commit()
        # increment number of players in game by 1
        num_players = addToNumPlayers(game_id, 1)
        # update users.current_game_id to game_id
        user.current_game_id = game_id
        db.session.commit()
        return num_players
    else:
        return False  # cannot add user to game since already in a game

def removePlayerFromGame(user, game_id):
    # if user not in a game, cannot remove
    if user.current_game_id != None:
        # remove user to players for game_id
        player = Player.query.filter_by(game_id=game_id, player_id=user.id).first()
        if player:
            player.result = 4  # set to 4 for exited before playing
            db.session.commit()
            # decrement number of players in game by 1
            num_players = addToNumPlayers(game_id, -1) 
            # update users.current_game_id to 0
            user.current_game_id = None
            db.session.commit()
            return num_players
        else:
            return False
    else:
        return False  # cannot remove user from game since not in a game

def startGame(game_id):
    # change games.game_status to 1 and set starting current_turn
    game = getGame(game_id)
    game.game_status = 1 # 0 = waiting, 1 = playing, 2 = completed
    game.current_turn = 1
    game.starting_turn = 1
    game.betting = 0
    game.round_num = 0
    db.session.commit()
    # ante up players and set players' turns (i.e. positions at table) and result=1
    players = getPlayers(game_id)
    num_players = getNumPlayers(game_id)
    turns = list(range(1,num_players+1))
    shuffle(turns)
    i = 0
    for player in players:
        user = User.query.get(player.player_id)
        makeBet(user, game, game.game_type.ante)
        player.result = 1
        player.turn = turns[i]
        i += 1
    game.current_bet = game.game_type.ante
    db.session.commit()
    # create card deck
    for number in range(2,15): # 2-10 numbers, 11 = Jack, 12 = Queen, 13 = King, 14 = Ace
        for suit in range(1,5):  # 1: clubs, 2: diamonds, 3: hearts, 4: spades
            new_card = Card(number=number, suit=suit, face_up=0, game_id=game_id)
            db.session.add(new_card)
    db.session.commit()
    return True

def getCardsInDeck(game_id):
    cards = Card.query.filter_by(game_id=game_id, player_id=None)
    if cards.count() == 0:
        return False
    else:
        return cards

def dealCard(game_id, user_id, face_up):
    # randomly pick card from remaining undealt cards in deck
    cards = getCardsInDeck(game_id)
    if cards:
        card = cards[randint(0, cards.count()-1)]
        # deal card to user
        card.player_id = user_id
        card.face_up = face_up
        card.updated_at = datetime.now()
        db.session.commit()
        return True
    else: # no cards left in deck
        return False

def getNumRounds(game_id):
    # returns number of rounds cards are dealt in the game
    game = Game.query.get(game_id)
    num_rounds = GameRound.query.filter_by(game_type_id=game.game_type_id).count()
    return num_rounds

def dealRound(game_id):
    # returns True if betting after this round is dealt, False otherwise
    players = Player.query.filter_by(game_id=game_id, result=1)
    game = Game.query.get(game_id)
    game.round_num = game.round_num + 1
    # game.betting = 1
    db.session.commit()
    game_round = GameRound.query.filter_by(game_type_id=game.game_type_id, round_num=game.round_num).first()
    for player in players:
        dealCard(game_id, player.player_id, game_round.face_up)
    print("game_round.round_num = ", game_round.round_num)
    print("game_round.betting = ", game_round.betting)
    return game_round.betting

def advanceTurn(game_id):
    game = getGame(game_id)
    # find the next player who has not folded, i.e. has player.result = 1
    t = game.current_turn % game.num_players + 1
    found = False
    while found == False:
        player = Player.query.filter_by(game_id=game_id, turn=t).first()
        if player:
            if player.result == 1:
                found = True
            else:
                t = t % game.num_players + 1
        else:
            return
    game.current_turn = t
    if t == game.starting_turn:
        game.betting = 0
    else:
        game.betting = 1
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

def gameStartBettingRound(user, game_id):
    player = Player.query.filter_by(game_id=game_id, player_id=user.id).first()
    game = Game.query.get(game_id)
    game.starting_turn = player.turn
    game.betting = 1
    db.session.commit()
    return

def gameFold(user, game_id):
    # set player.result = 3 for loss and user.losses += 1
    player = Player.query.filter_by(game_id=game_id, player_id=user.id).first()
    player.result = 3  # set to loss
    user.losses = user.losses + 1
    db.session.commit()
    # check if more than one player active; if so, advance turn; if not, remaining player is winner
    num_active_players = getNumActivePlayers(game_id)
    if num_active_players > 1:
        advanceTurn(game_id)
    else:
        gameEnd(game_id)
    return

def gameLeave(user):
    addToNumPlayers(user.current_game_id, -1)
    user.current_game_id = None
    db.session.commit()
    return False

def gameCall(user, game_id):
    player = Player.query.filter_by(game_id=game_id, player_id=user.id).first()
    game = Game.query.get(game_id)
    bet = game.current_bet - player.total_bet
    makeBet(user, game, bet)
    advanceTurn(game_id)
    return False

def gameRaise(user, game_id, raise_amount):
    player = Player.query.filter_by(game_id=game_id, player_id=user.id).first()
    game = Game.query.get(game_id)
    max_raise = game.game_type.max_raise
    if raise_amount > max_raise:
        raise_amount = max_raise
    elif raise_amount <= 0:
        raise_amount = game.game_type.ante
    makeBet(user, game, game.current_bet - player.total_bet + raise_amount)
    game.current_bet = game.current_bet + raise_amount
    game.starting_turn = player.turn
    db.session.commit()
    advanceTurn(game_id)
    return False

def gameMessage(user, game_id, message_content):
    new_message = Message(message=message_content, player_id=user.id, game_id=game_id)
    db.session.add(new_message)
    db.session.commit()
    return new_message

def gameEnd(game_id):
    # change game_status to 2 = completed
    game = Game.query.get(game_id)
    game.game_status = 2  # set game to be completed
    db.session.commit()
    # if 1 remaining player, that player is the winner
    # if >1 remaining player, compare hands to determine the winner and losers
    if getNumActivePlayers(game_id) == 1:
        winner = Player.query.filter_by(game_id=game_id, result=1).first()
        if winner:
            gameDeclareWinner(winner)
        return
    else:  # NEED TO FIX THIS TO DETERMINE BEST HAND
        winner = Player.query.filter_by(game_id=game_id, result=1).first()
        if winner:
            gameDeclareWinner(winner)
        players = Player.query.filter_by(game_id=game_id, result=1)
        for player in players:
            if player.id != winner.id:
                gameDeclareLoser(player)
    return

def gameDeclareWinner(player):
    player.result = 2
    user = User.query.get(player.player_id)
    game = Game.query.get(player.game_id)
    user.balance = user.balance + game.pot
    game.pot = 0
    user.wins = user.wins + 1
    db.session.commit()
    return

def gameDeclareLoser(player):
    player.result = 3
    user = User.query.get(player.player_id)
    user.losses = user.losses + 1
    db.session.commit()
    return

def gameShowHands(game_id):
    return

def scoreHand(cards):
    num_cards = len(cards)
    if num_cards == 1:
        score = 1+ cards[0].number/10
    elif num_cards == 2:
        if cards[0].number == cards[1].number:  # pair
            score = 2
    return score

def scoreCard(card):
    score = 1+ card.number/10
    return score

def gameStartNewGame(game_id):
    previous_game = Game.query.get(game_id)
    players = Player.query.filter(Player.game_id==game_id, Player.result != 4).all()
    new_game_id = createNewGame(previous_game.game_type_id)
    for player in players:
        user = User.query.get(player.player_id)
        user.current_game_id = None
        db.session.commit()
        addPlayerToGame(user, new_game_id)
    startGame(new_game_id)
    return

def getTopWinLossRecords(num_of_players):
    topWLRecords = User.query.order_by(User.wins / (User.losses + User.wins).desc()).limit(10)
    return topWLRecords

def getTopBettors(num_of_players):
    topBettors = User.query.order_by(User.balance.desc()).limit(10)
    return topBettors