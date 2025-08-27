# NATS Configuration Server

Run this code to set up a NATS configuration server with HTTP API for automatic account and user management.

## Installation

First, ensure you have NATS Server and NSC tools installed on your server:

```bash
curl -L https://raw.githubusercontent.com/nats-io/nsc/master/install.py | python
```

Then, use [git](https://git-scm.com/downloads) to clone this repository:
```bash
git clone https://github.com/Adi7015YT/nats-account-autoconfig
```

## Configuration

**FIRST, CUSTOMIZE THE CONFIGURATION IN THE `nats_config_server.py` FILE:**

1. Set your NATS server URL:
```python
NATS_SERVER_URL = "nats://your-server.com:4222"  # Your NATS server address
```

2. Configure your operator name:
```python
OPERATOR = "OP_NAME"  # Your NATS operator name
```

3. Adjust server listening settings (if needed):
```python
SERVER_HOST = '0.0.0.0'  # Listen on all interfaces
SERVER_PORT = 8080       # API server port
```

4. Set credentials storage directory:
```python
CREDS_DIR = "/etc/nats/creds"  # Directory to store credentials
```

## Usage

Start the NATS server first (if not already running):
```bash
nats-server &
```

Then start the configuration server:
```bash
sudo python3.9 nats_config_server.py
```

The server will start listening for client requests on port 8080.

### Client Usage

Clients can retrieve their credentials with a single command:

```bash
# Download credentials for account "myapp" and user "client1"
curl "http://your-server.com:8080/?account=myapp&user=client1" > myapp_client1.creds

# Use credentials with NATS client
nats sub -creds myapp_client1.creds "myapp.requests"
```

Or combine both commands:

```bash
curl "http://your-server.com:8080/?account=myapp&user=client1" | nats sub -creds - "myapp.requests"
```

## Features

- **HTTP API**: Simple RESTful interface for credential requests
- **Automatic Account Management**: Creates accounts and users on-demand
- **Key Generation**: Automatically generates signing keys and user credentials
- **Server Integration**: Automatically pushes accounts to NATS server
- **No External Dependencies**: Pure Python implementation
- **Secure**: Automatic credential generation and management

## Requirements

- Python 3.9+
- NATS Server (`nats-server`)
- NATS CLI tools (`nsc`)
- Superuser access (for server operation)
- Client machines need `curl` and NATS client tools

## Security Notes

- The server runs on HTTP by default. For production use, consider:
  - Adding HTTPS/TLS encryption
  - Implementing client authentication
  - Using a reverse proxy with SSL termination
  - Restricting access with firewall rules
  - Regular rotation of account signing keys

## Contributing

Pull requests are welcome. Please open an issue first to discuss significant changes.

## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)

## Repository Structure

```
nats-config-server/
├── nats_config_server.py    # Main server script
├── README.md                # This file
└──requirements.txt         # Python requirements
```
This implementation provides a complete solution for automating NATS account and user management through a simple HTTP API, making it easy for clients to get connected with a single command.
```
