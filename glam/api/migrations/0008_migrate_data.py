# Generated by Django 3.0.6 on 2020-05-19 20:31

from django.db import migrations


DATA = [
    {"channel": "nightly", "versions": "'75', '74', '73'"},
    {"channel": "beta", "versions": "'74', '73', '72'"},
    {"channel": "release", "versions": "'73', '72', '71'"},
]

forward_sql_template = """
    INSERT INTO
        glam_desktop_{channel}_aggregation (
            version,
            os,
            build_id,
            process,
            metric,
            metric_key,
            client_agg_type,
            metric_type,
            total_users,
            histogram,
            percentiles
        )

    SELECT
        version,
        os,
        build_id,
        CASE
            WHEN process=1 THEN 'parent'
            WHEN process=2 THEN 'content'
            WHEN process=3 THEN 'gpu'
        END AS process,
        metric,
        metric_key,
        client_agg_type,
        metric_type,
        total_users,
        MAX(CASE WHEN agg_type=1 THEN data::TEXT ELSE NULL END) AS histogram,
        MAX(CASE WHEN agg_type=2 THEN data::TEXT ELSE NULL END) AS percentiles
    FROM
        glam_aggregation_{channel}
    WHERE
        version IN ({versions}) AND metric_type != 'boolean'
        OR (metric_type = 'boolean' AND client_agg_type = '')
    GROUP BY
        version, build_id, os, metric, metric_type, metric_key, process, client_agg_type, total_users
    ON CONFLICT (version, os, build_id, process, metric, metric_Key, client_agg_type)
    DO UPDATE SET
        total_users = EXCLUDED.total_users,
        histogram = EXCLUDED.histogram,
        percentiles = EXCLUDED.percentiles
"""

reverse_sql_template = """
    DELETE FROM glam_desktop_{channel}_aggregation WHERE version IN ({versions})
"""


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0007_desktop_views"),
    ]

    operations = [
        migrations.RunSQL(
            [forward_sql_template.format(**d) for d in DATA],
            reverse_sql=[reverse_sql_template.format(**d) for d in DATA],
        )
    ]