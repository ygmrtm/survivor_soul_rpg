# Survivor Soul RPG

Survivor Soul RPG is a Lovecraftian-themed RPG survival game built with Python and Flask. It allows players to interact with playable characters, manage tasks and challenges, and explore an adventure-based game interface.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Contributing](#contributing)
- [License](#license)

## Overview
**Version:** 1.0.0  
**Codename:** amlayetnem  
**License:** EULA  

Survivor Soul RPG is a microservices-based RPG game with a Lovecraftian theme, featuring character management, daily tasks and challenges, and an adventure core module. The game integrates with external services like Notion and Todoist to enhance gameplay and task management.

## Features
- **Character Management**: Display and manage characters with attributes like level, XP, HP, attack, defense, and items.
- **Adventure Core**: Generate and execute adventures and challenges.
- **Task Integration**: Manage tasks and challenges using the Todoist SDK.
- **API Integrations**: Interfaces with the Notion API and Todoist API.
- **Docker Deployment**: Easily deployable with Docker containers.
- **CI/CD**: Automated testing and deployment using GitHub Actions.
- **Lovecraftian UI**: Themed frontend for an immersive experience.

## Technologies Used
- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript (for static file management)
- **API Integrations**: Notion API, Todoist SDK
- **Containerization**: Docker
- **CI/CD**: GitHub Actions

## Installation

### Prerequisites
- Python 3.8 or higher
- Docker
- Node.js (for frontend assets if needed)

### Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/survivor-soul-rpg.git
   cd survivor-soul-rpg
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```plaintext
   FLASK_ENV=development
   NOTION_API_KEY=your_notion_api_key
   TODOIST_API_KEY=your_todoist_api_key
   ```

4. **Run the Flask app**:
   ```bash
   flask run
   ```

5. **Run Docker container** (optional, local):
   ```bash
   docker build -t survivor-soul-rpg .
   docker run --env-file .env -p 5000:5000 survivor-soul-rpg
   ```

## Production Deployment

Production runs as a Docker container on your server. Releases are built in GitHub Actions, pushed to GitHub Container Registry (GHCR), and deployed over SSH.

### One-time server setup

1. Install Docker and Docker Compose on the production host.
2. Create the app directory:
   ```bash
   sudo mkdir -p /opt/survivor-soul-rpg
   sudo chown "$USER":"$USER" /opt/survivor-soul-rpg
   ```
3. Copy environment variables:
   ```bash
   cp .env.example /opt/survivor-soul-rpg/.env
   # Edit /opt/survivor-soul-rpg/.env with production secrets
   ```
4. Log in to GHCR on the server (needed if the package is private):
   ```bash
   echo "$GHCR_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
   ```

### GitHub secrets

Configure these repository secrets before running a release:

| Secret | Purpose |
|--------|---------|
| `DEPLOY_HOST` | Production server hostname or IP |
| `DEPLOY_USER` | SSH user on the production server |
| `DEPLOY_SSH_KEY` | Private SSH key for deployment |
| `GHCR_TOKEN` | GitHub PAT with `read:packages` (for private images) |

### Release workflow

1. Open **Actions → Release → Run workflow** on `main`.
2. Choose a version bump (`patch`, `minor`, `major`, or `none`).
3. The workflow will:
   - run tests
   - bump `VERSION.txt` and tag the release (unless bump is `none`)
   - build and push `ghcr.io/ygmrtm/survivor_soul_rpg:<version>` and `:latest`
   - copy `docker-compose.prod.yml` and `scripts/deploy.sh` to the server
   - pull the new image and restart the container

You can also trigger a release by pushing a tag such as `v1.2.3`.

### Manual deploy on the server

```bash
cd /opt/survivor-soul-rpg
export APP_VERSION=1.2.3   # or latest
./scripts/deploy.sh "$APP_VERSION"
```

Health check: `GET /api/adventure/version`

## Configuration

All configurations are managed in `config.py`. Set environment variables in `.env` for sensitive keys (e.g., API keys for Notion and Todoist).

## Usage

Once the app is running, you can access the **landing page** at `http://localhost:5000/`. The API endpoints can be accessed under `/api/`.

## Endpoints

### Notion Endpoints
- `GET /api/notion/characters`: Retrieve all characters.
- `PUT /api/notion/character/<id>`: Update a character.
- `GET /api/notion/characters/deep-level/<level>`: Filter characters by depth level.

### Adventure Core Endpoints
- `POST /api/adventure`: Create a new adventure.
- `POST /api/adventure/execute`: Execute an adventure.
- `POST /api/adventure/challenge`: Create a new challenge.
- `GET /api/adventure/challenges`: Retrieve challenges within a date range.

### Todoist Endpoints
- `POST /api/todoist/task`: Create a new task in Todoist.

## Contributing

1. **Fork** the project.
2. **Create** your feature branch (`git checkout -b feature/YourFeature`).
3. **Commit** your changes (`git commit -m 'Add YourFeature'`).
4. **Push** to the branch (`git push origin feature/YourFeature`).
5. **Open a Pull Request**.

Please review `CONTRIBUTING.md` for more details on coding standards and best practices.

## License

This project is licensed under the End User License Agreement (EULA). See `LICENSE` for more details.
```

---

These files should provide the foundation for project documentation, making it easy for others to understand, contribute to, and deploy the app. Let me know if you’d like to add further details or features!