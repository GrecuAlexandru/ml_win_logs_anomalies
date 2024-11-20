import os
import json
import subprocess
import time


def parse_pcap(path, name, test):
    # Use tshark to extract TCP payloads directly
    tshark_cmd = [
        "tshark",
        "-r",
        path,
        "-Y",
        "tcp",
        "-T",
        "fields",
        "-e",
        "tcp.payload",
    ]
    result = subprocess.run(tshark_cmd, capture_output=True, text=True)

    tcp_payloads = result.stdout.splitlines()
    tcp_payloads = [payload.replace(":", "") for payload in tcp_payloads if payload]

    tcp_payload = "".join(tcp_payloads)
    return parse_payload(tcp_payload, name, test)


def parse_payload(payloads, name, test):
    json_object = []

    try:
        # Convert the hex string to bytes
        data = bytes.fromhex(payloads)

        json_data = json.loads(data)

        json_object.append(json_data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error decoding payload: {e}")

    json_object[0]["filename"] = name
    if test:
        json_object[0]["label"] = 0

    return json_object


def parse_json(path, output, test):
    all_json_objects = []

    for file in os.listdir(path):
        file_path = f"{path}/{file}"
        json_objects = parse_pcap(file_path, file, test)
        all_json_objects.extend(json_objects)

    if all_json_objects:
        with open(output, "w") as outfile:
            json.dump(all_json_objects, outfile, indent=4)
    else:
        print("No valid JSON objects found.")


parse_json("/usr/src/app/InputData/test", "test.json", True)
parse_json("/usr/src/app/InputData/train", "train.json", False)
