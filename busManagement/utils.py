
from django.http import JsonResponse
from django.shortcuts import render
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

def find_indirect_route(start, end):
    start = start.strip().lower()
    end = end.strip().lower()

    routes = Route.objects.all()
    stop_to_routes = defaultdict(list)
    route_to_stops = {}

    for route in routes:
        stop_list = [stop.strip().lower() for stop in route.stops.split(',')]
        route_to_stops[route.route_number] = stop_list
        for stop in stop_list:
            stop_to_routes[stop].append(route.route_number)

    # ✅ First, check if direct route exists
    direct_routes = [
        route_num for route_num, stops in route_to_stops.items()
        if start in stops and end in stops and stops.index(start) < stops.index(end)
    ]

    if direct_routes:
        direct_route = direct_routes[0]
        stops = route_to_stops[direct_route]
        path = stops[stops.index(start):stops.index(end)+1]
        return {
            'path': path,
            'routes': [direct_route]
        }

    # ✅ Check for 1-transfer indirect routes
    for route1 in stop_to_routes[start]:
        for route2 in stop_to_routes[end]:
            if route1 == route2:
                continue

            # Look for a common stop (transfer point) between route1 and route2
            stops1 = route_to_stops[route1]
            stops2 = route_to_stops[route2]
            transfer_stops = set(stops1) & set(stops2)

            for transfer in transfer_stops:
                if (stops1.index(start) < stops1.index(transfer) and
                    stops2.index(transfer) < stops2.index(end)):
                    path1 = stops1[stops1.index(start):stops1.index(transfer)+1]
                    path2 = stops2[stops2.index(transfer)+1:stops2.index(end)+1]
                    return {
                        'path': path1 + path2,
                        'routes': [route1, route2],
                        'transfer_point': transfer
                    }

    return None  # No indirect route found

def route_view(request):

    if request.method == 'POST':
        start_location = request.POST.get('start_location', '').strip().lower()
        stop = request.POST.get('stop', '').strip().lower()

        if not start_location or not stop:
            return JsonResponse({'error': 'Start and end stops are required'}, status=400)

        result = find_indirect_route(start_location, stop)

        if not result:
            return JsonResponse({'message': 'No route found'}, status=404)

        return JsonResponse(result)

    # GET request — render the page with default route data
    routes = Route.objects.all()
    return render(request, 'bus_filter.html', {
        'routes': routes
    })