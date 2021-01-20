VERBOSE = True

# Global goals with initial values
goals = {
	'Enemy Warrior HP': 15,
	'My HP': 8,
	'My Mana': 8,
}

# Global (read-only) actions and effects
actions = {
	'Attack': { 'Enemy Warrior HP': -5, 'My Mana': -2, 'My HP': -2},
	'Defend': {'Enemy Warrior HP': -3, 'My Mana': -4,'My HP': -1},
}


def apply_action(action):
	'''Change all goal values using this action. An action can change multiple
	goals (positive and negative side effects).
	Negative changes are limited to a minimum goal value of 0.
	'''
	for goal, change in list(actions[action].items()):
		goals[goal] = max(goals[goal] + change, 0)


def action_utility(action, goal):


	if goal in actions[action]:
		# Is the goal affected by the specified action?
		return -actions[action][goal]
	else:
		# It isn't, so utility is zero.
		return 0

	### Extension
	###
	###  - return a higher utility for actions that don't change our goal past zero
	###  and/or
	###  - take any other (positive or negative) effects of the action into account
	###    (you will need to add some other effects to 'actions')


def choose_action():
	'''Return the best action to respond to the current most insistent goal.
	'''
	assert len(goals) > 0, 'Need at least one goal'
	assert len(actions) > 0, 'Need at least one action'

	# Find the most insistent goal - the 'Pythonic' way...
	best_goal, best_goal_value = max(list(goals.items()), key=lambda item: item[1])

	# ...or the non-Pythonic way. (This code is identical to the line above.)
	#best_goal = None
	#for key, value in goals.items():
	#    if best_goal is None or value > goals[best_goal]:
	#        best_goal = key

	if VERBOSE: print('BEST_GOAL:', best_goal, goals[best_goal])

	# Find the best (highest utility) action to take.
	# (Not the Pythonic way... but you can change it if you like / want to learn)
	best_action = None
	best_utility = None
	for key, value in actions.items():
		# Note, at this point:
		#  - "key" is the action as a string,
		#  - "value" is a dict of goal changes (see line 35)

		# Does this action change the "best goal" we need to change?
		if best_goal in value:

			# 	# # Do we currently have a "best action" to try? If not, use this one
			if best_action is None:
				best_action = key
				best_utility = action_utility(best_action, best_utility)
				### 1. store the "key" as the current best_action
				### ...
				### 2. use the "action_utility" function to find the best_utility value of this best_action
				### ...
				# Is this new action better than the current action?
			else:
				# utility_value = action_utility(key, best_goal)
				# if utility_value > best_utility:
				# 	best_action = key
				# 	best_utility = utility_value
				utility_action = action_utility(best_action, best_utility)
				if best_utility < utility_action:
					best_utility = utility_action
				elif utility_action > best_utility:
					best_action = key
				### 1. use the "action_utility" function to find the utility value of this action
				### ...
				### 2. If it's the best action to take (utility > best_utility), keep it! (utility and action)
				### ...
			# Return the "best action"
	return best_action
#==============================================================================
#rage
def rage():
	rage = 0
	for key, value in goals.items():
		rage +=value*value
	return rage

def retrieve_rage_pow(action, goal_list):
	rage_pow = 0
	for goal, change in list(actions[action].items()):  # adds rage to the list of goals and changes
		temporary = max(goal_list[goal]+change, 0)
		rage_pow += temporary*temporary
	return rage_pow

def preferredAction(goal_list):
	best_rage = 9999
	best_action = None
	for key, value in actions.items():
		currentDis = retrieve_rage_pow(key, goal_list)
		print(key, '(', current_rage, ')')
		if currentRage < best_rage:
			best_rage = currentRage
			best_action = key
	return best_action

def test(action, goal_list):
	temporary = goal_list.copy()
	for goal, change in list( actions[action].items()):
		temporary[goal] = max(temporary[goal] +change, 0)
	return temporary

def choice(maxDepth):

	best_action = None
	best_rage_pow = 999
	best_plan = [None]

	if VERBOSE:
		print('Now Searching')

	for key, value in actions.items():
		depth = maxDepth
		print('Step 1: ', key)
		run_rage = retrieve_rage_pow(key,goals)
		print('Level of rage at: ', run_rage)
		best_action = key
		temporary = test(best_action, goals)
		print('New goals: ', temporary)
		depth -= 1
	else:
			print('Running: ', run_rage, ' Best: ', best_rage_pow)
			if run_rage < best_rage_pow:
				best_rage_pow = run_rage
				best_plan[0] = best_action
	print('Best plan is: ', best_plan)
	return best_plan

#==============================================================================

def print_actions():
	print('ACTIONS:')
	for name, effects in list(actions.items()):
		print(" * [%s]: %s" % (name, str(effects)))

def run_until_all_goals_zero():
	HR = '-'*40
	print_actions()
	print('>> Start <<')
	print(HR)
	running = True
	while running:
		print('Start:', goals)
		# What is the best action
		action = choice(1)
		print('Preparing...')
		i = 0
		#apply best action
		while i < 1:
			print('Act Now!', action[i])
			apply_action(action[i])
			i += 1
		print('Next round:', goals)
		#check to stop if fulfilled
		if all(value == 0 for goal, value in list(goals.items())):
			running = False
		if goals['My HP'] < 2 :
			print('You have died')
			running = False
		if goals['Enemy Warrior HP'] <= 1:
			print('You have bested me! Aarrgghh')
			running = False
		print(HR)
	# finished
	print('>> Done! <<')

if __name__ == '__main__':
	run_until_all_goals_zero()