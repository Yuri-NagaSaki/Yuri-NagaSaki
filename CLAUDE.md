# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a dynamic GitHub profile README automation system that automatically updates a GitHub profile page with the latest starred repositories and WordPress blog posts. The system uses Python scripts with GitHub Actions to periodically fetch data from APIs and update the README.md file with formatted content.

## Architecture

### Core Components
- **GitHub API Integration**: Fetches recently starred repositories using GitHub's REST API
- **WordPress API Integration**: Gets latest blog posts from WordPress REST API (optional)
- **README Generation**: Dynamically updates README.md with formatted cards and statistics
- **GitHub Actions Automation**: Scheduled workflow for automatic updates

### Project Structure
```
├── scripts/                    # Python automation scripts
│   ├── update_readme.py       # Main orchestration script
│   ├── github_api.py          # GitHub API client and formatting
│   └── test_config.py         # Configuration testing utility
├── .github/workflows/         # GitHub Actions automation
│   └── update-readme.yml      # Scheduled update workflow
├── requirements.txt           # Python dependencies
├── README.md                  # Dynamic profile page (auto-generated)
└── SETUP.md                   # Setup and configuration guide
```

### Key Technologies
- **Python 3.11**: Core automation language
- **aiohttp**: Async HTTP client for API calls
- **GitHub Actions**: Automation and scheduling platform
- **GitHub API**: Repository and user data source
- **WordPress REST API**: Blog content source (optional)

## Development Commands

### Local Development
```bash
# Install Python dependencies
pip install -r requirements.txt

# Test all API configurations
python scripts/test_config.py

# Run manual README update
python scripts/update_readme.py

# Test individual API modules
python -c "from scripts.github_api import test_github_connection; import asyncio; asyncio.run(test_github_connection('username', 'token'))"
```

### Configuration Testing
```bash
# Interactive configuration test (prompts for missing values)
python scripts/test_config.py

# Test with environment variables
export GH_USERNAME="your-username"
export GH_TOKEN="your-token"
python scripts/test_config.py
```

### GitHub Actions Workflow
- **Automatic**: Runs daily at 2:00 UTC via cron schedule
- **Manual**: Can be triggered via GitHub Actions "Run workflow" button
- **Push Trigger**: Runs on pushes to master branch

## Required Configuration

### GitHub Secrets (Required)
The following secrets must be configured in repository Settings > Secrets and variables > Actions:

| Secret | Description | Required |
|--------|-------------|----------|
| `GH_USERNAME` | GitHub username for the profile | Yes |
| `GH_TOKEN` | GitHub Personal Access Token with repo access | Yes |
| `WORDPRESS_URL` | WordPress site URL for blog integration | Optional |

### Environment Variables for Local Development
```bash
export GH_USERNAME="your-github-username"
export GH_TOKEN="ghp_your-github-token"
export WORDPRESS_URL="https://yourblog.com"
```

## API Integration Details

### GitHub API (`github_api.py`)
- Fetches recently starred repositories with metadata
- Supports pagination and rate limiting
- Returns formatted repository cards with language colors and icons
- Handles authentication errors and API limits

### README Update Process (`update_readme.py`)
- Orchestrates GitHub API calls asynchronously
- Updates README.md sections between comment markers
- Preserves manual content outside automation markers
- Updates timestamp and handles formatting errors gracefully

## Content Sections

The README.md includes these dynamically updated sections:

### GitHub Stars Section
```html
<!-- GITHUB_STARS:START -->
<!-- Content auto-generated from recently starred repos -->
<!-- GITHUB_STARS:END -->
```

### Update Timestamp
```html
<!-- UPDATE_TIME:START -->2025-01-01 12:00:00 UTC<!-- UPDATE_TIME:END -->
```

## Layout Optimizations

The README layout has been optimized for better visual presentation:

- **GitHub Statistics**: Arranged in a responsive table layout with stats and streak side-by-side
- **Profile Badges**: Updated with correct username references
- **Enhanced Parameters**: Added `include_all_commits=true`, `count_private=true`, and `langs_count=8` for comprehensive stats
- **Improved Accessibility**: Better alt text and semantic structure

## Customization

### Modify Display Limits
Edit limits in `scripts/update_readme.py`:
```python
stars_data = await get_recent_stars(github_username, github_token, limit=5)
```

### Update Schedule
Modify cron schedule in `.github/workflows/update-readme.yml`:
```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2:00 UTC
```

### Styling Customization
- Card styles defined in individual API modules
- Language colors and icons in `github_api.py:get_language_color()`
- Modern gradient backgrounds and responsive layouts

## Error Handling

The system includes comprehensive error handling:
- API rate limiting and timeout management
- Graceful fallbacks for missing optional data
- Configuration validation and testing utilities
- Detailed error logging in GitHub Actions