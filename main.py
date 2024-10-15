import os
import time
import argparse
import yaml
from dotenv import load_dotenv
from find_parentkeys.parentkey_monitor.monitor_parentkey import monitor_parentkeys
from find_parentkeys.utils.sentry import init_sentry

load_dotenv()
sentry_dsn = os.getenv("SENTRY_DSN")

def create_db_directory(db_path):
    """Creates a db directory at the specified path if it doesn't exist."""
    if not os.path.exists(db_path):
        os.makedirs(db_path)
        print(f"Created directory: {db_path}")
    else:
        print(f"Directory already exists: {db_path}")

def run_bot(timestamp, config):
    """Runs the 'monitor_parentkeys' function continuously with a delay specified by timestamp."""
    while True:
        monitor_parentkeys(config)  # Pass the config file to monitor_parentkeys
        print(f"monitor_parentkeys finished, sleeping for {timestamp} seconds")
        time.sleep(timestamp)  # Delay for the specified time in seconds

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Initialize and run the bot.")
    parser.add_argument("config_file", default='config.yaml', help="Path to the YAML configuration file.")
    parser.add_argument("--interval", type=int, default=3600, help="Delay between runs in seconds.")
    args = parser.parse_args()
    
    init_sentry(sentry_dsn)
    
    with open(args.config_file, "r") as f:
        config = yaml.safe_load(f)
    db_dir = config.get("DATABASE_DIR")

    create_db_directory(db_dir)  # Create a db directory at the specified path

    timestamp = args.interval
    run_bot(timestamp, config)