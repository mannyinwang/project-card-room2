from flask import Flask, render_template, request, redirect, session
from utilities import *
from flask_socketio import SocketIO
import time


def login_registration():
    session['user_id']= None  # logout any user
    return render_template('login-registration.html')

def login_action():
    user_id = loginUser(request.form['email'], request.form['password'])
    if id:
        session['user_id'] = user_id
        return redirect('/user-profile')
    else:
        return redirect('/login-registration')

def registration_action():
    addUser(request.form['user_name'], request.form['email'], request.form['password'], request.form['confirm'])
    return redirect('/login-registration')

def user_profile():
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            return render_template('user-profile.html', user = user)
    return redirect('/login-registration')

def lobby():
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            if user.current_game_id:
                game = getGame(user.current_game_id)
                if game.game_status == 1:
                    return redirect('/card-table')
                elif game.game_status == 2:
                    removePlayerFromGame(user, user.current_game_id)
            games = getActiveGames()
            game_types = getGameTypes()
            return render_template('lobby.html', user = user, games = games, game_types = game_types)
    return redirect('/login-registration')

def lobby_join_game(game_id):
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(int(game_id))
            num_players = addPlayerToGame(user, int(game_id))
            if num_players:
                if num_players >= getGameMinPlayers(game):
                    startGame(int(game_id))
                    socketio.emit(game_id + ": card-table update") # notify other players
                    socketio.emit("lobby update") # notify others
                    return redirect('/card-table')
                else:
                    socketio.emit("lobby update") # notify others
                    return redirect('/lobby')
            else:  # user already in a game
                return redirect('/lobby')
    return redirect('/login-registration')

def lobby_leave_game(game_id):
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            getGame(int(game_id))
            removePlayerFromGame(user, int(game_id))
            socketio.emit("lobby update") # notify others
            return redirect('/lobby')
    return redirect('/login-registration')

def lobby_new_game():
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game_id = createNewGame(request.form['game_type_id'])
            num_players = addPlayerToGame(user, game_id)
            game = getGame(game_id)
            if num_players >= getGameMinPlayers(game):
                print("starting game", game_id)
                startGame(game_id)
                socketio.emit(str(game_id) + ": card-table update") # notify other players
                socketio.emit("lobby update") # notify others
                return redirect('/card-table')
            else:
                socketio.emit("lobby update") # notify others
                return redirect('/lobby')
    return redirect('/login-registration')

def card_table():
    if 'user_id' in session:
        user_id = session['user_id']
        user = getUser(user_id)
        if user:
            game_id = getGameIDFromUserID(user_id)
            game = getGame(game_id)
            players = getPlayers(game_id)
            cards = getCards(game_id, user_id)
            user_turn = getUserTurn(game_id, user_id)
            if game:
                if user_turn == game.current_turn:
                    # check if round of betting is completed and if so, check if last round; if last round, end game, otherwise deal next round
                    if not game.betting:  # betting round is completed
                        betting_round = False
                        num_rounds = getNumRounds(game_id)
                        while not game.betting and not betting_round and game.round_num < num_rounds:
                            print("dealing next round", game.betting, betting_round, game.round_num)
                            betting_round = dealRound(game_id)  # deal a round of cards
                            # time.sleep(5)
                            socketio.emit(str(game_id) + ": card-table update") # notify other players
                            print("done dealing round", game.betting, betting_round, game.round_num)
                        if not game.betting and game.round_num >= num_rounds:  # done with game
                            if game.game_status != 2:
                                print("end of game")
                                gameEnd(game_id)
                                socketio.emit(str(game_id) + ": card-table update") # notify other players
                            return render_template('card-table.html', user = user, user_turn = user_turn, game = game, players = players, cards = cards)
                        else: # start betting round
                            print("starting betting round")
                            socketio.emit(str(game_id) + ": card-table update") # notify other players
                            gameStartBettingRound(user, game_id)
                            return render_template('card-table.html', user = user, user_turn = user_turn, game = game, players = players, cards = cards)
                    else:  # continue betting round
                        print("continuing betting round")
                        return render_template('card-table.html', user = user, user_turn = user_turn, game = game, players = players, cards = cards)
                else:
                    print("not this user's turn")
                    return render_template('card-table.html', user = user, user_turn = user_turn, game = game, players = players, cards = cards)                 
            else:
                return redirect('/lobby')
    return redirect('/login-registration')

def card_table_fold(game_id):
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(int(game_id))
            if game:
                gameFold(user, game_id)
                socketio.emit(game_id + ": card-table update") # notify other players
                socketio.emit("leaderboard update")
    return redirect('/card-table')

def card_table_leave(game_id):
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(int(game_id))
            if game:
                if game.game_status ==1:
                    gameFold(user, game_id)
                    socketio.emit("leaderboard update")
                gameLeave(user)
                socketio.emit(game_id + ": card-table update") # notify other players
    return redirect('/lobby')

def card_table_call(game_id):
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            if user.current_game_id == int(game_id):
                gameCall(user, int(game_id))
                socketio.emit(game_id + ": card-table update") # notify other players
                return redirect('/card-table')
    return redirect('/lobby')

def card_table_raise():
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(request.form['game_id'])
            if game:
                gameRaise(user, game.id, int(request.form['raise_amount']))
                socketio.emit(str(game.id) + ": card-table update") # notify other players
                return redirect('/card-table')
    return redirect('/lobby')

def card_table_message():
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(request.form['game_id'])
            if game:
                gameMessage(user, game.id, request.form['message'])
                socketio.emit(str(game.id) + ": card-table update") # notify other players
                return redirect('/card-table')
    return redirect('/lobby')

def card_table_new_game(game_id):
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(int(game_id))
            if game:
                if game.num_players >= getGameMinPlayers(game):
                    gameStartNewGame(int(game_id))
                    socketio.emit(game_id + ": card-table update") # notify other players
                    return redirect('/card-table')
                else:
                    gameLeave(user)
                    new_game_id = createNewGame(game.game_type_id)
                    num_players = addPlayerToGame(user, new_game_id)
                    socketio.emit(game_id + ": card-table update") # notify other players
                    socketio.emit("lobby update") # notify other players
                    return redirect('/lobby')
    return redirect('/lobby')

def leaderboard():
    if 'user_id' in session:
        user = getUser(session['user_id'])
    records = getTopWinLossRecords(10)
    bettors = getTopBettors(10)
    return render_template('leaderboard.html', user = user, records = records, bettors = bettors, starting_balance=starting_balance)

def logout_action():
    session.clear()
    flash("Logged out.")
    return redirect('/login-registration')