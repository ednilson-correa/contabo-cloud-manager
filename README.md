# Contabo Cloud Manager

A comprehensive Python command-line tool to manage Contabo cloud resources including VPS instances, snapshots, storage volumes, firewalls, and more.

[![GitHub](https://img.shields.io/badge/GitHub-ednilson--correa/contabo--cloud--manager-blue?style=flat&logo=github)](https://github.com/ednilson-correa/contabo-cloud-manager)
[![Python](https://img.shields.io/badge/Python-3.7+-green?style=flat&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)

## 📋 Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Commands](#commands)
- [Examples](#examples)
- [API Coverage](#api-coverage)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Instance Management**: List, start, stop, restart, and delete VPS instances
- **Snapshot Management**: Create and list snapshots for backup purposes
- **Storage Management**: View and manage storage volumes
- **Firewall Management**: List and manage firewall rules
- **Resource Monitoring**: Check resource usage and limits
- **OAuth2 Authentication**: Secure API authentication with automatic token handling
- **Pagination Support**: Handle large numbers of resources efficiently

## 🔧 Requirements

- Python 3.7+
- `requests` library
- `PyYAML` library (optional, for config file support)

## 📦 Installation

### Option 1: Clone from GitHub

```bash
git clone git@github.com:ednilson-correa/contabo-cloud-manager.git
cd contabo-cloud-manager
```

### Option 2: Download the Script

Download `contabo_manager.py` directly from the repository.

### Install Dependencies

```bash
pip install requests PyYAML
```

Or install using the requirements file (if available):

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

You need to obtain API credentials from your Contabo Control Panel at https://my.contabo.com/api-settings

### Method 1: Configuration File (Recommended)

Create a config file at `~/.contabo/config.yaml`:

```yaml
# Contabo API Configuration
# Get these credentials from https://my.contabo.com/api-settings
client_id: "your_client_id_here"
client_secret: "your_client_secret_here"
api_username: "your_api_username_here"
api_password: "your_api_password_here"
```

### Method 2: Environment Variables

Set the following environment variables:

```bash
export CONTABO_CLIENT_ID="your_client_id"
export CONTABO_CLIENT_SECRET="your_client_secret"
export CONTABO_API_USERNAME="your_api_username"
export CONTABO_API_PASSWORD="your_api_password"
```

You can add these to your `~/.bashrc` or `~/.zshrc` to make them persistent.

## 🚀 Usage

The script uses a subcommand-based interface similar to `git` or `gh`.

```bash
python3 contabo_manager.py [command] [options]
```

Or make it executable:

```bash
chmod +x contabo_manager.py
./contabo_manager.py [command] [options]
```

### Getting Help

```bash
python3 contabo_manager.py --help
python3 contabo_manager.py [command] --help
```

## 📚 Commands

### Instance Management

#### List all instances
```bash
python3 contabo_manager.py list
```

#### Get instance details
```bash
python3 contabo_manager.py instance <instance_id>
```

#### Start an instance
```bash
python3 contabo_manager.py start <instance_id>
```

#### Stop an instance
```bash
python3 contabo_manager.py stop <instance_id>
# Force stop (hard shutdown)
python3 contabo_manager.py stop <instance_id> --force
```

#### Restart an instance
```bash
python3 contabo_manager.py restart <instance_id>
# Force restart
python3 contabo_manager.py restart <instance_id> --force
```

#### Delete an instance
```bash
python3 contabo_manager.py delete <instance_id>
```
> ⚠️ This will prompt for confirmation before deleting.

### Snapshot Management

#### List all snapshots
```bash
python3 contabo_manager.py snapshots list
```

#### Create a snapshot
```bash
python3 contabo_manager.py snapshots create <instance_id>
# With custom name
python3 contabo_manager.py snapshots create <instance_id> --name "Backup before update"
```

### Storage Management

#### List storage volumes
```bash
python3 contabo_manager.py storage
```

### Firewall Management

#### List firewall rules
```bash
python3 contabo_manager.py firewalls
```

### Resource Usage

#### Show resource usage and limits
```bash
python3 contabo_manager.py usage
```

## 💡 Examples

### Complete Workflow Example

```bash
# List all your VPS instances
python3 contabo_manager.py list

# Get details about a specific instance
python3 contabo_manager.py instance 123456

# Create a snapshot before making changes
python3 contabo_manager.py snapshots create 123456 --name "pre-update-backup"

# Stop the instance for maintenance
python3 contabo_manager.py stop 123456

# After maintenance, start it back up
python3 contabo_manager.py start 123456

# Check resource usage
python3 contabo_manager.py usage
```

### Using with Cron for Automated Backups

You can automate snapshot creation using cron:

```bash
# Edit crontab
crontab -e

# Add line to create snapshots daily at 2 AM
0 2 * * * /usr/bin/python3 /path/to/contabo_manager.py snapshots create 123456 --name "auto-backup-$(date +\%Y\%m\%d)"
```

## 🌐 API Coverage

This tool covers the following Contabo API endpoints:

| Resource | Endpoints |
|----------|-----------|
| **Compute Instances** | List, Get, Start, Stop, Restart, Delete |
| **Snapshots** | List, Create |
| **Storage Volumes** | List |
| **Firewalls** | List |
| **Usage/Metrics** | Get usage statistics |

For full API documentation, visit: https://api.contabo.com/docs/

## 🔒 Security Notes

- Never commit your API credentials to version control
- Use environment variables or the config file (add `~/.contabo/` to your `.gitignore`)
- The config file permissions should be restrictive: `chmod 600 ~/.contabo/config.yaml`
- Regularly rotate your API keys and secrets

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/yourusername/contabo-cloud-manager.git
cd contabo-cloud-manager
pip install -r requirements.txt
pip install -e .
```

### TODO / Roadmap

- [ ] Add storage volume creation and deletion
- [ ] Implement firewall rule creation and modification
- [ ] Add instance creation from snapshots
- [ ] Implement network management (assigning IPs, etc.)
- [ ] Add support for tagging resources
- [ ] Implement bulk operations
- [ ] Add JSON output format option
- [ ] Create interactive mode
- [ ] Add unit tests

## 📞 Support

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/ednilson-correa/contabo-cloud-manager/issues)
- **Contabo API Docs**: https://api.contabo.com/docs/
- **Contabo Support**: https://contabo.com/en/support/

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This is an unofficial tool and is not affiliated with, maintained, or endorsed by Contabo GmbH. Use at your own risk. Always test in a non-production environment first.

## 🙏 Acknowledgments

- Contabo for providing the API
- The Python community for the excellent libraries

---

**Made with ❤️ by [ednilson-correa](https://github.com/ednilson-correa)**

If you find this tool useful, please consider giving it a ⭐ on GitHub!
