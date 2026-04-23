user_memory = {}

def get_context(user_id):
    return user_memory.get(user_id, {})

def update_context(user_id, key, value):
    if user_id not in user_memory:
        user_memory[user_id] = {}
    user_memory[user_id][key] = value