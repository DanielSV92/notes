import os
import sys
import sqlalchemy as db

engine = None
MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', None)
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', None)
MYSQL_HOSTNAME = os.environ.get('MYSQL_HOSTNAME', None)
SMARTY_DBNAME = os.environ.get('SMARTY_DBNAME', None)

if len(sys.argv) != 1:
    print('usage: python3 init_metrics')
    exit(1)

url = "mysql+pymysql://{0}:{1}@{2}/{3}".format(MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOSTNAME, SMARTY_DBNAME)
engine = db.create_engine(url)

if engine:
    connection = engine.connect()
    metadata = db.MetaData()

    metrics = db.Table('prometheus_metrics', metadata, autoload=True, autoload_with=engine)
    query = db.select([metrics])
    ResultProxy = connection.execute(query)

    if not ResultProxy.first():
        print('Initializing Metrics Table')
        query = db.insert(metrics)
        values_list = [
            {"metric_name": "cpu_cores_machine", "operation": "sum (machine_cpu_cores{<source><instance>})",
             "metric_description": "Total CPU cores"},
            {"metric_name": "cpu_usage",
             "operation": "sum (rate (container_cpu_usage_seconds_total{<source><instance>}[<window>]))",
             "metric_description": "CPU usage"},
            {"metric_name": "cpu_usage_percentage",
             "operation": "sum (rate (container_cpu_usage_seconds_total{<source><instance>}[<window>])) / sum (machine_cpu_cores{<source><instance>}) * 100",
             "metric_description": "Percentage of CPU usage"},
            {"metric_name": "cpu_usage_pod",
             "operation": "sum (rate (container_cpu_usage_seconds_total{pod!='',<source><instance>}[<window>])) by (pod)",
             "metric_description": "CPU usage by application"},
            {"metric_name": "fs_limit",
             "operation": "sum (container_fs_limit_bytes{device=~\"^/dev/.*$\", id=\"/\",<source><instance>})",
             "metric_description": "File System Limit"},
            {"metric_name": "fs_usage",
             "operation": "sum (container_fs_usage_bytes{device=~\"^/dev/.*$\",id=\"/\",<source><instance>})",
             "metric_description": "File System usage"},
            {"metric_name": "fs_usage_percentage",
             "operation": "sum (container_fs_usage_bytes{device=~\"^/dev/.*$\",id=\"/\",<source><instance>}) / sum (container_fs_limit_bytes{device=~\"^/dev/.*$\",id=\"/\",<source><instance>}) * 100",
             "metric_description": "Percentage File System Usage"},
            {"metric_name": "memory_machine", "operation": "sum (machine_memory_bytes{<source><instance>})",
             "metric_description": "Total Memory"},
            {"metric_name": "memory_usage", "operation": "sum (container_memory_working_set_bytes{<source><instance>})",
             "metric_description": "Memory usage"},
            {"metric_name": "memory_usage_percentage",
             "operation": "sum (container_memory_working_set_bytes{<source><instance>}) / sum (machine_memory_bytes{<source><instance>}) * 100",
             "metric_description": "Percentage of CPU usage"},
            {"metric_name": "memory_usage_pod",
             "operation": "sum (container_memory_working_set_bytes{pod!='',<source><instance>}) by (pod)",
             "metric_description": "Memory usage by application"},
            {"metric_name": "network_receive",
             "operation": "sum (rate (container_network_receive_bytes_total{<source><instance>}[<window>]))",
             "metric_description": "Total bytes received by all containers"},
            {"metric_name": "network_receive_pod",
             "operation": "sum (rate (container_network_receive_bytes_total{pod!='',<source><instance>}[<window>])) by (pod)",
             "metric_description": "Total bytes feceived discriminated by application"},
            {"metric_name": "network_transmit",
             "operation": "sum (rate (container_network_transmit_bytes_total{<source><instance>}[<window>]))",
             "metric_description": "Total bytes transmited by all containers"},
            {"metric_name": "network_transmit_pod",
             "operation": "sum (rate (container_network_transmit_bytes_total{pod!='',<source><instance>}[<window>])) by (pod)",
             "metric_description": "Total bytes transmited discriminated by application"}
        ]
        ResultProxy = connection.execute(query, values_list)
    else:
        print('Metrics Table with data')
