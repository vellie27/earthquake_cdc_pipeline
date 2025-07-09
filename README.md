# earthquake_cdc_pipeline

Real_time earthquake CDC Pipeline

File Structure

earthquake_cdc_pipeline/

 docker-compose.yml
 
 config/
 
    mysql.cnf  
    # MySQL binlog configuration
    debezium-connector.json 
    # Debezium MySQL source config
    jdbc-sink.json 
    # PostgreSQL JDBC sink config
 usgs-poller/
 
    poller.py  
    # USGS API polling script
    requirements.txt
    # Python dependencies
    
 grafana/
 
    dashboards/          # Grafana dashboard JSONs


Deployment Commands

Start all services:

bash

docker-compose up -d --build

Register connectors (wait 2 mins after startup):


bash

# MySQL CDC Source
curl -X POST -H "Content-Type: application/json" \
--data @config/debezium-connector.json \
http://localhost:8083/connectors

# PostgreSQL Sink
curl -X POST -H "Content-Type: application/json" \
--data @config/jdbc-sink.json \
http://localhost:8083/connectors
Verify connectors:


bash

curl http://localhost:8083/connectors | jq


Maintenance Commands

bash
# View pipeline logs
docker-compose logs -f poller

# Check Kafka topics
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092

# Inspect PostgreSQL data
docker exec -it postgres psql -U postgres -d quake_analytics -c "SELECT COUNT(*) FROM earthquake_events;"

# Restart components
docker-compose restart poller


Troubleshooting

bash
# Check connector status
curl -s http://localhost:8083/connectors/earthquake-postgres-sink/status | jq

# Verify MySQL data
docker exec -it mysql mysql -uroot -proot earthquake_db -e "SELECT * FROM earthquake_minute LIMIT 1;"

# Test USGS API
curl "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=$(date -u -v-1M +'%Y-%m-%dT%H:%M:%S')&endtime=$(date -u +'%Y-%m-%dT%H:%M:%S')"


Clean Up

bash

docker-compose down -v
docker volume prune
