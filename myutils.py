def load_config(config_file):
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key.strip()] = value.strip()
    return config

def version():
    with open('version.txt', 'r') as file:
    content = file.read()  # Reads the entire file content
    return content
