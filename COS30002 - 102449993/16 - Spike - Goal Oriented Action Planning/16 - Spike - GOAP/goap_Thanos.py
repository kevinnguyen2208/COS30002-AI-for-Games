import copy
class GOAP_State:
    def __init__(self, states):
        self.states ={}
        for state in states:
            self.add_state(state)

    def add_state(self, name, value = False):
            self.states[name] = value

    def preconditions_met(self, action):
        for precondition in action.preconditions:
            if self.states[precondition['State']] != precondition['Needed']:
                return False
        return True

    def perform_action(self, action):
        for effect in action.effects:
            self.states[effect['State']] += effect['Result']

class GOAP_Action():
    def __init__(self, name, cost):
        self.name = name
        self.cost = cost
        self.preconditions = []
        self.effects = []

    def add_precondition(self, precondition, value = True):
        self.preconditions.append({'State':precondition, 'Needed': value})

    def add_effect(self, effect, value = True):
        self.effects.append({'State': effect,'Result': value})

class GOAP_Agent:
    def __init__(self):
        self.state = []
        self.actions = []
        self.running_cost = 0

        self.paths_evaluated = 0


    def perform_action(self, action):
        self.state.perform_action(action)
        self.running_cost += action.cost

    def plan(self, goal, state = None, path = None, start_action = None):

        if state is None:
            state = copy.deepcopy(self.state)

        if path is None:
            path = {'Actions': [], 'Ratio': 0}
            self.paths_evaluated = 0

        if start_action:
            path['Actions'].append(start_action)
            path['Ratio'] += start_action.cost
            state.perform_action(start_action)

        if state.states[goal_state]:
            self.paths_evaluated += 1
            return path

        available_actions = set()
        for action in self.actions:
            if state.preconditions_met(action):
                available_actions.add(action)


        easiest_path = None
        for action in available_actions:
            potential_path = self.plan(goal_state, copy.deepcopy(state), copy.deepcopy(path), action)

        if not easiest_path or potential_path['Ratio'] < easiest_path['Ratio']:
            easiest_path = potential_path

        return easiest_path


get_Gauntlet = GOAP_Action('get Gauntlet',5412989)
get_Gem = GOAP_Action('get Gem', 600860)
fight_Thanos = GOAP_Action('fight Thanos', 7986756)

agent = GOAP_Agent()
agent.state = GOAP_State(
    [
        'Has Gem',
        'Has Gauntlet',
        'Defeat Thanos'
    ])
agent.actions = [
    get_Gauntlet,
    get_Gem,
    fight_Thanos
]

get_Gem.add_precondition('Has Gem', False)
get_Gem.add_effect('Has Gem')
get_Gauntlet.add_precondition('Has Gem')
get_Gauntlet.add_precondition('Has Gauntlet', False)
get_Gauntlet.add_effect('Has Gauntlet')
fight_Thanos.add_precondition('Has Gauntlet')
fight_Thanos.add_precondition('Defeat Thanos', False)
fight_Thanos.add_effect('Defeat Thanos')


print(
"""--------------------------------
A: Do you want see the possibility of you saving the universe?
B: Quit
--------------------------------""")
option = input("Enter option:")
if option.lower() == "a":
    print("""--------------------------------
A: Steal Gem
B: Steal Gauntlet
C: Kill Thanos
D: Too hard ! Get me out
--------------------------------""")
    option = input("Enter your choice:")
    if option.lower() == "a":
        goal_state = 'Has Gem'
        path = agent.plan(goal_state)
        print('Goal: ' + goal_state + "\n")
        for i in range(len((path['Actions']))):
            print(str(i+1) + ') ' + path['Actions'][i].name +' (' + str(path['Actions'][i].cost) + ')')
        print('Win ratio: 1/' + str(path['Ratio']))
        pass

    elif option.lower() == "b":
        goal_state = 'Has Gauntlet'
        path = agent.plan(goal_state)
        print('Goal: ' + goal_state + "\n")
        for i in range(len((path['Actions']))):
            print(str(i+1) + ') ' + path['Actions'][i].name + ' (' + str(path['Actions'][i].cost) + ')')
        print('Win ratio: 1/' + str(path['Ratio']))
        pass
        
    elif option.lower() == "c":
        goal_state = 'Defeat Thanos'
        path = agent.plan(goal_state)
        print('Goal: ' + goal_state + "\n")
        for i in range(len((path['Actions']))):
            print(str(i+1) + ') ' + path['Actions'][i].name +' (' + str(path['Actions'][i].cost) + ')')
        print('Win ratio: 1/' + str(path['Ratio']))
        pass

    elif option.lower() == "d":
        print("--------------------------------")
        print("Understandable choice!")
        pass

elif option.lower() == "b":
    print("--------------------------------")
    print("Understandable choice!")
    pass
else:
    print("You can only selct A or B")
    print("Please try again")
    pass
