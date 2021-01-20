#variables
mana = 12
health = 12
monster = 10


states = ['attack', 'ultimate', 'neutral']
current_state = 'neutral'

alive = True
user_move = True
max_limit = 100
game_time = 0

while alive and user_move:
    game_time += 1

# Attack : attack when encounter monster, gold increases, mana reduces, health reduces
    if current_state == 'attack':
        print('Fight !!!')
        mana -= 1
        health -= 1
        monster -= 1 
        if monster == 1:
            current_state = "ultimate"

    # Ultimate : when there is 1 monster left (BOSS), mana decreses more, health decreases more
    elif current_state == 'ultimate':
        print('Last one left !!!')
        mana -= 2
        health -= 2
        monster -= 1
        if monster == 0:
            current_state = 'neutral'

    # Neutral : does nothing, mana regens, health regens
    elif current_state == 'neutral':
        print('Rest yourself')
        mana += 1
        health += 1
        monster += 1
        if monster > 1:
            current_state = 'attack'

# Death 
    if health < 1:
        alive = False

    # Game ends
    if game_time > max_limit:
        running = False

print ('GAME OVER')