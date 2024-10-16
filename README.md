# Project Documentation

## Overview

This project is designed to monitor the validator's childkey stake status, and continuously running a specified script at defined intervals. The project consists of several scripts that work together to achieve this goal.

## How to Run the Package

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/bactensor/bt-chlidkey-monitor
   cd bt-chlidkey-monitor
   ```

2. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
   ```

3. **Set Up the .env file**:
    ```sh
    SENTRY_DSN = "your sentry sdn"
    ```
4. **Prepare the config file**:
The script uses config.yaml file to get the configuration. Each run will store the current state of the repository in a SQLite database. Path to the database is specified in the config file. You can prepare your own config file based on the example in the repository. Here is the structure of the config file:

    ```
    # config.yaml
    DATABASE_DIR: "/path/to/your/db"
    CHAIN_ENDPOINT: "the chain endpoint url for connection"
    ```

5. **Run the Main Script**:
Run the script providing the config file and (optionally) wait interval between consecutive runs (in seconds).
    ```sh
    python main.py --interval 3600 config.yaml
    ```

## Target
The primary target of this project is to monitor the Validator's childkey stake status:


## Main Principles

1. Continuous Monitoring:

 * Identify validators from all subnets that have detected neurons holding more than 1000 Tao.
 * Use the Polkadot SDK to check their parentKey status on the chain and analyze the results.

## Script Explanations

### ParentkeyMonitor Class

The `ParentkeyMonitor` class is responsible for monitoring and managing parent keys in the blockchain network. It retrieves data about validators and their stakes, processes this data, and updates the database accordingly.

#### Methods

- `__init__(self, config: Dict) -> None`: Initializes the `ParentkeyMonitor` class with the given configuration.
- `get_subnet_uids(self, subtensor) -> List[int]`: Retrieves subnet UIDs from the subtensor.
- `get_subnet_validators(self, netuid: int, subtensor) -> List[HotkeyModel]`: Retrieves validators for a specific subnet.
- `get_all_validators_subnets(self, subtensor) -> Tuple[List[HotkeyModel], List[int]]`: Retrieves all validators and their associated subnets.
- `monitor_parentkeys(self) -> None`: Monitors parent keys and updates the database with the latest information.
- `_process_parent_keys(self, parent_keys: List[Dict], validator: HotkeyModel) -> None`: Processes and saves parent keys for a given validator.
- `_get_or_create_parent_validator(self, parent_key: Dict) -> HotkeyModel`: Retrieves or creates a parent validator.
- `_get_current_stake(self, hotkey: str) -> float`: Gets the current stake for a hotkey.

#### Usage

To use the `ParentkeyMonitor` class, you need to initiali
### DataBaseManager Class

The `DataBaseManager` class is responsible for managing database operations such as setting up the database path, applying migrations, and deleting the database file.

#### Methods

- `__init__(self, db_path: str) -> None`: Initializes the `DataBaseManager` class with the path to the database file.
  - `db_path`: Path to the SQLite database file.

- `delete_database_file(self) -> None`: Deletes the database file if it exists. Logs a message indicating whether the file was deleted or if it did not exist.

- `migrate_db(self) -> None`: Applies Django migrations to set up or update the database schema. Logs a message indicating whether the migration was successful or if there was an error.

#### Usage

To use the `DataBaseManager` class, you need to initialize it with the path to the database file and call its methods to manage the database.

## Django Integration

This project also includes a Django application to manage and display the data collected by the monitoring scripts. The Django application is set up to use the same SQLite database specified in the `config.yaml` file.

### Django Application Structure

* `bt_childkey_monitor/`: Main Django application directory.
    * `asgi.py`: ASGI configuration.
    * `settings.py`: Django settings.
    * `urls.py`: URL routing.
    * `wsgi.py`: WSGI configuration.
* `validators/`: Django app for managing validators.
    * `admin.py`: Admin interface configuration.
    * `apps.py`: App configuration.
    * `models.py`: Database models.
    * `views.py`: Views for handling HTTP requests.
    * `migrations/`: Database migrations.

## Dockerization

This project is Dockerized to ensure a consistent and reproducible environment for running the application. The Docker setup includes a `Dockerfile` and a `docker-compose.yml` file.

### Dockerfile

The `Dockerfile` defines the environment and dependencies required to run the application.

### docker-compose.yml

The `docker-compose.yml` file orchestrates the Docker containers needed for the application. Here is an excerpt from the `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - .:/app
    environment:
      - SENTRY_DSN=${SENTRY_DSN}
    env_file:
      - ./.env
    command: ["python", "main.py", "--interval", "3600", "config.yaml"]

```

## Project Overview

```
project/
    ├── Dockerfile
    ├── README.md
    ├── __init__.py
    ├── bt_childkey_monitor
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── config.yaml
    ├── db
    │   └── db.sqlite3
    ├── docker-compose.yml
    ├── find_parentkeys
    │   ├── database_manage
    │   │   └── db_manage.py
    │   ├── parentkey_monitor
    │   │   └── monitor_parentkey.py
    │   └── utils
    │       ├── db.sqlite3
    │       ├── get_parentkey.py
    │       └── sentry.py
    ├── main.py
    ├── manage.py
    ├── requirements.txt
    └── validators
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── migrations
        ├── models.py
        ├── tests.py
        └── views.py
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.