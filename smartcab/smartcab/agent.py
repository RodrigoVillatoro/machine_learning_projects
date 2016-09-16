import logging
import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        # sets self.env = env, state = None, next_waypoint = None,
        # and a default color

        super(LearningAgent, self).__init__(env)

        # override color
        self.color = 'red'
        # simple route planner to get next_waypoint
        self.planner = RoutePlanner(self.env, self)
        # TODO: Initialize any additional variables here

        # Keys: light-oncoming-right-left
        self.states = self.generate_states_dict_with_empty_rewards()

        # Will define the next action we take (random vs learned)
        self.epsilon = 0.10

        # Gamma
        self.gamma = 0.15

        # Total reward obtained:
        self.total_reward = 0

        # Logging
        logging.basicConfig(filename='smartcab.log', level=logging.DEBUG)

    def generate_states_dict_with_empty_rewards(self):

        # Dictionary to store states: keys are inputs, values are rewards
        LIGHT = ['red', 'green']
        VALID_ACTIONS = [None, 'forward', 'left', 'right']

        # Store all input combinations
        all_inputs = []

        # Dictionary with all possible combinations, with rewards 0
        states = {}

        for light in LIGHT:
            for oncoming in VALID_ACTIONS:
                for right in VALID_ACTIONS:
                    for left in VALID_ACTIONS:
                        for hurry_up in ['yes', 'no']:
                            for next_waypont in VALID_ACTIONS:
                                all_inputs.append('{}-{}-{}-{}-{}-{}'.format(
                                    light, oncoming, right, left, hurry_up,
                                    next_waypont))

        for possible_input in all_inputs:
            states[possible_input] = {}
            for valid_action in VALID_ACTIONS:
                states[possible_input][valid_action] = 0

        return states

    def update_state(self, inputs, deadline, next_waypoint):

        # Input values will serve as key in states dictionary
        input_values = [str(value) for key, value in inputs.items()]

        if deadline < 20:
            hurry_up = 'yes'
        else:
            hurry_up = 'no'

        # Generate state base on inputs, including deadline and next_waypoint
        state = '-'.join(input_values)
        state += '-{}'.format(hurry_up)
        state += '-{}'.format(next_waypoint)

        return state

    def follow_next_waypoint_directly_from_plan(self, inputs, next_waypoint):
        """ When we are in a hurry, one alternative would be to just follow the
        next_waypoint and wait when we needed to wait.
        """
        state = None
        if inputs['light'] == 'green':
            # 0: Green light, not turning left --will continue forward or right
            if next_waypoint != 'left':
                state = 'move'
            else:
                # 1: Green light, turning left, NO oncoming traffic.
                if inputs['oncoming'] is None or inputs['oncoming'] == 'left':
                    state = 'move'
                # 2: Green light, turning left, going forward or turning right.
                else:
                    state = 'wait'
        else:  # Red light
            # 3: Red light, moving forward.
            if next_waypoint == 'forward':
                state = 'wait'
            # 4: Red light, turning right, NO oncoming traffic.
            elif next_waypoint == 'right' and inputs['left'] != 'forward':
                state = 'move'
            # 5: Red light, turning right, cars coming our way.
            else:
                state = 'wait'

        # TODO: Select action according to your policy
        if state == 'move':
            action = next_waypoint
        else:
            action = None

        return action

    def get_action_by_cheating(self, deadline, inputs, next_waypoint, state):
        """
        It's called "get_action_by_cheating" because if the cab is in a hurry
        (meaning that it has less than 10 moves left), then the cab will
        follow the next_waypoint by waiting correctly when it has to wait
        (i.e. we are telling it what to do, and it has not really learned it
        on it's own.)
        """
        if deadline < 10:
            action = self.follow_next_waypoint_directly_from_plan(
                inputs, self.next_waypoint)
        else:
            # Explore
            random_number = random.uniform(0, 1)
            if random_number < self.epsilon:
                # Take random action:
                action = random.choice([None, 'forward', 'left', 'right'])
            # Exploit
            else:
                # Take action with maximum reward
                action = max(self.states[state], key=self.states[state].get)

        return action

    def get_action(self, state):
        """
        Will return the action that maximizes the reward in most cases, or
        a random action in case the random number generated is less than
        self.epsilon.
        """
        # Explore
        random_number = random.uniform(0, 1)
        if random_number < self.epsilon:
            # Take random action:
            action = random.choice([None, 'forward', 'left', 'right'])
        # Exploit
        else:
            # Take action with maximum reward
            action = max(self.states[state], key=self.states[state].get)

        return action

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        logging.debug(
            'Gamma {}, Epsilon {}, Cumulative Reward: {}'.format(
                self.gamma, self.epsilon, self.total_reward))

    def update(self, t):

        # Gather inputs

        # from route planner, also displayed by simulator
        self.next_waypoint = self.planner.next_waypoint()
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        state = self.update_state(inputs, deadline, self.next_waypoint)
        self.state = state

        # Get action the smartcab should execute
        action = self.get_action(state)

        # Execute action and get reward
        reward = self.env.act(self, action)
        self.states[state][action] += reward

        # Increment total reward
        self.total_reward += reward

        # TODO: Learn policy based on state, action, reward

        # Gather inputs for next trip
        self.next_waypoint = self.planner.next_waypoint()
        inputs = self.env.sense(self)
        next_state = self.update_state(inputs, deadline, self.next_waypoint)

        # Learn Q
        # Q(s, a) = R(s, a) + Gamma * Max[Q(next state, all actions)]
        # http://mnemstudio.org/path-finding-q-learning-tutorial.htm
        self.states[state][action] += self.gamma * max(
            self.states[next_state].values())

        # [debug]
        print "LearningAgent.update(): deadline = {}, inputs = {}, " \
              "action = {}, reward = {}".format(
            deadline, inputs, action, reward)


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set
    # display=False
    sim = Simulator(e, update_delay=0.15, display=True)

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
