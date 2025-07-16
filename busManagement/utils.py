from django.http import JsonResponse
from django.shortcuts import render
from collections import defaultdict
from .models import Route, Bus

def get_buses_for_route(route_number):
    """Get all available buses for a specific route with detailed information, sorted by departure time"""
    try:
        route = Route.objects.get(route_number=route_number)
        buses = Bus.objects.filter(route=route).select_related('driver').order_by('departure_time')
        
        bus_list = []
        for bus in buses:
            bus_info = {
                'bus_id': bus.id,
                'bus_number': bus.bus_number,
                'status': getattr(bus, 'status', 'active'),
                'route_number': route_number,
                # 'route_name': route.route_name, 
                'departure_time': bus.departure_time.strftime('%H:%M') if bus.departure_time else 'Not Set',
            }
            
            # Add additional fields if they exist in your Bus model
            if hasattr(bus, 'driver') and bus.driver:
                bus_info['driver_name'] = bus.driver.name
            if hasattr(bus, 'capacity'):
                bus_info['capacity'] = bus.capacity
            if hasattr(bus, 'current_location'):
                bus_info['current_location'] = bus.current_location
            if hasattr(bus, 'next_arrival_time'):
                bus_info['next_arrival_time'] = str(bus.next_arrival_time)
                
            bus_list.append(bus_info)
            
        print(f"Found {len(bus_list)} buses for route {route_number}")
        return bus_list
    except Route.DoesNotExist:
        return []

def get_active_buses_only(route_number):
    """Get only active/operational buses for a route"""
    try:
        route = Route.objects.get(route_number=route_number)
        # Filter for active buses only
        buses = Bus.objects.filter(route=route)
        
        # If your Bus model has a status field, filter by it
        if hasattr(Bus, 'status'):
            buses = buses.filter(status='active')  # or whatever your active status value is
            
        return [{'bus_id': bus.id, 'bus_number': bus.bus_number, 'status': getattr(bus, 'status', 'active')} for bus in buses]
    except Route.DoesNotExist:
        return []

def find_shortest_indirect_route_with_buses(start, end):
    """Find the shortest direct or indirect route with bus availability information"""
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

    # ✅ Try direct route first
    direct_routes = []
    for route_num, stops in route_to_stops.items():
        if start in stops and end in stops and stops.index(start) < stops.index(end):
            direct_routes.append(route_num)

    if direct_routes:
        all_buses = []
        segments = []

        for route_num in direct_routes:
            stops = route_to_stops[route_num]
            path = stops[stops.index(start):stops.index(end) + 1]
            buses = get_buses_for_route(route_num)
            print(f"Direct route {route_num} has {len(buses)} buses")

            all_buses.extend(buses)
            segments.append({
                'route': route_num,
                'from': start,
                'to': end,
                'stops': path,
                'buses': buses
            })

        print(f"Total buses for direct routes: {len(all_buses)}")
        return {
            'type': 'direct',
            'path': [start, end],
            'routes': direct_routes,
            'start': start,
            'end': end,
            'transfer_points': [],
            'total_stops': len(route_to_stops[direct_routes[0]]),
            'buses': all_buses,
            'segments': segments
        }

    # ✅ Try indirect route with one transfer first
    print(f"No direct routes found. Trying one transfer routes...")
    one_transfer_routes = find_one_transfer_routes_with_buses(start, end, stop_to_routes, route_to_stops)
    print(f"Found {len(one_transfer_routes)} one-transfer routes")
    
    if one_transfer_routes:
        # Return the route with the fewest total stops
        best_route = sorted(one_transfer_routes, key=lambda r: r['total_stops'])[0]
        
        # Debug: Print segment information
        total_buses = 0
        for i, segment in enumerate(best_route['segments']):
            print(f"Segment {i+1}: Route {segment['route']} has {len(segment['buses'])} buses")
            total_buses += len(segment['buses'])
        print(f"Total buses across all segments: {total_buses}")
        
        return {
            'type': 'indirect',
            'path': best_route['path'],
            'routes': best_route['routes'],
            'start': start,
            'end': end,
            'transfer_points': best_route['transfer_points'],
            'total_stops': best_route['total_stops'],
            'buses': [bus for seg in best_route['segments'] for bus in seg['buses']],  # Keep for backward compatibility
            'segments': best_route['segments']  # This is what the template actually uses
        }

    # ✅ Try indirect route with two transfers
    print(f"No one-transfer routes found. Trying two transfer routes...")
    two_transfer_routes = find_two_transfer_routes_with_buses(start, end, stop_to_routes, route_to_stops)
    print(f"Found {len(two_transfer_routes)} two-transfer routes")

    if two_transfer_routes:
        # Return the route with the fewest total stops
        best_route = sorted(two_transfer_routes, key=lambda r: r['total_stops'])[0]
        return {
            'type': 'indirect',
            'path': best_route['path'],
            'routes': best_route['routes'],
            'start': start,
            'end': end,
            'transfer_points': best_route['transfer_points'],
            'total_stops': best_route['total_stops'],
            'buses': [bus for seg in best_route['segments'] for bus in seg['buses']],  # Keep for backward compatibility
            'segments': best_route['segments']  # This is what the template actually uses
        }

    # ❌ No route found
    print(f"No routes found between {start} and {end}")
    return None

def find_one_transfer_routes_with_buses(start, end, stop_to_routes, route_to_stops):
    """Find routes with exactly 1 transfer including bus information"""
    print(f"Looking for one-transfer routes from {start} to {end}")
    print(f"Routes serving {start}: {stop_to_routes.get(start, [])}")
    print(f"Routes serving {end}: {stop_to_routes.get(end, [])}")
    
    one_transfer_routes = []
    
    # Get all routes from start
    for route1 in stop_to_routes[start]:
        stops1 = route_to_stops[route1]
        start_idx = stops1.index(start)
        print(f"Checking route {route1}, stops: {stops1}")
        
        # For each possible transfer point on route1
        for i in range(start_idx + 1, len(stops1)):
            transfer_point = stops1[i]
            print(f"  Checking transfer point: {transfer_point}")
            
            # Find routes that pass through transfer point and go to end
            for route2 in stop_to_routes[transfer_point]:
                if route2 == route1:
                    continue
                    
                stops2 = route_to_stops[route2]
                print(f"    Checking route {route2} from transfer: {stops2}")
                if end in stops2:
                    transfer_idx2 = stops2.index(transfer_point)
                    end_idx = stops2.index(end)
                    print(f"      Transfer at index {transfer_idx2}, end at index {end_idx}")
                    
                    # Check if transfer point comes before destination on route2
                    if transfer_idx2 < end_idx:
                        print(f"      FOUND valid one-transfer route: {route1} -> {route2}")
                        path1 = stops1[start_idx:stops1.index(transfer_point) + 1]
                        path2 = stops2[transfer_idx2 + 1:end_idx + 1]
                        total_path = path1 + path2
                        
                        # Get buses for both routes
                        buses1 = get_buses_for_route(route1)
                        buses2 = get_buses_for_route(route2)
                        
                        print(f"        Route {route1} has {len(buses1)} buses")
                        print(f"        Route {route2} has {len(buses2)} buses")
                        
                        route_info = {
                            'path': total_path,
                            'routes': [route1, route2],
                            'transfer_points': [transfer_point],
                            'total_stops': len(total_path),
                            'total_buses': len(buses1) + len(buses2),
                            'segments': [
                                {
                                    'route': route1,
                                    'from': start,
                                    'to': transfer_point,
                                    'stops': path1,
                                    'buses': buses1,
                                    'bus_count': len(buses1)
                                },
                                {
                                    'route': route2,
                                    'from': transfer_point,
                                    'to': end,
                                    'stops': path2,
                                    'buses': buses2,
                                    'bus_count': len(buses2)
                                }
                            ]
                        }
                        one_transfer_routes.append(route_info)
    
    print(f"Total one-transfer routes found: {len(one_transfer_routes)}")
    return one_transfer_routes

def find_two_transfer_routes_with_buses(start, end, stop_to_routes, route_to_stops):
    """Find routes with exactly 2 transfers including bus information"""
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
                            
                        if end in route_to_stops[route3]:
                            stops3 = route_to_stops[route3]
                            transfer2_idx3 = stops3.index(transfer2)
                            end_idx = stops3.index(end)
                            
                            if transfer2_idx3 < end_idx:
                                path1 = stops1[start_idx:stops1.index(transfer1) + 1]
                                path2 = stops2[transfer1_idx2 + 1:stops2.index(transfer2) + 1]
                                path3 = stops3[transfer2_idx3 + 1:end_idx + 1]
                                total_path = path1 + path2 + path3
                                
                                # Get buses for all three routes
                                buses1 = get_buses_for_route(route1)
                                buses2 = get_buses_for_route(route2)
                                buses3 = get_buses_for_route(route3)
                                
                                route_info = {
                                    'path': total_path,
                                    'routes': [route1, route2, route3],
                                    'transfer_points': [transfer1, transfer2],
                                    'total_stops': len(total_path),
                                    'total_buses': len(buses1) + len(buses2) + len(buses3),
                                    'segments': [
                                        {
                                            'route': route1,
                                            'from': start,
                                            'to': transfer1,
                                            'stops': path1,
                                            'buses': buses1,
                                            'bus_count': len(buses1)
                                        },
                                        {
                                            'route': route2,
                                            'from': transfer1,
                                            'to': transfer2,
                                            'stops': path2,
                                            'buses': buses2,
                                            'bus_count': len(buses2)
                                        },
                                        {
                                            'route': route3,
                                            'from': transfer2,
                                            'to': end,
                                            'stops': path3,
                                            'buses': buses3,
                                            'bus_count': len(buses3)
                                        }
                                    ]
                                }
                                two_transfer_routes.append(route_info)
    
    return two_transfer_routes

def available_buses_for_direct_route(request):
    """Your original function for direct routes"""
    buses = []
    matching_routes = []

    if request.method == 'POST':
        start_location = request.POST.get('start_location', '').strip().lower()
        stop = request.POST.get('stop', '').strip().lower()

        if start_location and stop:
            for route in Route.objects.all():
                route_stops = [s.strip().lower() for s in route.stops.split(',') if s.strip()]

                if start_location in route_stops and stop in route_stops:
                    if route_stops.index(start_location) < route_stops.index(stop):
                        matching_routes.append(route)

            buses = Bus.objects.filter(route__in=matching_routes)
            # print(f"Found {len(buses)} buses for routes: {[bus.bus_number for bus in buses]}")
        else:
            return JsonResponse({'error': 'Both start and end locations are required'}, status=400)

    return render(request, 'route_view.html', {
        'buses': buses,
        'routes': matching_routes
    })

def route_view(request):
    """Enhanced route view with bus availability"""
    if request.method == 'POST':
        start_location = request.POST.get('start_location', '').strip().lower()
        stop = request.POST.get('stop', '').strip().lower()

        if not start_location or not stop:
            return JsonResponse({'error': 'Start and end stops are required'}, status=400)

        result = find_shortest_indirect_route_with_buses(start_location, stop)
        
        if not result:
            return JsonResponse({'error': 'No route found'}, status=404)
        # print(result)
        return render(request, 'route_view.html', {'result': result})
    
    # If GET request, just render empty form
    return render(request, 'route_view.html')
