# Research Digest Agent

Sends a daily email of the most relevant AI security / computer vision research,
filtered by Claude to your specific interests.

## Sources
- arXiv (CS papers — CV attacks, adversarial ML, AI security)
- OSTI.gov (DOE publications)
- Ars Technica (tech news RSS)

## Setup

### 1. GitHub secrets required
Go to your repo → Settings → Secrets and variables → Actions:

| Secret | Value |
|--------|-------|
| `ANTHROPIC_API_KEY` | Your key from console.anthropic.com |
| `ICLOUD_ADDRESS` | Your @icloud.com address |
| `ICLOUD_APP_PASSWORD` | App-specific password from appleid.apple.com |

### 2. Schedule
Runs at 7:00am Mountain Time (MDT, UTC-7).
Change the cron line in `.github/workflows/daily.yml` if needed:
- MDT (summer): `0 14 * * *`
- MST (winter): `0 15 * * *`

### 3. Manual test run
Go to Actions tab in your repo → "Daily Research Digest" → "Run workflow"

## Local testing
```bash
python -m venv venv
source venv/bin/activate
pip install requests

export ANTHROPIC_API_KEY=your_key_here
export ICLOUD_ADDRESS=you@icloud.com
export ICLOUD_APP_PASSWORD=your_app_password

python main.py
```
