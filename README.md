# Delos Client

**Self-hosted VPN and Cloud Service Daemon**

Delos-client is a lightweight, extensible backend service that manages secure remote connections and cloud resources without relying on any external, paid, or proprietary services. Designed for speed, modularity, and full self-ownership, Delos-client operates cleanly across Linux, macOS, and Windows systems (to be fully tested outside Linux).

---

## Features

- **WireGuard VPN Manager**
  - Add, start, stop, and remove WireGuard configurations dynamically.
  - Full API-driven VPN lifecycle management.

- **Rclone Remote Manager**
  - Add, mount, unmount, and remove remote drives.
  - Automates mounting cloud storage or remote NAS resources.

- **FastAPI Background Service**
  - RESTful API access to all features.
  - Clean, structured responses and professional error handling.

- **Cross-platform compatibility**
  - Linux, macOS, and Windows support (service layer adapts automatically).

- **Pluggable architecture**
  - Future modules (e.g., task scheduling, SSH management) designed to integrate cleanly.

- **Zero External Dependency**
  - No third-party orchestration or paid services required.

---

## Quick Start

### Prerequisites
- Python 3.11+
- WireGuard installed (`wg`, `wg-quick`)
- Rclone installed (`rclone`)

### Install
```bash
# Clone the repository
git clone https://github.com/yourusername/delos-client.git
cd delos-client

# Install dependencies
pip install -r requirements.txt
```

### Run Delos
```bash
# From the project root
delos-py$ uvicorn api.restapi:app --host 0.0.0.0 --port 8001
```

or

```bash
./service.py  # python wrapper for starting uvicorn with above creds
```

The API will be available at: `http://127.0.0.1:8001`

Interactive API docs: `http://127.0.0.1:8001/docs`

---

## API Overview

| Method | Endpoint | Description |
|:------|:---------|:------------|
| `POST` | `/vpn/add` | Add a WireGuard config |
| `POST` | `/vpn/start` | Start a VPN config |
| `POST` | `/vpn/stop` | Stop a VPN config |
| `POST` | `/vpn/remove` | Remove a VPN config |
| `GET`  | `/vpn/status` | Get status of VPN configs |

| Method | Endpoint | Description |
|:------|:---------|:------------|
| `POST` | `/rclone/add` | Add an Rclone remote mount |
| `POST` | `/rclone/mount` | Mount a remote drive |
| `POST` | `/rclone/unmount` | Unmount a remote drive |
| `POST` | `/rclone/remove` | Remove an Rclone remote mount |
| `GET`  | `/rclone/status` | Get status of Rclone mounts |

---

## Project Structure

```text
.
├── api/        # FastAPI endpoint routers
├── core/       # Service managers (WireGuard, Rclone)
├── utils/      # Logging, context helpers
├── run.py      # Uvicorn entry point (optional)
```

---

## Roadmap

- [ ] Scheduled Task Manager ("Delos-cron")
- [ ] SSH Session Management
- [ ] Remote Desktop Session Management
- [ ] Lightweight client (Nereid) for GUI control

---

## License

This project is licensed under the MIT License.


---

## Contributing

If you find bugs, have suggestions, or want to contribute, feel free to open an issue or pull request.


> "Delos is about giving control back to the user: your servers, your networks, your data."

