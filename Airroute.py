import heapq
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import networkx as nx

# --- Dijkstra with flexible metric (cost or time) ---
def dijkstra(graph, start, metric='cost'):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    prev = {}
    queue = [(0, start)]

    while queue:
        curr_dist, node = heapq.heappop(queue)

        for neighbor in graph[node]:
            weight = graph[node][neighbor][metric]
            new_dist = curr_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                prev[neighbor] = node
                heapq.heappush(queue, (new_dist, neighbor))

    return distances, prev

def reconstruct_path(prev, start, end):
    path = []
    while end != start:
        path.append(end)
        end = prev.get(end)
        if end is None:
            return []
    path.append(start)
    return path[::-1]

# --- GUI ---
class AirRouteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 Air Route Finder – Cost or Time Based")
        self.root.geometry("520x540")
        self.graph = {
            'DEL': {'DXB': {'cost': 2500, 'time': 200}, 'LHR': {'cost': 7000, 'time': 540}},
            'DXB': {'DEL': {'cost': 2500, 'time': 200}, 'LHR': {'cost': 2800, 'time': 420}, 'JFK': {'cost': 9000, 'time': 720}},
            'LHR': {'DEL': {'cost': 7000, 'time': 540}, 'DXB': {'cost': 2800, 'time': 420}, 'JFK': {'cost': 5000, 'time': 420}},
            'JFK': {'DXB': {'cost': 9000, 'time': 720}, 'LHR': {'cost': 5000, 'time': 420}, 'LAX': {'cost': 3000, 'time': 380}},
            'LAX': {'JFK': {'cost': 3000, 'time': 380}}
        }
        self.nodes = list(self.graph.keys())
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Air Route Shortest Path Finder", font=("Arial", 16, "bold")).pack(pady=10)

        form = tk.Frame(self.root)
        form.pack(pady=10)

        # Start
        tk.Label(form, text="Start Airport: ", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
        self.start_var = tk.StringVar(value=self.nodes[0])
        ttk.Combobox(form, textvariable=self.start_var, values=self.nodes, state="readonly").grid(row=0, column=1)

        # End
        tk.Label(form, text="Destination Airport: ", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5)
        self.end_var = tk.StringVar(value=self.nodes[1])
        ttk.Combobox(form, textvariable=self.end_var, values=self.nodes, state="readonly").grid(row=1, column=1)

        # Metric choice
        tk.Label(form, text="Optimize By: ", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5)
        self.metric_var = tk.StringVar(value='cost')
        ttk.Combobox(form, textvariable=self.metric_var, values=['cost', 'time'], state="readonly").grid(row=2, column=1)

        # Add custom route
        tk.Label(self.root, text="Add Route: (e.g. DEL-DXB-3000-480)", font=("Arial", 11)).pack()
        self.route_entry = tk.Entry(self.root, width=30)
        self.route_entry.pack(pady=5)
        tk.Button(self.root, text="Add Route", command=self.add_route).pack(pady=5)

        # Find path
        tk.Button(self.root, text="Find Shortest Path", command=self.find_path,
                  font=("Arial", 13), bg="#3498db", fg="white").pack(pady=15)

    def add_route(self):
        try:
            route = self.route_entry.get().strip().upper()
            src, dest, cost, time = route.split("-")
            cost = int(cost)
            time = int(time)

            if src not in self.graph:
                self.graph[src] = {}
            if dest not in self.graph:
                self.graph[dest] = {}

            self.graph[src][dest] = {'cost': cost, 'time': time}
            self.graph[dest][src] = {'cost': cost, 'time': time}

            if src not in self.nodes:
                self.nodes.append(src)
            if dest not in self.nodes:
                self.nodes.append(dest)

            self.start_var.set(src)
            self.end_var.set(dest)

            messagebox.showinfo("Success", f"Route {src} <-> {dest} added!")
            self.route_entry.delete(0, tk.END)
        except:
            messagebox.showerror("Format Error", "Use: SRC-DEST-COST-TIME (e.g. DEL-DXB-3000-480)")

    def find_path(self):
        start = self.start_var.get()
        end = self.end_var.get()
        metric = self.metric_var.get()

        if start == end:
            messagebox.showerror("Invalid Input", "Start and Destination must be different.")
            return

        distances, prev = dijkstra(self.graph, start, metric)
        path = reconstruct_path(prev, start, end)

        if not path:
            messagebox.showerror("No Path", "No available route found.")
            return

        self.display_graph(path, distances[end], metric)

    def display_graph(self, path, value, metric):
        G = nx.Graph()
        for src in self.graph:
            for dst in self.graph[src]:
                label = self.graph[src][dst][metric]
                G.add_edge(src, dst, weight=label)

        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(10, 7))
        title = f"Shortest Path ({metric.upper()}): {' → '.join(path)} = {value}"
        plt.title(title, fontsize=14, fontweight="bold")

        nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightgreen", font_size=12)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))

        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=3)

        plt.tight_layout()
        plt.show()

# --- Launch App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AirRouteApp(root)
    root.mainloop()
