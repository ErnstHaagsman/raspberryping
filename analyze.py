import os
import pwd

import StringIO
from flask import Flask, render_template, make_response

import psycopg2
import psycopg2.extras
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure

app = Flask(__name__)

pg_host = os.environ['PGHOST']
pg_user = os.environ['PGUSER']
pg_pass = os.environ['PGPASSWORD']
pg_db = os.environ['PGDATABASE']


def get_conn():
    return psycopg2.connect(dbname=pg_db, host=pg_host, user=pg_user, password=pg_pass)


@app.route('/')
def index():
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        destination_overview_query = """
            SELECT
              destination,
              min(pingtime),
              round(avg(pingtime), 2) AS avg,
              max(pingtime)
            FROM
              pings
            WHERE
              recorded_at > now() - INTERVAL '1 hour'
            GROUP BY
              destination;
        """

        cur.execute(destination_overview_query)

        destinations = cur.fetchall()

    return render_template('index.html', destinations=destinations)


@app.route('/graphs/<destination>')
def graph(destination):
    with get_conn() as conn:
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

        cur.execute(destination_history_query, (destination,))

        times = cur.fetchall()

    fig = Figure()
    ax = fig.add_subplot(111)

    begin_times = [row['begin_time'] for row in times]

    maxs = [row['max'] for row in times]
    ax.plot_date(
        x=begin_times,
        y=maxs,
        label='max',
        linestyle='solid'
    )

    avgs = [row['avg'] for row in times]
    ax.plot_date(
        x=begin_times,
        y=avgs,
        label='avg',
        linestyle='solid'
    )

    mins = [row['min'] for row in times]
    ax.plot_date(
        x=begin_times,
        y=mins,
        label='min',
        linestyle='solid'
    )

    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))

    ax.set_xlabel('Time')
    ax.set_ylabel('Round Trip (ms)')
    ax.set_ylim(bottom=0)

    ax.legend()

    # Output plot as PNG
    # canvas = FigureCanvasAgg(fig)
    png_output = StringIO.StringIO()

    # canvas.print_png(png_output, transparent=True)
    fig.set_canvas(FigureCanvasAgg(fig))
    fig.savefig(png_output, transparent=True)

    response = make_response(png_output.getvalue())
    response.headers['content-type'] = 'image/png'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
