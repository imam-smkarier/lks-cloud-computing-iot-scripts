# Standalone sensor simulator for LKS Cloud Computing Kabupaten Bogor 2026.
# Requires: python -m pip install awsiotsdk

from awscrt import http, mqtt
from awsiot import mqtt_connection_builder
import argparse
import json
import random
import threading
import time
from datetime import datetime, timezone


received_count = 0
received_all_event = threading.Event()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Publish simulated sensor data to AWS IoT Core."
    )
    parser.add_argument("--endpoint", required=True, help="AWS IoT data endpoint.")
    parser.add_argument("--cert", required=True, help="Device certificate file path.")
    parser.add_argument("--key", required=True, help="Private key file path.")
    parser.add_argument("--ca_file", required=True, help="Amazon Root CA file path.")
    parser.add_argument("--client_id", default="lks-sensor-client", help="MQTT client ID.")
    parser.add_argument("--topic", default="lks/sensor/data", help="MQTT topic.")
    parser.add_argument("--count", type=int, default=10, help="Messages to publish. Use 0 for continuous mode.")
    parser.add_argument("--message", default="", help="Optional text message field.")
    parser.add_argument("--port", type=int, default=8883, help="MQTT TLS port.")
    parser.add_argument("--proxy_host", default=None, help="Optional HTTP proxy host.")
    parser.add_argument("--proxy_port", type=int, default=0, help="Optional HTTP proxy port.")
    parser.add_argument("--device_id", default="LKS-Sensor-01", help="Sensor device ID.")
    parser.add_argument("--interval", type=float, default=1.0, help="Delay between messages in seconds.")
    return parser.parse_args()


def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted: {error}")


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(f"Connection resumed. return_code={return_code} session_present={session_present}")
    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()
        resubscribe_future.result()


def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    global received_count
    received_count += 1
    print(f"Received message from topic '{topic}': {payload.decode('utf-8', errors='replace')}")
    received_all_event.set()


def on_connection_success(connection, callback_data):
    print(f"Connection successful. return_code={callback_data.return_code} session_present={callback_data.session_present}")


def on_connection_failure(connection, callback_data):
    print(f"Connection failed: {callback_data.error}")


def on_connection_closed(connection, callback_data):
    print("Connection closed")


def build_sensor_payload(args, sequence):
    payload = {
        "device_id": args.device_id,
        "sequence": sequence,
        "lux": random.randint(300, 1000),
        "temperature": round(random.uniform(24.0, 34.0), 2),
        "humidity": random.randint(45, 85),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    if args.message:
        payload["message"] = args.message

    return payload


def main():
    args = parse_args()

    proxy_options = None
    if args.proxy_host and args.proxy_port:
        proxy_options = http.HttpProxyOptions(
            host_name=args.proxy_host,
            port=args.proxy_port,
        )

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=args.endpoint,
        port=args.port,
        cert_filepath=args.cert,
        pri_key_filepath=args.key,
        ca_filepath=args.ca_file,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=args.client_id,
        clean_session=False,
        keep_alive_secs=30,
        http_proxy_options=proxy_options,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed,
    )

    print(f"Connecting to {args.endpoint} with client ID '{args.client_id}'...")
    mqtt_connection.connect().result()
    print("Connected.")

    print(f"Subscribing to topic '{args.topic}'...")
    subscribe_future, _ = mqtt_connection.subscribe(
        topic=args.topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received,
    )
    subscribe_result = subscribe_future.result()
    print(f"Subscribed with {subscribe_result['qos']}.")

    if args.count == 0:
        print("Publishing continuously. Press Ctrl+C to stop.")
    else:
        print(f"Publishing {args.count} message(s).")

    sequence = 1
    try:
        while args.count == 0 or sequence <= args.count:
            payload = build_sensor_payload(args, sequence)
            message = json.dumps(payload)
            print(f"Publishing to '{args.topic}': {message}")
            mqtt_connection.publish(
                topic=args.topic,
                payload=message,
                qos=mqtt.QoS.AT_LEAST_ONCE,
            )
            sequence += 1
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        print("Disconnecting...")
        mqtt_connection.disconnect().result()
        print("Disconnected.")


if __name__ == "__main__":
    main()
