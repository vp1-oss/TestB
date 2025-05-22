import json

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            print("JSON content:")
            print(json.dumps(data, indent=4))  # Pretty-print JSON
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

# Example usage
if __name__ == "__main__":
    read_json_file("data.json")  # Replace with your JSON file path
