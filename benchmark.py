import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine
import pandas as pd


def get_with_pandas():

    engine = create_engine('postgres:///pi')

    with engine.connect() as conn, conn.begin():

        data = pd.read_sql_query("select recorded_at, pingtime from pings where recorded_at > now() - interval "
                                 "'3 hours' and "
                                 "destination='jetbrains.com'; ", conn)

    engine.dispose()

    df = data.set_index(pd.DatetimeIndex(data['recorded_at']))

    # We have this information in the index now, so let's drop it
    del df['recorded_at']

    return df.resample('10T').agg(['min', 'mean', 'max'])


def get_with_sql():
    with psycopg2.connect('') as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        destination_history_query = """
            WITH intervals AS (
                SELECT
                  begin_time,
                  LEAD(begin_time)
                  OVER (
                    ORDER BY begin_time ) AS end_time
                FROM
                      generate_series(
                          now() - INTERVAL '3 hours',
                          now(),
                          INTERVAL '10 minutes'
                      ) begin_time
            )
            SELECT
              i.begin_time AT TIME ZONE 'Europe/Berlin' AS begin_time,
              i.end_time AT TIME ZONE 'Europe/Berlin' AS end_time,
              p.destination,
              count(p.pingtime),
              round(avg(p.pingtime),2) AS avg,
              max(p.pingtime),
              min(p.pingtime)
            FROM intervals i LEFT JOIN pings p
            ON p.recorded_at >= i.begin_time AND
              p.recorded_at < i.end_time
            WHERE 
              i.end_time IS NOT NULL
              AND destination = %s
            GROUP BY i.begin_time, i.end_time, p.destination
            ORDER BY i.begin_time ASC;        
        """

        cur.execute(destination_history_query, ('jetbrains.com',))

        times = cur.fetchall()

    return times