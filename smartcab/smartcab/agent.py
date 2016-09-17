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

        # Parameters
        self.epsilon = 0.10  # explore vs exploit
        self.gamma = 0.15  # discount factor
        self.alpha = 0.30  # learning rate

        # Cumulative reward obtained:
        self.total_reward = 0

        # Counter of positive rewards (for report)
        self.num_total_rewards = 0
        self.num_negative_rewards = 0

        # Did the agent reach it's destination on time?
        self.reached_destination = False

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
                inputs, next_waypoint)
        else:
            random_number = random.uniform(0, 1)
            if random_number < self.epsilon:
                # Explore: take random action
                action = random.choice([None, 'forward', 'left', 'right'])
            # Exploit
            else:
                # Exploit: take action with maximum reward
                action = max(self.states[state], key=self.states[state].get)

        return action

    def get_action(self, state):
        """
        Will return the action that maximizes the reward in most cases, or
        a random action in case the random number generated is less than
        self.epsilon.
        """
        random_number = random.uniform(0, 1)
        if random_number < self.epsilon:
            # Explore: take random action
            action = random.choice([None, 'forward', 'left', 'right'])
        else:
            # Exploit: take action with maximum reward
            action = max(self.states[state], key=self.states[state].get)

        return action

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

        # Calculate the percentage of negative rewards
        try:
            pct_neg_rewards = \
                float(self.num_negative_rewards)/float(self.num_total_rewards)
            pct_neg_rewards = round(pct_neg_rewards * 100, 1)
        except ZeroDivisionError:
            pct_neg_rewards = 0

        logging.debug(
            'Gamma {}, Alpha {}, Epsilon {}, Rewards: {} : {} : {}'.format(
                self.gamma, self.alpha, self.epsilon, self.total_reward,
                pct_neg_rewards, int(self.reached_destination)))

        # Reset rewards
        self.num_total_rewards = 0
        self.num_negative_rewards = 0

    def update(self, t):

        # Gather inputs

        # from route planner, also displayed by simulator
        self.next_waypoint = self.planner.next_waypoint()
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = self.update_state(inputs, deadline, self.next_waypoint)

        # Get action the smartcab should execute
        action = self.get_action(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)
        self.states[self.state][action] += reward

        # Increment total reward
        self.total_reward += reward

        # Increment counter (for final report)
        self.num_total_rewards += 1

        if reward < 0:
            self.num_negative_rewards += 1

        # TODO: Learn policy based on state, action, reward

        # Gather inputs for next trip
        self.next_waypoint = self.planner.next_waypoint()
        inputs = self.env.sense(self)
        next_state = self.update_state(inputs, deadline, self.next_waypoint)

        # Learn Q
        self.states[self.state][action] += self.alpha * (
            reward + self.gamma * max(self.states[next_state].values()) -
            self.states[self.state][action])

        # [debug]
        print "LearningAgent.update(): deadline = {}, inputs = {}, " \
              "action = {}, reward = {}".format(
                deadline, inputs, action, reward)

        # For final report
        self.reached_destination = self.env.done


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to
    # allow longer trials

    # Now simulate it
    # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set
    # display=False
    sim = Simulator(e, update_delay=0.01, display=False)

    sim.run(n_trials=101)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window,
    # or hit Ctrl+C on the command-line


if __name__ == '__main__':
    for i in range(0, 3):
        run()
