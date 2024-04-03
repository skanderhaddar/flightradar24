from confluent_kafka import Producer
from datetime import datetime
import pandas as pd
import time
from RSS import get_new_flights

# Fonction pour envoyer des données à Kafka
def send_to_kafka(producer, row, topic):
    producer.produce(topic, key=str(row).encode('utf-8'), value=str(row).encode('utf-8'))
    producer.flush()

def produceKafka(df):
    # Configuration Kafka
    bootstrap_servers = 'localhost:9092'
    topic = 'test'

    # Configuration du producteur Kafka
    conf = {'bootstrap.servers': "localhost:9092"}
    # Création de l'instance du producteur Kafka
    producer = Producer(**conf)

    # Boucle pour envoyer les données à Kafka toutes les minutes
    for index, row in df.iterrows():
        print(row)
        send_to_kafka(producer, row, topic)
        print("Sent message:", row)
        time.sleep(1)  # Assuming you want to send messages every second

    # Fermer le producteur Kafka
    producer.flush()
    # Fermer le producteur
    del producer
# Create a dictionary with data
"""data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'Age': [25, 30, 35, 40],
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston']
}

# Create DataFrame from dictionary
df = pd.DataFrame(data)"""



df = get_new_flights(duré = 10)[0]
produceKafka(df)