
import hydra
from omegaconf import DictConfig, OmegaConf
import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
import yaml
from Algos import PolicyIteration
from shapely.geometry import LineString
from matplotlib.patches import FancyArrowPatch
from matplotlib.patches import Circle
from math import exp
import numpy as np

def visualize_policy(G, policy, cfg):
    # Create a MultiDiGraph copy of the original graph
    G_multi = nx.MultiDiGraph(G)

    # Add a 'geometry' attribute to edges (required by ox.plot_graph)
    for u, v, data in G_multi.edges(data=True):
        data['geometry'] = LineString([[G.nodes[u]['x'], G.nodes[u]['y']],
                                     [G.nodes[v]['x'], G.nodes[v]['y']]])

    # Prepare edge colors based on the policy
    edge_colors = []
    for u, v, k, data in G_multi.edges(keys=True, data=True):
        if policy[u] == v:
            edge_colors.append('r')  # Red for policy edges
        else:
            edge_colors.append('black')  # Black for non-policy edges

    # Add arrows for policy edges
    ax = plt.gca()
    for u, v, k, data in G_multi.edges(keys=True, data=True):
        if policy.get(u) == v:
            x1, y1 = G.nodes[u]['x'], G.nodes[u]['y']
            x2, y2 = G.nodes[v]['x'], G.nodes[v]['y']
            arrow = FancyArrowPatch((x1, y1), (x2, y2), color='green', arrowstyle='->', mutation_scale=10, lw=2)
            ax.add_patch(arrow)

    # draw circles for damaged areas
    for index in G.nodes:
        node = G.nodes[index]
        for key in ["major_damage", "minor_damage"]:
            if(node[key]):
                coord = np.array(node[key])
                x, y = coord.T
                ax.scatter(y, x, s=cfg.radius, color='red' if key == "major_damage" else "yellow", alpha=0.7)

    # Plot the graph
    fig, ax = ox.plot_graph(G_multi, node_size=50, node_color='skyblue',
                            edge_color=edge_colors, edge_linewidth=1,
                            edge_alpha=0.7, bgcolor='w', ax=ax)

    if cfg.save:
        fig.savefig(cfg.output_path)


@hydra.main(version_base=None, config_path="config", config_name="main")
def main(cfg: DictConfig) -> None:
    print(OmegaConf.to_yaml(cfg))

    # Read the YAML file
    with open(cfg.dataset.roadmap, "r") as yaml_file:
        graph_data = yaml.unsafe_load(yaml_file)

    # Convert the data back to a NetworkX graph
    # G = nx.node_link_graph(graph_data, edges="links")
    G = nx.node_link_graph(graph_data)

    for node in G.nodes():
        G.nodes[node]['cost'] = exp(-G.nodes[node]['cost'])

    pi = PolicyIteration(G)
    optimal_policy, value_function, iterations = pi.run()

    print("Optimal Policy:", optimal_policy)
    print("Value Function:", value_function)
    print("Iterations:", iterations)

    visualize_policy(G, optimal_policy, cfg)


if __name__ == "__main__":
    main()
