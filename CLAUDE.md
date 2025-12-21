# CLAUDE.md

Instructions for Claude Code when working in this repository.

## Project Overview

**Site:** resurrexi.io
**Purpose:** Main Resurrexi Labs site - research overview, publications, technical projects, and compute access.

**Architecture:** Flask backend with Jinja2 templating. Static site generation for deployment. Hosted on K3s cluster via Cloudflare Tunnel.

## Brand Position

**Resurrexi Labs** is the technical infrastructure and research hub. The compute backbone.

**This site hosts:** Research overview, publication listings, technical project showcase, compute interest forms.

**NOT:** Paper details (→ farzulla.org), blog posts (→ resurrexi.dev), personal content (→ farzulla.com), governance research (→ dissensus.ai)

## Site Structure

```
resurrexi-io/
├── templates/           # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── infrastructure.html
│   ├── experiments.html
│   └── dashboards.html
├── content/             # Markdown content (if used)
├── static/              # CSS, images
├── public/              # Generated static output
│   ├── *.html
│   └── sitemap.xml
├── dashboards/          # Dashboard integrations
├── k8s/                 # Kubernetes manifests
├── app.py               # Flask application
├── build.py             # Static site generator
├── deploy.sh            # Deployment script
├── Dockerfile           # Container build
├── requirements.txt     # Python dependencies
└── wrangler.jsonc       # Cloudflare config
```

## Development

**Flask dev server:**
```bash
pip install -r requirements.txt
python app.py
# Access at http://localhost:5000
```

**Static build:**
```bash
python build.py
```

## Deployment

**K8s deployment:**
```bash
kubectl apply -f k8s/
kubectl -n resurrexi-io get pods,svc
# NodePort: 30801
```

**Manual rsync:**
```bash
./deploy.sh
# Syncs public/ to SudoSenpai:/mnt/storage/resurrexi-io/
```

**Docker:**
```bash
docker build -t resurrexi-io:latest .
docker run -p 5000:5000 resurrexi-io:latest
```

## Site Pages

- `/` - Homepage (research overview)
- `/infrastructure.html` - Cluster infrastructure details
- `/experiments.html` - Ongoing experiments
- `/dashboards.html` - Live dashboards (ASRI, etc.)

## Dashboards

ASRI (Aggregated Systemic Risk Index) dashboard available at `/dashboards/asri/`

## Form Handling

Compute interest forms submit to Flask backend, saved as JSON in `submissions/`:

```json
{
  "name": "Researcher Name",
  "email": "email@example.com",
  "institution": "University",
  "research_area": "ai-ml",
  "project_description": "...",
  "submitted_at": "2025-11-24T16:00:00"
}
```

## Tech Stack

- Python 3.13
- Flask 3.0
- Jinja2 (templating)
- Pico CSS (styling)
- Kubernetes (deployment)
- Cloudflare Tunnel (ingress)

## Infrastructure Context

Runs on the Frankencluster:
- **SudoSenpai** - K3s control plane, storage server
- **CronCrunch** - K3s worker with GTX 1080
- **PurrPower** - Beast workstation, LM Studio
- Storage: PersistentVolumes on SudoSenpai

## Design System

**Aesthetic:** Clean, professional, but with technical edge.

**Colors:**
- Uses Pico CSS defaults
- Custom RSX branding elements

## Content Guidelines

**Tone:** Professional but not corporate. Technical competence without marketing speak.

**Focus areas:**
- Offensive security research
- Infrastructure engineering
- Autonomous AI agents
- Financial modeling

## Links

- Technical docs: resurrexi.dev
- Research papers: farzulla.org
- Governance research: dissensus.ai
- Personal: farzulla.com
- GitHub: github.com/resurrexio

## What NOT to Do

- Don't add blog functionality (use resurrexi.dev)
- Don't duplicate paper abstracts (link to farzulla.org)
- Don't expose sensitive infrastructure details
- Don't use the form endpoint for anything except compute interest

---

**Last Updated:** December 2025
