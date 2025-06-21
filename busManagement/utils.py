
# from django.http import JsonResponse
# from django.shortcuts import render
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

# def find_indirect_route(start, end):
#     start = start.strip().lower()
#     end = end.strip().lower()

#     routes = Route.objects.all()
#     stop_to_routes = defaultdict(list)
#     route_to_stops = {}

#     for route in routes:
#         stop_list = [stop.strip().lower() for stop in route.stops.split(',')]
#         route_to_stops[route.route_number] = stop_list
#         for stop in stop_list:
#             stop_to_routes[stop].append(route.route_number)

#     # ✅ First, check if direct route exists
#     direct_routes = [
#         route_num for route_num, stops in route_to_stops.items()
#         if start in stops and end in stops and stops.index(start) < stops.index(end)
#     ]

#     if direct_routes:
#         direct_route = direct_routes[0]
#         stops = route_to_stops[direct_route]
#         path = stops[stops.index(start):stops.index(end)+1]
#         return {
#             'path': path,
#             'routes': [direct_route]
#         }

#     # ✅ Check for 1-transfer indirect routes
#     for route1 in stop_to_routes[start]:
#         for route2 in stop_to_routes[end]:
#             if route1 == route2:
#                 continue

#             # Look for a common stop (transfer point) between route1 and route2
#             stops1 = route_to_stops[route1]
#             stops2 = route_to_stops[route2]
#             transfer_stops = set(stops1) & set(stops2)

#             for transfer in transfer_stops:
#                 if (stops1.index(start) < stops1.index(transfer) and
#                     stops2.index(transfer) < stops2.index(end)):
#                     path1 = stops1[stops1.index(start):stops1.index(transfer)+1]
#                     path2 = stops2[stops2.index(transfer)+1:stops2.index(end)+1]
#                     return {
#                         'path': path1 + path2,
#                         'routes': [route1, route2],
#                         'transfer_point': transfer
#                     }

#     return None  # No indirect route found

# def route_view(request):

#     if request.method == 'POST':
#         start_location = request.POST.get('start_location', '').strip().lower()
#         stop = request.POST.get('stop', '').strip().lower()

#         if not start_location or not stop:
#             return JsonResponse({'error': 'Start and end stops are required'}, status=400)

#         result = find_indirect_route(start_location, stop)

#         if not result:
#             return JsonResponse({'message': 'No route found'}, status=404)

#         return JsonResponse(result)

#     # GET request — render the page with default route data
#     routes = Route.objects.all()
#     return render(request, 'bus_filter.html', {
#         'routes': routes
#     })
from django.http import JsonResponse
from django.shortcuts import render
from collections import defaultdict
from .models import Route

def find_shortest_indirect_route(start, end):
    """Find the shortest indirect route between two stops that are not directly connected"""
    start = start.strip().lower()
    end = end.strip().lower()

    routes = Route.objects.all()
    stop_to_routes = defaultdict(list)
    route_to_stops = {}

    # Build mappings
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
        return None  # Return None for direct routes - we only want indirect routes

    # ✅ Find all possible indirect routes with transfers
    all_indirect_routes = []

    # Check 1-transfer routes
    for route1 in stop_to_routes[start]:
        stops1 = route_to_stops[route1]
        start_idx = stops1.index(start)
        
        for route2 in stop_to_routes[end]:
            if route1 == route2:
                continue
                
            stops2 = route_to_stops[route2]
            end_idx = stops2.index(end)
            
            # Find common stops (potential transfer points)
            transfer_stops = set(stops1) & set(stops2)
            
            for transfer in transfer_stops:
                transfer_idx1 = stops1.index(transfer)
                transfer_idx2 = stops2.index(transfer)
                
                # Check if transfer is reachable in correct direction
                if start_idx < transfer_idx1 and transfer_idx2 < end_idx:
                    path1 = stops1[start_idx:transfer_idx1 + 1]
                    path2 = stops2[transfer_idx2 + 1:end_idx + 1]
                    total_path = path1 + path2
                    
                    route_info = {
                        'path': total_path,
                        'routes': [route1, route2],
                        'transfer_point': transfer,
                        'total_stops': len(total_path),
                        'segments': [
                            {
                                'route': route1,
                                'from': start,
                                'to': transfer,
                                'stops': path1
                            },
                            {
                                'route': route2,
                                'from': transfer,
                                'to': end,
                                'stops': path2
                            }
                        ]
                    }
                    all_indirect_routes.append(route_info)

    # Check 2-transfer routes if no 1-transfer route found
    if not all_indirect_routes:
        all_indirect_routes.extend(find_two_transfer_routes(start, end, stop_to_routes, route_to_stops))

    # Return the shortest route (minimum total stops)
    if all_indirect_routes:
        shortest_route = min(all_indirect_routes, key=lambda x: x['total_stops'])
        return shortest_route

    return None

def find_two_transfer_routes(start, end, stop_to_routes, route_to_stops):
    """Find routes with exactly 2 transfers"""
    two_transfer_routes = []
    
    # Get all routes from start
    for route1 in stop_to_routes[start]:
        stops1 = route_to_stops[route1]
        start_idx = stops1.index(start)
        
        # For each possible first transfer point on route1
        for i in range(start_idx + 1, len(stops1)):
            transfer1 = stops1[i]
            
            # Find routes that pass through first transfer point
            for route2 in stop_to_routes[transfer1]:
                if route2 == route1:
                    continue
                    
                stops2 = route_to_stops[route2]
                transfer1_idx2 = stops2.index(transfer1)
                
                # For each possible second transfer point on route2
                for j in range(transfer1_idx2 + 1, len(stops2)):
                    transfer2 = stops2[j]
                    
                    # Find routes that go from second transfer to end
                    for route3 in stop_to_routes[transfer2]:
                        if route3 == route2 or route3 == route1:
                            continue
                            
                        if end in stop_to_routes[transfer2] and route3 in stop_to_routes[end]:
                            stops3 = route_to_stops[route3]
                            transfer2_idx3 = stops3.index(transfer2)
                            end_idx = stops3.index(end)
                            
                            if transfer2_idx3 < end_idx:
                                path1 = stops1[start_idx:stops1.index(transfer1) + 1]
                                path2 = stops2[transfer1_idx2 + 1:stops2.index(transfer2) + 1]
                                path3 = stops3[transfer2_idx3 + 1:end_idx + 1]
                                total_path = path1 + path2 + path3
                                
                                route_info = {
                                    'path': total_path,
                                    'routes': [route1, route2, route3],
                                    'transfer_points': [transfer1, transfer2],
                                    'total_stops': len(total_path),
                                    'segments': [
                                        {
                                            'route': route1,
                                            'from': start,
                                            'to': transfer1,
                                            'stops': path1
                                        },
                                        {
                                            'route': route2,
                                            'from': transfer1,
                                            'to': transfer2,
                                            'stops': path2
                                        },
                                        {
                                            'route': route3,
                                            'from': transfer2,
                                            'to': end,
                                            'stops': path3
                                        }
                                    ]
                                }
                                two_transfer_routes.append(route_info)
    
    return two_transfer_routes

def get_all_indirect_routes(start, end):
    """Get all possible indirect routes sorted by efficiency"""
    result = find_shortest_indirect_route(start, end)
    if not result:
        return None
    
    # You can extend this to return multiple routes if needed
    return result

def route_view(request):
    if request.method == 'POST':
        start_location = request.POST.get('start_location', '').strip().lower()
        stop = request.POST.get('stop', '').strip().lower()

        if not start_location or not stop:
            return JsonResponse({'error': 'Start and end stops are required'}, status=400)

        # Check if direct route exists first
        routes = Route.objects.all()
        route_to_stops = {}
        
        for route in routes:
            stop_list = [stop.strip().lower() for stop in route.stops.split(',')]
            route_to_stops[route.route_number] = stop_list

        # Check for direct routes
        direct_routes = [
            route_num for route_num, stops in route_to_stops.items()
            if start_location in stops and stop in stops and stops.index(start_location) < stops.index(stop)
        ]

        if direct_routes:
            # Direct route exists
            direct_route = direct_routes[0]
            stops = route_to_stops[direct_route]
            path = stops[stops.index(start_location):stops.index(stop) + 1]
            
            return JsonResponse({
                'type': 'direct',
                'message': 'Direct route available',
                'path': path,
                'routes': [direct_route],
                'total_stops': len(path)
            })

        # Find indirect route
        result = find_shortest_indirect_route(start_location, stop)

        if not result:
            return JsonResponse({'message': 'No indirect route found'}, status=404)

        result['type'] = 'indirect'
        result['message'] = f'Indirect route with {len(result["routes"])-1} transfer(s)'
        
        return JsonResponse(result)

    # GET request — render the page with default route data
    routes = Route.objects.all()
    return render(request, 'bus_filter.html', {
        'routes': routes
    })