import sys
from influxdb import InfluxDBClient
from influxdb import SeriesHelper

TIME = 0
L4_PROTO = 1
L3_PROTO = 2
IP_SRC = 3
IP_DST = 4
PORT_SRC = 5
PORT_DST = 6
LOG_MSG = 7

client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('malilog_logs')


def get_logs_lines(path):
    with open(path, 'r') as f:
        for line in f:
            tokens = line.strip().split(' ')
            yield tokens


class MySeriesHelper(SeriesHelper):
    """Instantiate SeriesHelper to write points to the backend."""

    class Meta:
        """Meta class stores time series helper configuration."""

        # The client should be an instance of InfluxDBClient.
        client = client

        # The series name must be a string. Add dependent fields/tags
        # in curly brackets.
        series_name = 'events.stats.{server_name}'

        # Defines all the fields in this time series.
        fields = ['port_src', 'port_dst']

        # Defines all the tags for the series.
        tags = ['server_name', 'l4_proto', "ip_src", "ip_dst", "log_message"]

        # Defines the number of data points to store prior to writing
        # on the wire.
        bulk_size = 5

        # autocommit must be set to True when using bulk_size
        autocommit = True


if len(sys.argv) < 2:
    print("Error : need log file path as parameter")
    exit(-1)

entries = get_logs_lines(sys.argv[1])

# e.g [2019-02-06 14:27:40] TCP ipv4 139.143.119.26  18.123.82.2 30249 43781 Default message for logs
for entry in entries:
    print("Current log line : ", entry)
    MySeriesHelper(time=entries[TIME],
                   server_name='Malilog server 1',
                   l4_proto=entries[L4_PROTO],
                   ip_src=entries[IP_SRC], ip_dst=entries[IP_DST],
                   port_src=entries[PORT_SRC], port_dst=entries[PORT_DST],
                   log_message=entries[LOG_MSG]
                   )
