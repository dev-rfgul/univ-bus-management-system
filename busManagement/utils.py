

# from collections import defaultdict
# from heapq import heappush, heappop
# from .models import Route

# def build_graph():
#     graph = defaultdict(list)
#     all_routes = Route.objects.all()

#     for route in all_routes:
#         stop_list = [stop.strip().lower() for stop in route.stops.split(',')]
#         for i in range(len(stop_list) - 1):
#             from_stop = stop_list[i]
#             to_stop = stop_list[i + 1]
#             graph[from_stop].append((to_stop, route.route_number))
#             # graph[to_stop].append((from_stop, route.route_number))  # Uncomment for bidirectional

#     return graph

# # Simple heuristic: number of steps (for future upgrade: use geolocation for better heuristic)
# def heuristic(a, b):
#     return 0  # Neutral heuristic for now (acts like Dijkstra)

# def find_route(start, end):
#     graph = build_graph()
#     start = start.lower()
#     end = end.lower()

#     queue = []
#     visited = set()

#     # (f_score, current_stop, path, routes_so_far, current_route)
#     heappush(queue, (0, start, [], [], None))

#     while queue:
#         cost, current, path, routes, current_route = heappop(queue)

#         if current == end:
#             return {
#                 'path': path + [current],
#                 'routes': routes
#             }

#         state = (current, current_route)
#         if state in visited:
#             continue
#         visited.add(state)

#         for neighbor, route in graph.get(current, []):
#             neighbor = neighbor.lower()
#             new_path = path + [current]
#             new_routes = list(routes)

#             # ✅ Fix route switching logic:
#             if current_route is None:
#                 new_routes.append(route)
#             elif route != current_route and (not routes or route != routes[-1]):
#                 new_routes.append(route)

#             total_cost = cost + 1 + heuristic(neighbor, end)
#             heappush(queue, (total_cost, neighbor, new_path, new_routes, route))

#     return None


# def route_view(request):

#     if request.method == 'POST':
#         start_location = request.POST.get('start_location', '').strip().lower()
#         stop = request.POST.get('stop', '').strip().lower()

#         if not start_location or not stop:
#             return JsonResponse({'error': 'Start and end stops are required'}, status=400)

#         result = find_route(start_location, stop)

#         if not result:
#             return JsonResponse({'message': 'No route found'}, status=404)

#         return JsonResponse(result)

#     # GET request — render the page with default route data
#     routes = Route.objects.all()
#     return render(request, 'bus_filter.html', {
#         'routes': routes
#     })