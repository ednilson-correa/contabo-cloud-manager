#!/usr/bin/env python3
"""
Contabo Cloud Manager
A comprehensive CLI tool to manage Contabo cloud resources (VMs, storage, snapshots, etc.)
API Documentation: https://api.contabo.com/docs/

Requirements:
    pip install requests urllib3 PyYAML

Setup:
    1. Get API credentials from Contabo Control Panel
    2. Set environment variables or create ~/.contabo/config.yaml:
        CONTRIBO_CLIENT_ID=your_client_id
        CONTRIBO_CLIENT_SECRET=your_client_secret
        CONTRIBO_API_KEY=your_api_key
"""

import os
import sys
import json
import argparse
import urllib3
import requests
from datetime import datetime
from pathlib import Path

# Disable SSL warnings for self-signed certs (optional)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ContaboManager:
    """Main class to interact with Contabo API"""
    
    BASE_URL = "https://api.contabo.com"
    
    def __init__(self, client_id=None, client_secret=None, api_key=None, config_path=None):
        """Initialize with credentials"""
        self.client_id = client_id or os.getenv("CONTRIBO_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("CONTRIBO_CLIENT_SECRET")
        self.api_key = api_key or os.getenv("CONTRIBO_API_KEY")
        
        # Try loading from config file
        if not all([self.client_id, self.client_secret, self.api_key]):
            self._load_config(config_path)
        
        if not all([self.client_id, self.client_secret, self.api_key]):
            raise ValueError(
                "Missing credentials! Set CONTRIBO_CLIENT_ID, CONTRIBO_CLIENT_SECRET, "
                "and CONTRIBO_API_KEY environment variables, or create ~/.contabo/config.yaml"
            )
        
        self.access_token = None
        self.token_expiry = None
        self.session = requests.Session()
        self.session.verify = False  # Contabo API may have cert issues
        
    def _load_config(self, config_path=None):
        """Load credentials from config file"""
        if config_path is None:
            config_path = Path.home() / ".contabo" / "config.yaml"
        
        if Path(config_path).exists():
            try:
                import yaml
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    self.client_id = self.client_id or config.get("client_id")
                    self.client_secret = self.client_secret or config.get("client_secret")
                    self.api_key = self.api_key or config.get("api_key")
            except ImportError:
                print("PyYAML not installed. Install with: pip install PyYAML")
                
    def authenticate(self):
        """Get OAuth2 access token from Contabo"""
        url = f"{self.BASE_URL}/oauth/v1/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        
        try:
            response = self.session.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data["access_token"]
            # Store token for subsequent requests
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "x-api-key": self.api_key,
                "Accept": "application/json",
            })
            return True
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            return False
    
    def _request(self, method, endpoint, **kwargs):
        """Make authenticated API request"""
        if not self.access_token:
            self.authenticate()
        
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"API Error: {e.response.status_code} - {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    # ==================== Compute Instances (VMs) ====================
    
    def list_instances(self, page=1, size=20):
        """List all VPS instances"""
        print(f"\n{'='*80}")
        print(f"VPS INSTANCES (Page {page})")
        print('='*80)
        
        data = self._request("GET", "/v1/compute/instances", params={"page": page, "size": size})
        if not data or "data" not in data:
            print("No instances found or error occurred.")
            return
        
        instances = data["data"]
        if not instances:
            print("No instances found.")
            return
        
        for inst in instances:
            print(f"\nID: {inst.get('instanceId')}")
            print(f"  Name: {inst.get('name', 'N/A')}")
            print(f"  Status: {inst.get('status', 'N/A')}")
            print(f"  IP: {inst.get('ipConfig', {}).get('v4', {}).get('ip', 'N/A')}")
            print(f"  Region: {inst.get('region', 'N/A')}")
            print(f"  Product: {inst.get('product', {}).get('name', 'N/A')}")
            print(f"  OS: {inst.get('image', {}).get('name', 'N/A')}")
        
        # Pagination info
        if "pagination" in data:
            p = data["pagination"]
            print(f"\nPage {p.get('page', 1)} of {p.get('pages', 1)} (Total: {p.get('total', 0)})")
    
    def get_instance(self, instance_id):
        """Get details of a specific instance"""
        print(f"\n{'='*80}")
        print(f"INSTANCE DETAILS: {instance_id}")
        print('='*80)
        
        data = self._request("GET", f"/v1/compute/instances/{instance_id}")
        if not data or "data" not in data:
            return
        
        inst = data["data"]
        print(json.dumps(inst, indent=2))
    
    def start_instance(self, instance_id):
        """Start a stopped instance"""
        print(f"Starting instance {instance_id}...")
        data = self._request("POST", f"/v1/compute/instances/{instance_id}/actions/start")
        if data:
            print("Start command sent successfully.")
        else:
            print("Failed to start instance.")
    
    def stop_instance(self, instance_id, force=False):
        """Stop a running instance"""
        print(f"Stopping instance {instance_id} (force={force})...")
        data = self._request(
            "POST", 
            f"/v1/compute/instances/{instance_id}/actions/stop",
            json={"force": force}
        )
        if data:
            print("Stop command sent successfully.")
        else:
            print("Failed to stop instance.")
    
    def restart_instance(self, instance_id, force=False):
        """Restart an instance"""
        print(f"Restarting instance {instance_id} (force={force})...")
        data = self._request(
            "POST",
            f"/v1/compute/instances/{instance_id}/actions/restart",
            json={"force": force}
        )
        if data:
            print("Restart command sent successfully.")
        else:
            print("Failed to restart instance.")
    
    def delete_instance(self, instance_id):
        """Delete an instance"""
        confirm = input(f"Are you sure you want to DELETE instance {instance_id}? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cancelled.")
            return
        
        print(f"Deleting instance {instance_id}...")
        response = self._request("DELETE", f"/v1/compute/instances/{instance_id}")
        if response is not None:  # DELETE might return 204 No Content
            print("Instance deleted successfully.")
        else:
            print("Failed to delete instance.")
    
    # ==================== Snapshots ====================
    
    def list_snapshots(self, instance_id=None):
        """List snapshots"""
        print(f"\n{'='*80}")
        print("SNAPSHOTS")
        print('='*80)
        
        params = {}
        if instance_id:
            params["instanceId"] = instance_id
        
        data = self._request("GET", "/v1/compute/snapshots", params=params)
        if not data or "data" not in data:
            print("No snapshots found.")
            return
        
        snapshots = data["data"]
        for snap in snapshots:
            print(f"\nID: {snap.get('snapshotId')}")
            print(f"  Name: {snap.get('name', 'N/A')}")
            print(f"  Instance: {snap.get('instanceId', 'N/A')}")
            print(f"  Status: {snap.get('status', 'N/A')}")
            print(f"  Size: {snap.get('size', 'N/A')} GB")
    
    def create_snapshot(self, instance_id, name=None):
        """Create a snapshot of an instance"""
        if not name:
            name = f"snapshot-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        print(f"Creating snapshot '{name}' for instance {instance_id}...")
        data = self._request(
            "POST",
            "/v1/compute/snapshots",
            json={"instanceId": instance_id, "name": name}
        )
        if data:
            print("Snapshot creation initiated.")
        else:
            print("Failed to create snapshot.")
    
    # ==================== Storage ====================
    
    def list_storage(self):
        """List storage volumes"""
        print(f"\n{'='*80}")
        print("STORAGE VOLUMES")
        print('='*80)
        
        data = self._request("GET", "/v1/compute/storages")
        if not data or "data" not in data:
            print("No storage volumes found.")
            return
        
        volumes = data["data"]
        for vol in volumes:
            print(f"\nID: {vol.get('storageId')}")
            print(f"  Name: {vol.get('name', 'N/A')}")
            print(f"  Size: {vol.get('size', 'N/A')} GB")
            print(f"  Status: {vol.get('status', 'N/A')}")
            print(f"  Instance: {vol.get('instanceId', 'Not attached')}")
    
    # ==================== Networking ====================
    
    def list_firewalls(self):
        """List firewall rules"""
        print(f"\n{'='*80}")
        print("FIREWALL RULES")
        print('='*80)
        
        data = self._request("GET", "/v1/compute/firewalls")
        if not data or "data" not in data:
            print("No firewall rules found.")
            return
        
        rules = data["data"]
        for rule in rules:
            print(f"\nID: {rule.get('firewallId')}")
            print(f"  Name: {rule.get('name', 'N/A')}")
            print(f"  Instance: {rule.get('instanceId', 'N/A')}")
            print(f"  Rules: {len(rule.get('rules', []))} configured")
    
    # ==================== Usage/Metrics ====================
    
    def get_usage(self):
        """Get resource usage/limits"""
        print(f"\n{'='*80}")
        print("RESOURCE USAGE")
        print('='*80)
        
        data = self._request("GET", "/v1/compute/usage")
        if not data or "data" not in data:
            print("Could not fetch usage data.")
            return
        
        usage = data["data"]
        print(json.dumps(usage, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Contabo Cloud Manager - Manage VMs and resources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                           # List all instances
  %(prog)s start <instance_id>             # Start an instance
  %(prog)s stop <instance_id>              # Stop an instance
  %(prog)s restart <instance_id>           # Restart an instance
  %(prog)s snapshots list                  # List all snapshots
  %(prog)s snapshots create <instance_id>  # Create snapshot
  %(prog)s storage list                    # List storage volumes
  %(prog)s usage                           # Show resource usage

Setup:
  Create ~/.contabo/config.yaml with:
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    api_key: "your_api_key"

  Or set environment variables:
    export CONTRIBO_CLIENT_ID=your_client_id
    export CONTRIBO_CLIENT_SECRET=your_client_secret
    export CONTRIBO_API_KEY=your_api_key
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Instance commands
    subparsers.add_parser("list", help="List all VPS instances")
    
    start_parser = subparsers.add_parser("start", help="Start an instance")
    start_parser.add_argument("instance_id", help="Instance ID")
    
    stop_parser = subparsers.add_parser("stop", help="Stop an instance")
    stop_parser.add_argument("instance_id", help="Instance ID")
    stop_parser.add_argument("--force", action="store_true", help="Force stop")
    
    restart_parser = subparsers.add_parser("restart", help="Restart an instance")
    restart_parser.add_argument("instance_id", help="Instance ID")
    restart_parser.add_argument("--force", action="store_true", help="Force restart")
    
    delete_parser = subparsers.add_parser("delete", help="Delete an instance")
    delete_parser.add_argument("instance_id", help="Instance ID")
    
    instance_parser = subparsers.add_parser("instance", help="Get instance details")
    instance_parser.add_argument("instance_id", help="Instance ID")
    
    # Snapshot commands
    snapshot_parser = subparsers.add_parser("snapshots", help="Manage snapshots")
    snapshot_subparsers = snapshot_parser.add_subparsers(dest="snapshot_command")
    snapshot_subparsers.add_parser("list", help="List snapshots")
    create_parser = snapshot_subparsers.add_parser("create", help="Create snapshot")
    create_parser.add_argument("instance_id", help="Instance ID")
    create_parser.add_argument("--name", help="Snapshot name")
    
    # Storage commands
    subparsers.add_parser("storage", help="List storage volumes")
    
    # Firewall commands
    subparsers.add_parser("firewalls", help="List firewall rules")
    
    # Usage command
    subparsers.add_parser("usage", help="Show resource usage")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize manager
    try:
        manager = ContaboManager()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Execute command
    if args.command == "list":
        manager.list_instances()
    elif args.command == "start":
        manager.start_instance(args.instance_id)
    elif args.command == "stop":
        manager.stop_instance(args.instance_id, args.force)
    elif args.command == "restart":
        manager.restart_instance(args.instance_id, args.force)
    elif args.command == "delete":
        manager.delete_instance(args.instance_id)
    elif args.command == "instance":
        manager.get_instance(args.instance_id)
    elif args.command == "snapshots":
        if args.snapshot_command == "list" or not args.snapshot_command:
            manager.list_snapshots()
        elif args.snapshot_command == "create":
            manager.create_snapshot(args.instance_id, args.name)
    elif args.command == "storage":
        manager.list_storage()
    elif args.command == "firewalls":
        manager.list_firewalls()
    elif args.command == "usage":
        manager.get_usage()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
