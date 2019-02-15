# Install grafana (dashboard)
apt-get clean
apt-get update
apt-get install -y curl
apt-get install  -y apt-transport-https
curl https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" > /etc/apt/sources.list.d/grafana.list
apt-get update
apt-get upgrade
apt-get install -y grafana

grafana-cli plugins install grafana-piechart-panel
grafana-cli plugins install grafana-worldmap-panel

#Start grafana
systemctl daemon-reload
systemctl start grafana-server

# Install influxdb
apt-get clean
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/debian stretch stable" > /etc/apt/sources.list.d/influxdb.list
apt-get update
apt-get install -y influxdb
systemctl start influxdb
systemctl enable influxdb

# Install datasource configuration file for Malilog
cp datasource.yaml /etc/grafana/provisioning/datasources/

# Install dashboard JSON descriptor for Malilog dashboard
mkdir -p /var/lib/grafana/dashboards
cp dashboard.yaml /etc/grafana/provisioning/dashboards/
cp MalilogDashboard.json /var/lib/grafana/dashboards

# Install influxdb python API
apt-get clean
apt-get install -y python3-pip
python3 -m pip install influxdb

# Install geoDB and geohash for IP geolocation on the dashboard
mkdir -p geolite2-city
wget https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz
tar -xzf GeoLite2-City.tar.gz -C geolite2-city --strip-components=1
rm -R --interactive=never GeoLite2-City.tar.gz
rm -R --interactive=never /usr/share/geolocation-database
mkdir -p /usr/share/geolocation-database
mv geolite2-city /usr/share/geolocation-database
python3 -m pip install geoip2
python3 -m pip install Geohash2

mkdir -p /home/vagrant/grafana-dashboard
cp log_to_bdd.py /home/vagrant/grafana-dashboard/log_to_bdd.py
cp alert_to_bdd.py /home/vagrant/grafana-dashboard/alert_to_bdd.py
# cp ./logcheck /etc/cron.d/logcheck # La tâche CRON pour exécution auto programmée.
# Reload service so the imported dashboard and datasource are used.
systemctl stop grafana-server
systemctl start grafana-server
systemctl enable grafana-server
