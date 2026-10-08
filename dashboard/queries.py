from django.db import connection

def dict_fetch_all(cursor):
    """Return all rows from a cursor as a list of dictionaries."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_championship_standings(year):
    """
    Fetch driver standings and total accumulated points for a given year.
    """
    sql = """
        SELECT 
            p.full_name AS driver_name,
            p.team_name AS team_name,
            SUM(frs.points) AS total_points
        FROM fact_resultado_sesion frs
        JOIN dim_piloto p ON frs.piloto_key = p.piloto_key
        JOIN dim_tiempo t ON frs.tiempo_key = t.tiempo_key
        WHERE t.anio = %s
        GROUP BY p.piloto_key, p.full_name, p.team_name
        ORDER BY total_points DESC;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [year])
        return dict_fetch_all(cursor)

def get_race_pace(session_key):
    """
    Fetch lap times per driver for a specific race session.
    Excludes pit exit laps and null duration entries.
    """
    sql = """
        SELECT 
            p.full_name AS driver_name,
            p.team_name AS team_name,
            fv.lap_number AS lap_number,
            fv.lap_duration AS lap_duration_seconds
        FROM fact_vuelta fv
        JOIN dim_piloto p ON fv.piloto_key = p.piloto_key
        WHERE fv.sesion_key = %s 
        ORDER BY fv.lap_number, p.full_name;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [session_key])
        return dict_fetch_all(cursor)

def get_session_results(session_key):
    """
    Fetch race results for a specific session.
    """
    sql = """
        SELECT 
            frs.position AS position,
            p.full_name AS driver_name,
            p.team_name AS team_name,
            frs.points AS points,
            frs.number_of_laps AS laps_completed,
            frs.dnf AS dnf,
            frs.dns AS dns,
            frs.dsq AS dsq
        FROM fact_resultado_sesion frs
        JOIN dim_piloto p ON frs.piloto_key = p.piloto_key
        WHERE frs.sesion_key = %s
        ORDER BY frs.position ASC;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [session_key])
        return dict_fetch_all(cursor)

def get_circuit_session_date():
    sql = """
        select distinct 
	        dr.circuit_short_name, 
	        frs.sesion_key, 
	        dt.fecha 
        from fact_resultado_sesion frs
        join dim_reunion dr on dr.reunion_key = frs.reunion_key
        join dim_tiempo dt on dt.tiempo_key = frs.tiempo_key
        where frs.sesion_key in (
	        select sesion_key from dim_sesion
	        where session_type = 'Race'
        );
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return dict_fetch_all(cursor)

def get_race_st_speed(session_key):
    sql = """
        select
            p.full_name AS driver_name,
            p.team_name AS team_name,
            fv.lap_number AS lap_number,
            fv.st_speed AS standard_speed
        FROM fact_vuelta fv
        JOIN dim_piloto p ON fv.piloto_key = p.piloto_key
        where fv.sesion_key = %s
        order by fv.lap_number, p.full_name;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [session_key])
        return dict_fetch_all(cursor)

def get_race_pace_info(session_key):
    sql = """
        select
            dp.full_name as driver_name,
            avg(fv.st_speed) as avg_speed,
            max(fv.st_speed) as max_speed,
            min(fv.st_speed) as min_speed,
            std(fv.st_speed) as std_speed,
            avg(fv.lap_duration) as avg_duration,
            max(fv.lap_duration) as max_duration,
            min(fv.lap_duration) as min_duration,
            std(fv.lap_duration) as std_duration
        from fact_vuelta fv
        join dim_piloto dp on dp.piloto_key = fv.piloto_key
        where fv.sesion_key = %s
        group by fv.piloto_key;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [session_key])
        return dict_fetch_all(cursor) 

