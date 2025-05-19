# # utils.py

# from collections import defaultdict

# def build_graph():
#     from .models import Route

#     graph = defaultdict(list)
#     all_routes = Route.objects.all()

#     for route in all_routes:
#         stop_list = [stop.strip().lower() for stop in route.stops.split(',')]

#         for i in range(len(stop_list) - 1):
#             from_stop = stop_list[i]
#             to_stop = stop_list[i + 1]

#             graph[from_stop].append((to_stop, route.route_number))
#             # graph[to_stop].append((from_stop, route.route_number))  # if bidirectional

#     return graph

# from collections import deque

# def find_route(start, end):
#     graph = build_graph()
#     visited = set()
#     queue = deque()
#     queue.append((start.lower(), [], [], None))  # current, path, routes, current_route

#     while queue:
#         current, path, routes, current_route = queue.popleft()

#         if current == end.lower():
#             return {
#                 'path': path + [current],
#                 'routes': routes
#             }

#         # Use a composite key: (current_node, current_route) or (current_node, tuple(routes))
#         state = (current, current_route.lower() if current_route else None)
#         if state in visited:
#             continue
#         visited.add(state)

#         for neighbor, route in graph.get(current, []):
#             neighbor_state = (neighbor, route.lower())
#             # Only add if not visited with this route context
#             if neighbor_state not in visited:
#                 new_routes = list(routes)
#                 if current_route is None or route.lower() != current_route.lower():
#                     new_routes.append(route)
#                 queue.append((neighbor, path + [current], new_routes, route))
#                 print(f"Visiting: {neighbor}, via route: {route}, routes so far: {new_routes}")

#     return None


from collections import defaultdict
from heapq import heappush, heappop
from .models import Route

def build_graph():
    graph = defaultdict(list)
    all_routes = Route.objects.all()

    for route in all_routes:
        stop_list = [stop.strip().lower() for stop in route.stops.split(',')]
        for i in range(len(stop_list) - 1):
            from_stop = stop_list[i]
            to_stop = stop_list[i + 1]
            graph[from_stop].append((to_stop, route.route_number))
            # graph[to_stop].append((from_stop, route.route_number))  # Uncomment for bidirectional

    return graph

# Simple heuristic: number of steps (for future upgrade: use geolocation for better heuristic)
def heuristic(a, b):
    return 0  # Neutral heuristic for now (acts like Dijkstra)

def find_route(start, end):
    graph = build_graph()
    start = start.lower()
    end = end.lower()

    queue = []
    visited = set()

    # (f_score, current_stop, path, routes_so_far, current_route)
    heappush(queue, (0, start, [], [], None))

    while queue:
        cost, current, path, routes, current_route = heappop(queue)

        if current == end:
            return {
                'path': path + [current],
                'routes': routes
            }

        state = (current, current_route)
        if state in visited:
            continue
        visited.add(state)

        for neighbor, route in graph.get(current, []):
            neighbor = neighbor.lower()
            new_path = path + [current]
            new_routes = list(routes)

            # ✅ Fix route switching logic:
            if current_route is None:
                new_routes.append(route)
            elif route != current_route and (not routes or route != routes[-1]):
                new_routes.append(route)

            total_cost = cost + 1 + heuristic(neighbor, end)
            heappush(queue, (total_cost, neighbor, new_path, new_routes, route))

    return None
