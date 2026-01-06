# CI/CD Pipeline Documentation

## Overview

This directory contains Gitea Actions workflows for the Homelab Dashboard project.

## Workflows

### CI/CD Pipeline (`ci-cd.yml`)

This workflow runs on:
- Push to `main`, `master`, or `develop` branches
- Pull requests to `main`, `master`, or `develop` branches
- Manual trigger via workflow_dispatch

#### Jobs

1. **Test Job**
   - Runs on every push and pull request
   - Sets up Python 3.12 and Node.js 20
   - Installs dependencies
   - Runs frontend tests (Jest)
   - Runs backend tests (pytest) with coverage
   - Uploads coverage reports to Codecov (optional)

2. **Build and Push Job**
   - Only runs after tests pass
   - Only runs on push to `main` or `master` branches
   - Builds Docker image using Buildx
   - Pushes image to local registry at `registryui.local.kosuiroom.ovh`
   - Tags images with:
     - Branch name
     - Git SHA
     - `latest` (for default branch)

## Setup Requirements

### Gitea Secrets

You need to configure the following secrets in your Gitea repository settings:
(Repository → Settings → Secrets → Actions)

1. **DOCKER_REGISTRY_USERNAME**: Your Docker registry username
2. **DOCKER_REGISTRY_PASSWORD**: Your Docker registry password/token

### Registry Configuration

The pipeline is configured to push to:
```
https://registryui.local.kosuiroom.ovh
```

Image name: `homelab-dashboard`

### Gitea Actions Runner

Ensure you have a Gitea Actions runner set up and registered with your Gitea instance. Since you're using a local registry, the runner should have network access to `registryui.local.kosuiroom.ovh`.

To set up a runner:
```bash
# Download act_runner
# https://gitea.com/gitea/act_runner/releases

# Register the runner
./act_runner register --instance https://your-gitea-url --token YOUR_RUNNER_TOKEN

# Run the runner
./act_runner daemon
```

Or use Docker:
```bash
docker run -d \
  --name gitea-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/act_runner_data:/data \
  -e GITEA_INSTANCE_URL=https://your-gitea-url \
  -e GITEA_RUNNER_REGISTRATION_TOKEN=YOUR_RUNNER_TOKEN \
  gitea/act_runner:latest
```

## Manual Triggering

You can manually trigger the workflow from the Gitea Actions tab:
1. Go to Actions → CI/CD Pipeline
2. Click "Run workflow"
3. Select the branch to run from

## Image Tags

After a successful build, images are tagged as:
- `registryui.local.kosuiroom.ovh/homelab-dashboard:main`
- `registryui.local.kosuiroom.ovh/homelab-dashboard:main-<git-sha>`
- `registryui.local.kosuiroom.ovh/homelab-dashboard:latest` (for main branch)

## Deployment

To deploy the built image:

```bash
docker pull registryui.local.kosuiroom.ovh/homelab-dashboard:latest
docker run -p 8000:8000 registryui.local.kosuiroom.ovh/homelab-dashboard:latest
```

Or update your docker-compose.yml to use the registry image:

```yaml
services:
  app:
    image: registryui.local.kosuiroom.ovh/homelab-dashboard:latest
    # ... rest of configuration
```

## Troubleshooting

### Runner can't access registry
Ensure your Gitea Actions runner has network access to your local registry and trusts the SSL certificate if you're using HTTPS.

### Actions not triggering
Check that:
- Gitea Actions is enabled in your instance settings
- At least one runner is registered and active
- The workflow file is in `.gitea/workflows/` directory
