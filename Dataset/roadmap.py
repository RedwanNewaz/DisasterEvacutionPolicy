import osmnx as ox
import matplotlib.pyplot as plt
import json
import pandas as pd
import networkx as nx
import numpy as np
import yaml

from geopy.distance import geodesic

def read_geospatial_json(file_path):
    try:
        # Read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Process different JSON structures
        locations = []
        # Extracting the data
        extracted_data = []
        for item in data:
            lat_lon = item.get("EPSG:4326", [])
            label = item.get("label", "unknown")
            for coord in lat_lon:
                extracted_data.append({"lat": coord["lat"], "lon": coord["lon"], "label": label})
        return extracted_data
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None




def calculate_nodecost(graph, radius):
    # Iterate over nodes
    for node in graph.nodes:
        #print(graph.nodes[node])
        center_coord = (graph.nodes[node]["y"], graph.nodes[node]["x"])
        #print ('centernode', center_coord)
        minor_count=0
        major_count = 0
        if graph.nodes[node]["minor_damage"]:
            minor_damage= graph.nodes[node]["minor_damage"]
            for indn in minor_damage:
                if is_point_in_circle(center_coord, indn, radius):
                    minor_count = minor_count - 2
        if graph.nodes[node]["major_damage"]:
            major_damage= graph.nodes[node]["minor_damage"]
            for indj in major_damage:
                if is_point_in_circle(center_coord, indj, radius):
                    major_count = major_count - 10
        graph.nodes[node]["cost"] = major_count + minor_count
    return graph



def is_point_in_circle(center_coord, point_coord, radius_km):
    """
    Checks if a given geocoordinate is within a circular region.

    Parameters:
    - center_coord: tuple, the latitude and longitude of the center (e.g., (lat, lon)).
    - point_coord: tuple, the latitude and longitude of the point to check (e.g., (lat, lon)).
    - radius_km: float, the radius of the circular region in kilometers.

    Returns:
    - bool: True if the point is within the circle, False otherwise.
    """
    distance = geodesic(center_coord, point_coord).kilometers  # Great-circle distance
    return distance <= radius_km



if __name__ == '__main__':
    # Data with latitude and longitude
    data = read_geospatial_json('dataset/Pecan, TX/flooddamage.json')

    # Extract coordinates and labels
    lats = [point['lat'] for point in data]
    lons = [point['lon'] for point in data]
    labels = [point['label'] for point in data]

    # Define a bounding box around the data
    north, south = max(lats) + 0.001, min(lats) - 0.001
    east, west = max(lons) + 0.001, min(lons) - 0.001

    # Fetch the roadmap using OSMNX
    graph = ox.graph_from_bbox(north, south, east, west, network_type='drive')

    # Extract node coordinates
    nodes, edges = ox.graph_to_gdfs(graph)
    node_coordinates = nodes[["y", "x"]]  # 'y' is latitude, 'x' is longitude


    # Convert the roadmap graph to a NetworkX graph
    G = nx.DiGraph(graph)

    # Plot the roadmap
    fig, ax = ox.plot_graph(graph, show=False, close=False, bgcolor='white', node_color='black', edge_color='gray', node_size=20, edge_linewidth=0.5)

    radius = 0.15

    df = pd.DataFrame(node_coordinates)

    # Iterate over rows
    for index, row in df.iterrows():
        #print (index, row["y"], row["x"], G.nodes[index])
        center_coord = (row["y"], row["x"])
        minor_damage=[]
        major_damage=[]
        for lat, lon, label in zip(lats, lons, labels):
            if label != 'no damage' and label != 'un-classified':
                if is_point_in_circle(center_coord, (lat, lon), radius):
                    if label == 'minor damage':
                        minor_damage.append((lat,lon))
                    if label == 'major damage':
                        major_damage.append((lat, lon))
        G.nodes[index]["minor_damage"] = minor_damage
        G.nodes[index]["major_damage"] = major_damage
        #print(G.nodes[index], minor_damage)


    #Calculate reward for each node of the roadmap graph
    G=calculate_nodecost(G, radius)

    # Convert the graph to a dictionary format (use the adjacency list format or other formats)
    graph_data = nx.node_link_data(G)

    # Save the graph as YAML
    with open("dataset/Pecan, TX/roadmap.yaml", "w") as yaml_file:
        yaml.dump(graph_data, yaml_file, default_flow_style=False)

    # # Load the graph from the YAML file
    # with open("roadmap.yaml", "r") as yaml_file:
    #     graph_data = yaml.safe_load(yaml_file)
    #
    # # Convert the data back to a NetworkX graph
    # G_loaded = nx.node_link_graph(graph_data)

    # Overlay the data points
    colors = {'no damage': 'green', 'minor damage': 'orange', 'major damage': 'red', 'un-classified': 'blue'}
    for lat, lon, label in zip(lats, lons, labels):
        if label != 'no damage' and label != 'un-classified':
            ax.scatter(lon, lat, c=colors[label], label=label, edgecolor='black', s=30, zorder=5)

            #is_point_in_circle(center, point1, radius)
    # Avoid duplicate labels in the legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper right')




    # # Display the plot
    #plt.title("Roadmap with Damage Data Overlay")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    #plt.savefig('overlaidroutemap.jpg')
    #plt.savefig('overlaidroutemap.png')
    #plt.savefig('overlaidroutemap.svg')
    plt.savefig('dataset/Pecan, TX/roadmap.pdf')
    plt.show()

