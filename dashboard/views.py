from django.shortcuts import render
from django.http import JsonResponse
from .queries import (
    get_championship_standings, 
    get_race_pace, 
    get_session_results,
    get_circuit_session_date,
    get_race_st_speed,
    get_race_pace_info,
    get_race_result_info,
    get_driver_performance,
    get_driver_info,
)

def index_view(request):
    """Render main dashboard home page."""
    return render(request, 'dashboard/index.html')

def race_view_laps(request):
    """Render to see indicators of fact laps"""
    return render(request, 'dashboard/race-pace.html')

def race_view_results(request):
    """Render to see indicators of fact results"""
    return render(request, 'dashboard/session-results.html')

def api_championship_standings(request, year):
    """API endpoint for drivers championship standings."""
    data = get_championship_standings(year)
    return JsonResponse({'status': 'success', 'data': data})

def api_race_pace(request, session_key):
    """API endpoint for lap times in a specific session."""
    data = get_race_pace(session_key)
    return JsonResponse({'status': 'success', 'data': data})

def api_race_st_speed(request, session_key):
    """API endpoint for lap standard speed in a specific session."""
    data = get_race_st_speed(session_key)
    return JsonResponse({'status': 'success', 'data': data})

def api_session_results(request, session_key):
    """API endpoint for overall session classification."""
    data = get_session_results(session_key)
    return JsonResponse({'status': 'success', 'data': data})

def api_circuit_date(request):
    """API endpoint for overall session_key with circuit_name and date"""
    data = get_circuit_session_date() 
    return JsonResponse({'status': 'success', 'data': data})

def api_race_pace_info(request, session_key):
    """API endpoint for info to standard speed and lap duration in a specific session"""
    data = get_race_pace_info(session_key)
    return JsonResponse({'status': 'success', 'data': data})

def api_race_result_info(request, session_key):
    """API endpoint for info to session result in a specific session"""
    data = get_race_result_info(session_key)
    return JsonResponse({'status': 'success', 'data': data})

def api_driver_info(request, driver_key):
    """API endpoint for info to driver"""
    data = get_driver_info(driver_key)
    return JsonResponse({'status': 'success', 'data': data})
    
def api_driver_performance(request):
    """
    API endpoint for driver performance aggregated metrics.
    Accepts query parameter 'time_frame': 'year', 'quarter', 'month', 'all'
    """
    valid_time_frames = ['year', 'quarter', 'month', 'all']
    time_frame = request.GET.get('time_frame', 'year')
    
    # Fallback to 'year' if an invalid time_frame is passed
    if time_frame not in valid_time_frames:
        time_frame = 'year'
        
    data = get_driver_performance(time_frame)
    return JsonResponse({'status': 'success', 'data': data})


