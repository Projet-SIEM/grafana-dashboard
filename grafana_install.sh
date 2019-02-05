# Install grafana (dashboard)
echo "deb https://packages.grafana.com/oss/deb stable main" > /etc/apt/sources.list.d/grafana.list
apt-get install -y curl
apt-get install  -y apt-transport-https
curl https://packages.grafana.com/gpg.key | sudo apt-key add -
apt-get update
apt-get install grafana

grafana-cli plugins install grafana-piechart-panel
grafana-cli plugins install grafana-worldmap-panel

#Start grafana
systemctl daemon-reload
systemctl start grafana-server

# Install influxdb
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/debian stretch stable" > /etc/apt/sources.list.d/influxdb.list
apt-get update
apt-get install influxdb
systemctl start influxdb
systemctl enable influxdb

# Install influxdb python API
apt-get install python3-pip
python3 -m pip install influxdb
