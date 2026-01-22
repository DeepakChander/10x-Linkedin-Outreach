# 10x Outreach Skill Plugin

A comprehensive multi-platform outreach automation plugin for Claude Code.

## Overview

This plugin provides intelligent routing and automation for:
- **Email Campaigns** - Bulk email outreach with Gmail
- **Social Media** - LinkedIn, Twitter, Instagram automation
- **Discovery** - Find people using Exa AI semantic search
- **Analytics** - Track campaign performance
- **Content Marketing** - Create blog posts and social content
- **SEO Optimization** - Keyword research and competitor analysis

## Installation

The plugin is automatically loaded when you open a project containing this folder.

### Requirements

- Claude Code v1.0.0+
- Python 3.9+
- Node.js 18+

### Setup

1. Run the auto-setup script:
   ```bash
   python .claude/scripts/auto_setup.py
   ```

2. Configure environment variables in `.env`

3. Start using skills with `/start`

## Skills

| Skill | Description | MCP |
|-------|-------------|-----|
| `outreach-manager` | Email campaigns | Gmail |
| `discovery-engine` | Find people | Exa |
| `linkedin-adapter` | LinkedIn automation | Browser-Use |
| `twitter-adapter` | Twitter automation | Browser-Use |
| `instagram-adapter` | Instagram automation | Browser-Use |
| `analytics` | Campaign metrics | Internal |
| `content-marketing` | Content creation | Exa |
| `seo-optimization` | SEO research | Exa |

## Hooks

The plugin includes intelligent routing hooks:

- **keyword-router.cjs** - Routes requests based on keywords
- **pre-tool-router.cjs** - Selects optimal MCP for tools
- **context-detector.cjs** - Analyzes user intent

## MCP Integrations

### Exa AI
- Semantic search for people discovery
- Content research
- SEO keyword research

### Browser-Use
- Social platform automation
- Profile-based authentication

### ClaudeKit Extension
- Real-time browser control
- Platform-specific actions

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the visual canvas |
| `/discover` | Find people |
| `/outreach` | Email campaigns |
| `/linkedin` | LinkedIn actions |
| `/twitter` | Twitter actions |
| `/instagram` | Instagram actions |
| `/workflow` | Create/run workflows |
| `/analytics` | View metrics |

## Configuration

See `settings.schema.json` for all configuration options.

## License

MIT License - Free to use, modify, and distribute.
