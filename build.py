#!/usr/bin/env python3
"""
Static site generator for resurrexi.io
Research infrastructure site with experiments, infrastructure specs, and about
"""

from pathlib import Path
import shutil
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
CONTENT_DIR = BASE_DIR / "content"
STATIC_DIR = BASE_DIR / "static"
PUBLIC_DIR = BASE_DIR / "public"

# Setup Jinja2
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content"""
    if content.startswith('---'):
        try:
            _, frontmatter, body = content.split('---', 2)
            metadata = yaml.safe_load(frontmatter)
            return metadata, body.strip()
        except ValueError:
            return {}, content
    return {}, content

def build_pages():
    """Build static pages"""
    pages = [
        'index.html',
        'about.html',
        'infrastructure.html',
        'experiments.html',
        'compute.html',  # Keep for when it's ready, just not linked
    ]

    for page in pages:
        try:
            template = env.get_template(page)
            output = template.render(year=datetime.now().year)
            (PUBLIC_DIR / page).write_text(output)
            print(f"Built {page}")
        except Exception as e:
            print(f"Warning: Could not build {page}: {e}")

def copy_static():
    """Copy static assets"""
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, PUBLIC_DIR / "static", dirs_exist_ok=True)
        print("Copied static assets")

def copy_apps():
    """Copy embedded React apps"""
    # ASRI Dashboard
    asri_dist = BASE_DIR.parent.parent / "resurrexi-projects" / "asri" / "frontend" / "dist"
    if asri_dist.exists():
        shutil.copytree(asri_dist, PUBLIC_DIR / "asri", dirs_exist_ok=True)
        print("Copied ASRI dashboard")

def main():
    """Build the entire site"""
    print("Building resurrexi.io...")

    # Clean and recreate public directory
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_DIR.mkdir()

    # Build all pages
    build_pages()
    copy_static()
    copy_apps()

    print("\n✓ Build complete!")
    print(f"Output: {PUBLIC_DIR}")

if __name__ == "__main__":
    main()
