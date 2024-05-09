import streamsync as ss

def increment(state, context, session: dict):
    state['counter'] += 1

def decrement(state, context, session: dict):
    state['counter'] -= 1

def register_email(state, session: dict):
    state['email'] = session['userinfo'].get('email', 'N/D')


initial_state = ss.init_state({
    "counter": 26,
    "email": "N/D"
})
