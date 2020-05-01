from flask import Flask, render_template, request, redirect, session
from models import *
from utilities import *

def DUMMYcard_table():
    game, players, cards = DUMMYgetGame(1)
    user = {'user_name': 'Joe'}
    if game:
        return render_template('card-table.html', user = user, game = game, players = players, cards = cards)
    else:
        return redirect('/lobby')

def DUMMYgetGame(game_id):
    game = {}
    game['game_id'] = 1
    game['game_status'] = 1
    game['pot'] = 200
    game['current_turn'] = 2
    game['num_players'] = 3
    game['game_type'] = {}
    game['game_type']['game_name'] = '5-Card Stud'
    game['game_type']['time_limit'] = 30
    game['game_type']['current_turn'] = 0
    game['game_type']['num_players'] = 4
    game['game_type']['min_players'] = 4
    game['game_type']['max_players'] = 4
    game['game_type']['ante'] = 10
    game['game_type']['max_raise'] = 50
    players = [{},{},{}]
    players[0] = {}
    players[0]['turn'] = 1
    players[0]['player'] = {}
    players[0]['player']['user_id'] = 1
    players[0]['player']['user_name'] = "Mary"
    players[0]['player']['balance'] = 7000
    players[0]['player']['photo'] = False
    players[0]['player']['message'] = 'Hi All!'
    players[1] = {}
    players[1]['turn'] = 2
    players[1]['player'] = {}
    players[1]['player']['user_id'] = 2
    players[1]['player']['user_name'] = "Joe"
    players[1]['player']['balance'] = 5000
    players[1]['player']['photo'] = False
    players[1]['player']['message'] = 'Hi!'
    players[2] = {}
    players[2]['turn'] = 3
    players[2]['player'] = {}
    players[2]['player']['user_id'] = 3
    players[2]['player']['user_name'] = "Elizabeth"
    players[2]['player']['balance'] = 3000
    players[2]['player']['photo'] = False
    players[2]['player']['message'] = "Hey losers!"
    cards = [{},{},{},{},{}]
    cards[0] = {'number': 5, 'suit': 1, 'face_up': 1}
    cards[1] = {'number': 10, 'suit': 1, 'face_up': 1}
    cards[2] = {'number': 1, 'suit': 2, 'face_up': 0}
    cards[3] = {'number': 7, 'suit': 3, 'face_up': 0}
    cards[4] = {'number': 11, 'suit': 4, 'face_up': 0}
    return game, players, cards