from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.index_view, name='index'),
    path('race/', views.race_view_laps, name='race_view_laps'),
    path('results/', views.race_view_results, name='race_view_results'),

    # API Endpoints
    path('api/standings/<int:year>/', views.api_championship_standings, name='api_standings'),
    path('api/race-pace/lap-duration/<int:session_key>/', views.api_race_pace, name='api_race_pace_lap_duration'),
    path('api/race-pace/st-speed/<int:session_key>/', views.api_race_st_speed, name='api_race_pace_st_speed'),
    path('api/results/<int:session_key>/', views.api_session_results, name='api_session_results'),
    path('api/circuit-date/', views.api_circuit_date, name="api_circuit_date"),
    path('api/race-pace/info/<int:session_key>/', views.api_race_pace_info, name="api_race_info"),
    path('api/race-result/info/<int:session_key>/', views.api_race_result_info, name="api_result_info"),
    path('api/driver-performance/', views.api_driver_performance, name="driver_performance"),
]
