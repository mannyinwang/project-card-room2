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
        return redirect('/lobby')
    else:
        return redirect('/login-registration')

def registration_action():
    addUser(request.form['user_name'], request.form['email'], request.form['password'], request.form['confirm'])
    return redirect('/login-registration')

def user_profile():
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            user_info = getUserProfile(user)
            return render_template('user-profile.html', user = user_info)
    return redirect('/login-registration')

def lobby():
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            if user.current_game_id:  # user is in a game
                game = getGame(user.current_game_id)
                if game.game_status == 1:  # game is playing
                    return redirect('/card-table')
                elif game.game_status == 2:  # game is completed
                    removePlayerFromGame(user, user.current_game_id)
            lobbyInfo = getLobbyInfo(user)
            return render_template('lobby.html', user = lobbyInfo['user'], games = lobbyInfo['games'], game_types = lobbyInfo['game_types'])
    return redirect('/login-registration')

def lobby_join_game(game_id):
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(int(game_id))
            addPlayerToGame(user, int(game_id))
            num_players = getNumNonExitedPlayers(int(game_id))
            if num_players:
                if num_players >= getGameMinPlayers(game):
                    if game.game_status == 0: # not already playing
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
            addPlayerToGame(user, game_id)
            num_players = getNumWaitingOrActivePlayers(int(game_id))
            game = getGame(game_id)
            if num_players >= getGameMinPlayers(game):
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
            user_turn = getUserTurn(game_id, user_id)
            if game and game.game_status != 0:
                if user_turn == game.current_turn:
                    # check if round of betting is completed and if so, check if last round; if last round, end game, otherwise deal next round
                    if not game.betting:  # betting round is completed
                        betting_round = False
                        num_rounds = getNumRounds(game_id)
                        if not game.betting and not betting_round and game.round_num < num_rounds:
                            while not game.betting and not betting_round and game.round_num < num_rounds:
                                betting_round = dealRound(game_id)  # deal a round of cards
                                time.sleep(0.3) # let data load before updating all pages
                                socketio.emit("lobby update") # notify other players
                                socketio.emit(str(game_id) + ": card-table update") # notify other players
                        elif not game.betting and game.round_num >= num_rounds:  # done with game
                            if game.game_status != 2:
                                gameEnd(game_id)
                                time.sleep(0.3)
                                socketio.emit("lobby update") # notify other players
                                socketio.emit("leaderboard update")
                                socketio.emit(str(game_id) + ": card-table update") # notify other players
                        else: # start betting round
                            gameStartBettingRound(user, game_id)
                            socketio.emit(str(game_id) + ": card-table update") # notify other players
                time.sleep(0.3)  # important to let data load into database from other actions before getting data and rendering
                gameInfo = getGameInfo(user, game)
                return render_template('card-table.html', user = gameInfo['user'], game = gameInfo['game'], players = gameInfo['players'], cards = gameInfo['cards'])                 
            else:
                return redirect('/lobby')
    return redirect('/login-registration')

def card_table_fold(game_id):
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(int(game_id))
            if game:
                if user.current_game_id == int(game_id):
                    if isUserTurn(user,game):
                        gameFold(user, game_id)
                        socketio.emit(game_id + ": card-table update") # notify other players
                        socketio.emit("leaderboard update")
                return redirect('/card-table')
    return redirect('/lobby')

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
            game = getGame(int(game_id))
            if game:
                if user.current_game_id == int(game_id):
                    if isUserTurn(user,game):
                        gameCall(user, int(game_id))
                        socketio.emit(str(game_id) + ": card-table update") # notify other players
                return redirect('/card-table')
    return redirect('/lobby')

def card_table_raise():
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(request.form['game_id'])
            if game:
                if user.current_game_id == game.id:
                    if isUserTurn(user,game):
                        raise_amount = request.form['raise_amount']
                        if raise_amount:
                            if isUserTurn(user,game):
                                gameRaise(user, game.id, int(raise_amount))
                                socketio.emit("lobby update") # notify of update to pot
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
                num_players = getNumNonExitedPlayers(int(game_id))
                print("Num players in new game = ", num_players)
                if num_players >= getGameMinPlayers(game):
                    game_started = gameStartNewGame(user, int(game_id))
                    socketio.emit("lobby update") # notify other players
                    if game_started:
                        socketio.emit(game_id + ": card-table update") # notify other players
                        return redirect('/card-table')
                    else:
                        return redirect('/lobby')
                else:
                    # gameLeave(user)
                    # new_game_id = createNewGame(game.game_type_id)
                    # addPlayerToGame(user, new_game_id)
                    # socketio.emit(game_id + ": card-table update") # notify other players
                    # socketio.emit("lobby update") # notify other players
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
