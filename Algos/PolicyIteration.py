import networkx as nx
import numpy as np

class PolicyIteration:
    def __init__(self, G, gamma=0.9, theta=1e-6):
        self.G = G
        self.gamma = gamma
        self.theta = theta
        self.V = {node: 0 for node in G.nodes()}
        self.policy = {node: next(iter(G.neighbors(node)), None) for node in G.nodes()}

    def policy_evaluation(self):
        while True:
            delta = 0
            for node in self.G.nodes():
                v = self.V[node]
                if self.policy[node] is not None:
                    self.V[node] = self.G.nodes[node]['cost'] + self.gamma * self.V[self.policy[node]]
                else:
                    self.V[node] = self.G.nodes[node]['cost']
                delta = max(delta, abs(v - self.V[node]))
            if delta < self.theta:
                break

    def policy_improvement(self):
        policy_stable = True
        for node in self.G.nodes():
            old_action = self.policy[node]
            best_value = float('inf')
            best_action = None
            for neighbor in self.G.neighbors(node):
                value = self.G.nodes[node]['cost'] + self.gamma * self.V[neighbor]
                if value < best_value:
                    best_value = value
                    best_action = neighbor
            if best_action is None:
                best_value = self.G.nodes[node]['cost']
            self.policy[node] = best_action
            if old_action != self.policy[node]:
                policy_stable = False
        return policy_stable

    def run(self):
        iteration = 0
        while True:
            iteration += 1
            self.policy_evaluation()
            if self.policy_improvement():
                break
        return self.policy, self.V, iteration

if __name__ == '__main__':
    # Example usage
    G = nx.DiGraph()
    G.add_nodes_from([0, 1, 2, 3], cost=1)
    G.add_edges_from([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)])

    pi = PolicyIteration(G)
    optimal_policy, value_function, iterations = pi.run()

    print("Optimal Policy:", optimal_policy)
    print("Value Function:", value_function)
    print("Iterations:", iterations)
