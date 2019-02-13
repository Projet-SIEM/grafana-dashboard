import sys
import datetime
from influxdb import InfluxDBClient
from influxdb import SeriesHelper
import geoip2.database
import geohash2

GEOLOC_DB_PATH = '/usr/share/geolocation-database/geolite2-city/GeoLite2-City.mmdb'
TIME = 0
L4_PROTO = 1
L3_PROTO = 2
IP_SRC = 3
IP_DST = 4
PORT_SRC = 5
PORT_DST = 6
LOG_MSG = 7
TIME_ALERT = 8
ALERT_TYPE = 9
SECTION_MARKER = "=-=-=-=-=-=-="

client = InfluxDBClient(host='localhost', port=8086)
# client.drop_database('malilog_logs')
# client.create_database('malilog_logs')
client.switch_database('malilog_logs')


def get_time_now():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def parse_log_line(line):
    tokens = []
    tokens_raw = line.strip().split()
    date = ' '.join([tokens_raw[0], tokens_raw[1]])
    tokens.append(date[1:-1])
    tokens.extend(tokens_raw[2:8])
    msg = ' '.join(tokens_raw[8:len(tokens_raw)])
    tokens.append(msg)
    yield tokens


def get_logs_lines(path):
    current_section_name = "Header"
    last_line = None

    with open(path, 'r') as f:
        for line in f:
            if line.strip == "":
                pass
            elif line == SECTION_MARKER:
                current_section_name = last_line
            elif current_section_name != "Header" and line.startswith("["):
                tokens = parse_log_line(line)
                tokens.extend(get_time_now())
                tokens.extend(current_section_name)
                yield tokens

            last_line = line

class MySeriesHelper(SeriesHelper):
    """Instantiate SeriesHelper to write points to the backend."""

    class Meta:
        """Meta class stores time series helper configuration."""

        # The client should be an instance of InfluxDBClient.
        client = client

        # The series name must be a string. Add dependent fields/tags
        # in curly brackets.
        series_name = '{table_name}'

        # Defines all the fields in this time series.
        fields = ['port_src', 'port_dst', 'time_event']

        # Defines all the tags for the series.
        tags = ['alert_type', 'src_geohash', 'l3_proto', 'l4_proto', "ip_src", "ip_dst", "log_message"]

        # Defines the number of data points to store prior to writing
        # on the wire.
        bulk_size = 5

        # autocommit must be set to True when using bulk_size
        autocommit = True


if len(sys.argv) < 2:
    print("Error : need log file path as parameter")
    exit(-1)

entries = get_logs_lines(sys.argv[1])
reader = geoip2.database.Reader(GEOLOC_DB_PATH)

# e.g [2019-02-06 14:27:40] TCP ipv4 139.143.119.26  18.123.82.2 30249 43781 Default message for logs
for entry in entries:
    print("Current log line : ", entry)
    try:
        geoloc = reader.city(entry[IP_SRC])
        latitude = geoloc.location.latitude
        longitude = geoloc.location.longitude
        geohash = geohash2.encode(latitude, longitude)
    except (geoip2.errors.AddressNotFoundError, Exception):
        geohash = "UNKNOW"
    MySeriesHelper(time=entry[TIME_ALERT],
                   table_name='Malilog-alerts',
                   time_event=entry[TIME],
                   alert_type=entry[ALERT_TYPE],
                   src_geohash=geohash,
                   l3_proto=entry[L3_PROTO],
                   l4_proto=entry[L4_PROTO],
                   ip_src=entry[IP_SRC], ip_dst=entry[IP_DST],
                   port_src=int(entry[PORT_SRC]), port_dst=int(entry[PORT_DST]),
                   log_message=entry[LOG_MSG]
                   )
    MySeriesHelper.commit()