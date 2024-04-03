from confluent_kafka import Consumer, KafkaError

# Fonction pour lire les données depuis Kafka
def consume_from_kafka():
    # Configuration Kafka
    bootstrap_servers = 'localhost:9092'
    topic = 'test'
    
    # Configuration du consommateur Kafka
    conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'my_consumer_group',
        'auto.offset.reset': 'earliest'
    }

    # Créer un consommateur Kafka
    consumer = Consumer(conf)

    # Abonnement au topic
    consumer.subscribe([topic])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # Fin du message
                    continue
                else:
                    print(msg.error())
                    break
            else:
                # Message reçu
                print('Received message: {}'.format(msg.value().decode('utf-8')))
    finally:
        # Fermer le consommateur Kafka
        consumer.close()

consume_from_kafka()
