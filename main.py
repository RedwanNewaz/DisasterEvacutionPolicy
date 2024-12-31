import hydra
from omegaconf import DictConfig
from omegaconf import OmegaConf
import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
import yaml

@hydra.main(version_base=None, config_path="config", config_name="main")
def main(cfg : DictConfig) -> None:
    print(OmegaConf.to_yaml(cfg))
    # Read the YAML file

    with open(cfg.dataset.roadmap, "r") as yaml_file:
        graph_data = yaml.unsafe_load(yaml_file)

    # Convert the data back to a NetworkX graph
    G = nx.node_link_graph(graph_data, edges="links")
    G = nx.MultiDiGraph(G)
    fig, ax = ox.plot_graph(
        G,
        node_size=2,
        node_color="blue",
        edge_color="black",
        edge_linewidth=1,
        bgcolor="white"
    )
    plt.show()
if __name__ == "__main__":
    main()