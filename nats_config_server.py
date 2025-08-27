"""
NATS Configuration Server with HTTP API
Run this on your NATS server to handle client requests
"""
import os
import subprocess
import json
import urllib.parse
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Configuration - Customize these
SERVER_HOST = '0.0.0.0'  # Listen on all interfaces
SERVER_PORT = 8080       # HTTP port for the configuration server
NATS_SERVER_URL = "nats://your_server:4222"  # Your NATS server URL
CREDS_DIR = "./"  # Directory to store credentials

def run_nsc_command(command: list) -> tuple:
    """Run an NSC command and return the result."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr

def account_exists(account_name: str) -> bool:
    """Check if an account already exists."""
    returncode, stdout, stderr = run_nsc_command([
        "nsc", "describe", "account",
        account_name
    ])
    return returncode == 0

def user_exists(account_name: str, user_name: str) -> bool:
    """Check if a user already exists in an account."""
    returncode, stdout, stderr = run_nsc_command([
        "nsc", "describe", "user"
        "--account", account_name, 
        user_name
    ])
    return returncode == 0

def create_account(account_name: str) -> None:
    """Create a new account and generate a signing key."""
    if not account_exists(account_name):
        # Create the account
        returncode, stdout, stderr = run_nsc_command([
            "nsc", "add", "account",
            account_name
        ])
        if returncode != 0:
            raise Exception(f"Failed to create account: {stderr}")
        
        # Generate signing key
        returncode, stdout, stderr = run_nsc_command([
            "nsc", "edit", "account",
            account_name, "--sk", "generate"
        ])
        if returncode != 0:
            raise Exception(f"Failed to generate signing key: {stderr}")

def create_user(account_name: str, user_name: str) -> None:
    """Create a new user in the specified account."""
    returncode, stdout, stderr = run_nsc_command([
        "nsc", "add", "user",
        "--account", account_name, 
        user_name
    ])
    if returncode != 0:
        raise Exception(f"Failed to create user: {stderr}")

def generate_creds(account_name: str, user_name: str) -> str:
    """Generate credentials file and return its path."""
    creds_filename = f"{account_name}_{user_name}.creds"
    creds_path = os.path.join(CREDS_DIR, creds_filename)
    
    returncode, stdout, stderr = run_nsc_command([
        "nsc", "generate", "creds",
        "--account", account_name,
        "--name", user_name,
        "--output-file", creds_path
    ])
    
    if returncode != 0:
        raise Exception(f"Failed to generate credentials: {stderr}")
    
    return creds_path

def push_account(account_name: str) -> None:
    """Push account changes to the NATS server."""
    returncode, stdout, stderr = run_nsc_command([
        "nsc", "push",
        "--account", account_name,
        "-u", NATS_SERVER_URL
    ])
    
    if returncode != 0:
        raise Exception(f"Failed to push account to NATS server: {stderr}")

class NATSConfigHandler(BaseHTTPRequestHandler):
    """HTTP request handler for NATS configuration requests."""
    
    def do_GET(self):
        """Handle GET requests for NATS configuration."""
        try:
            # Parse query parameters
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            # Get account and user names from query parameters
            if 'account' not in query_params or 'user' not in query_params:
                self.send_error(400, "Both 'account' and 'user' parameters are required")
                return
                
            account_name = query_params['account'][0]
            user_name = query_params['user'][0]
            
            if not account_name or not user_name:
                self.send_error(400, "Account and user names cannot be empty")
                return
            
            print(f"Processing request for account: {account_name}, user: {user_name}")
            
            # Create account if it doesn't exist
            if not account_exists(account_name):
                print(f"Creating account: {account_name}")
                create_account(account_name)
            
            # Create user
            print(f"Creating user: {user_name}")
            create_user(account_name, user_name)
            
            # Generate credentials
            print(f"Generating credentials for: {user_name}")
            creds_path = generate_creds(account_name, user_name)
            
            # Push account to NATS server
            print(f"Pushing account to NATS server: {account_name}")
            push_account(account_name)
            
            # Read the credentials file
            with open(creds_path, 'r') as f:
                creds_content = f.read()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(creds_content.encode('utf-8'))
            
            print(f"Credentials generated for: {account_name}/{user_name}")
            
        except Exception as e:
            self.send_error(500, f"Error generating configuration: {str(e)}")
            print(f"Error handling request: {e}")

def run_server():
    """Run the HTTP server."""
    
    # Start the server
    server = HTTPServer((SERVER_HOST, SERVER_PORT), NATSConfigHandler)
    print(f"NATS configuration server listening on {SERVER_HOST}:{SERVER_PORT}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server shutting down")
        server.shutdown()

if __name__ == "__main__":
    run_server()
