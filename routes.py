from config import app
from controller import *

app.add_url_rule('/', view_func=login_registration)
app.add_url_rule('/login-registration', view_func=login_registration)
app.add_url_rule('/login-action', view_func=login_action, methods=['POST'])
app.add_url_rule('/registration-action', view_func=registration_action, methods=['POST'])

app.add_url_rule('/user-profile', view_func=user_profile)
app.add_url_rule('/lobby', view_func=lobby)
app.add_url_rule('/lobby/join-game/<game_id>', view_func=lobby_join_game)
app.add_url_rule('/lobby/leave-game/<game_id>', view_func=lobby_leave_game)
app.add_url_rule('/lobby/new-game', view_func=lobby_new_game, methods=['POST'])
app.add_url_rule('/card-table', view_func=card_table)

app.add_url_rule('/card-table/fold/<game_id>', view_func=card_table_fold)
app.add_url_rule('/card-table/call/<game_id>', view_func=card_table_call)
app.add_url_rule('/card-table/raise', view_func=card_table_raise, methods=['POST'])
app.add_url_rule('/card-table/message', view_func=card_table_message, methods=['POST'])
app.add_url_rule('/card-table/leave/<game_id>', view_func=card_table_leave)
app.add_url_rule('/card-table/new-game/<game_id>', view_func=card_table_new_game)
app.add_url_rule('/leaderboard', view_func=leaderboard)

app.add_url_rule('/logout-action', view_func=logout_action)

