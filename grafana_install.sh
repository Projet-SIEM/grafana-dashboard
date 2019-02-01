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
