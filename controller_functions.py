from flask import Flask, render_template, request, redirect, session
from models import *
from utilities import *
from config import migrate


def login_registration():
    session['user_id']= 0  # logout any user
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
            if num_players >= game.game_type.min_players:
                startGame(int(game_id))
                return redirect('/card-table')
            else:
                return redirect('/lobby')
    return redirect('/login-registration')

def lobby_new_game():
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game_id = createNewGame(request.form['game_type_id'])
            num_players = addPlayerToGame(user, game_id)
            game = getGame(game_id)
            if num_players >= game.game_type.min_players:
                startGame(game_id)
                return redirect('/card-table')
            else:
                return redirect('/lobby')
    return redirect('/login-registration')

def DUMMYcard_table():
    game_id = getGameIDFromUserID(user_id=1)
    game, players = DUMMYgetGame(game_id)
    user = {}
    if game:
        return render_template('card-table.html', user = user, game = game, players = players)
    else:
        return redirect('/lobby')

def card_table():
    if 'user_id' in session:
        user_id = session['user_id']
        user = getUser(user_id)
        if user:
            game_id = getGameIDFromUserID(user_id)
            game = getGame(game_id)
            players = getPlayersWithCardsAndMessages(game_id)
    if game:
        return render_template('card-table.html', user = user, game = game, players = players)
    else:
        return redirect('/lobby')

def card_table_fold(game_id):
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(int(game_id))
            if game:
                gameFold(user, game)
    return redirect('/card-table')

def card_table_leave(game_id):
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(int(game_id))
            if game:
                gameFold(user, game)
    return redirect('/lobby')

def card_table_call(game_id):
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(int(game_id))
            if game:
                gameCall(user, game)
                return redirect('/card-table')
    return redirect('/lobby')

def card_table_raise():
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(request.form['game_id'])
            if game:
                gameRaise(user, game, request.form['raise_amount'])
                return redirect('/card-table')
    return redirect('/lobby')

def card_table_message():
    if 'user_id' in session:
        user = getUser(session['user_id'])
        if user:
            game = getGame(request.form['game_id'])
            if game:
                gameMessage(user, game, request.form['message'])
                return redirect('/card-table')
    return redirect('/lobby')

def leaderboard():
    if 'user_id' in session:
        user = getUser(session['user_id'])
    records = getTopWinLossRecords(10)
    bettors = getTopBettors(10)
    return render_template('leaderboard.html', user = user, records = records, bettors = bettors)

def logout_action():
    session.clear()
    flash("Logged out.")
    return redirect('/login-registration')
