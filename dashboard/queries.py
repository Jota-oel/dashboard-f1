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
            avg(fv.st_speed) as speed_avg,
            max(fv.st_speed) as speed_max,
            min(fv.st_speed) as speed_min,
            std(fv.st_speed) as speed_std,
            sum(fv.lap_duration)/60 as duration_sum, 
            avg(fv.lap_duration) as duration_avg,
            max(fv.lap_duration) as duration_max,
            min(fv.lap_duration) as duration_min,
            std(fv.lap_duration) as duration_std
        from fact_vuelta fv
        join dim_piloto dp on dp.piloto_key = fv.piloto_key
        where fv.sesion_key = %s
        group by fv.piloto_key
        order by dp.full_name;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [session_key])
        return dict_fetch_all(cursor) 

def get_race_result_info(session_key):
    sql = """
        select
	        dp.full_name as driver_name,
	        frs.number_of_laps as total_laps,
	        frs.session_total_duration/60 as total_duration,
	        frs.gap_to_leader as gap_to_leader,
	        frs.position as position,
	        frs.dnf as dnf,
	        frs.dns as dns,
	        frs.dsq as dsq
        from fact_resultado_sesion frs
        join dim_tiempo dt on dt.tiempo_key = frs.tiempo_key
        join dim_piloto dp on dp.piloto_key = frs.piloto_key
        join dim_reunion dr on dr.reunion_key = frs.reunion_key
        where frs.sesion_key = %s
        group by frs.piloto_key
        order by dp.full_name;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [session_key])
        return dict_fetch_all(cursor) 

def get_driver_performance(time_frame='year'):
    """
    Fetch aggregated driver performance based on time granularity.
    Supported time_frame: 'all', 'year', 'quarter', 'month'
    """
    # Safe mapping for dynamic grouping
    time_frame_mapping = {
        'all': {
            'select': "'Career' AS time_period",
            'group_by': "p.piloto_key, p.full_name",
            'order_by': "p.full_name ASC"
        },
        'year': {
            'select': "CAST(dt.anio AS CHAR) AS time_period",
            'group_by': "dt.anio, p.piloto_key, p.full_name",
            'order_by': "dt.anio ASC, p.full_name ASC"
        },
        'quarter': {
            'select': "CONCAT(dt.anio, ' Q', dt.trimestre) AS time_period",
            'group_by': "dt.anio, dt.trimestre, p.piloto_key, p.full_name",
            'order_by': "dt.anio ASC, dt.trimestre ASC, p.full_name ASC"
        },
        'month': {
            'select': "CONCAT(dt.anio, '-', LPAD(dt.mes, 2, '0')) AS time_period",
            'group_by': "dt.anio, dt.mes, p.piloto_key, p.full_name",
            'order_by': "dt.anio ASC, dt.mes ASC, p.full_name ASC"
        }
    }

    config = time_frame_mapping.get(time_frame, time_frame_mapping['year'])

    sql = f"""
        SELECT 
            p.full_name AS driver_name,
            {config['select']},
            SUM(frs.number_of_laps) AS total_laps,
            ROUND(SUM(frs.session_total_duration) / 3600.0, 2) AS total_hours,
            ROUND(AVG(frs.gap_to_leader), 3) AS gap_avg,
            ROUND(STD(frs.gap_to_leader), 3) AS gap_std,
            ROUND(AVG(frs.position), 2) AS pos_avg,
            ROUND(STD(frs.position), 2) AS pos_std,
            SUM(frs.points) AS total_points,
            ROUND(AVG(frs.points), 2) AS points_avg,
            ROUND(STD(frs.points), 2) AS points_std,
            SUM(frs.dnf) AS total_dnf,
            SUM(frs.dns) AS total_dns,
            SUM(frs.dsq) AS total_dsq,
            SUM(frs.dnf) + SUM(frs.dns) + SUM(frs.dsq) AS total_out,
            COUNT(frs.sesion_key) - (SUM(frs.dnf) + SUM(frs.dns) + SUM(frs.dsq)) AS sessions_count
        FROM dw_formula1.fact_resultado_sesion frs
        JOIN dw_formula1.dim_tiempo dt ON dt.tiempo_key = frs.tiempo_key
        JOIN dw_formula1.dim_piloto p ON p.piloto_key = frs.piloto_key
        JOIN dw_formula1.dim_sesion ds ON ds.sesion_key = frs.sesion_key
        WHERE ds.session_type = 'Race'
        GROUP BY {config['group_by']}
        ORDER BY {config['order_by']};
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        return dict_fetch_all(cursor)

def get_driver_info(driver_key):
    sql = """
        SELECT
            dp.full_name AS full_name,
            dr.circuit_short_name AS circuit,
            dt.fecha AS time_period,
            frs.`position` AS `position`,
            frs.number_of_laps AS laps,
            frs.gap_to_leader AS gap,
            frs.points AS points,
	        (frs.points > 25) as fast_lap
        FROM dw_formula1.fact_resultado_sesion frs 
        JOIN dw_formula1.dim_piloto dp ON dp.piloto_key = frs.piloto_key 
        JOIN dw_formula1.dim_reunion dr ON dr.reunion_key = frs.reunion_key
        JOIN dw_formula1.dim_tiempo dt ON dt.tiempo_key = frs.tiempo_key
        JOIN dw_formula1.dim_sesion ds ON ds.sesion_key = frs.sesion_key
        WHERE 
            frs.piloto_key = %s
            AND ds.session_type = 'Race'
        ORDER BY dt.fecha DESC;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [driver_key])
        return dict_fetch_all(cursor) 

