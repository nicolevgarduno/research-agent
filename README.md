# Research Digest Agent

Sends you a daily email digest of the research and news most relevant to your specified interests. Allows you to describe what you care about and Claude filters through to find 3-5 articles that are most important. Fully configurable: nothing in this repo is tied to any one person's interests or email provider.

## How it works

Every morning, a GitHub Actions workflow (`.github/workflows/daily.yml`) runs `main.py` on a schedule, which orchestrates four pieces:

1. **`scraper.py`** pulls recent items from arXiv, OSTI.gov, and an Ars Technica RSS feed, based on the search terms you configure.
2. **`main.py`** dedupes those items against `seen_links.json` (a running log of every link already sent, so you never get the same item twice), then hands the fresh ones to the filter.
3. **`filter.py`** sends the fresh items to Claude along with a description of what you care about (your `RESEARCH_INTERESTS`), and gets back the 3-5 most relevant, each with a one-paragraph of why it matters.
4. **`digest.py`** formats the result as an HTML + plaintext email and sends it through your email provider's SMTP server.

**Widening window logic:** if today's fresh items don't yield at least 3 relevant results, `main.py` doesn't just send a short digest — it re-runs the scrape with a wider lookback window (1 → 3 → 7 → 14 days), and falls back to 30 days if all else fails.

`seen_links.json` is committed back to the repo at the end of each run (with entries older than 30 days pruned), so state persists between runs without needing an external database.

## Sources

- arXiv (search terms you define)
- OSTI.gov (keywords you define)
- Ars Technica (tech news RSS. Not configurable, general-interest by design)

## Setup

Everything personal such as your interests, email, and API key live in GitHub Secrets. Forking this repo doesn't expose anyone's actual configuration.

### 1. Get an API key

This project uses Claude (Anthropic) by default to do the filtering — it reads your interests and picks the relevant items. Go to [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys), sign in (or create an account), and generate a new API key.

Prefer a different provider? `filter.py` makes a single, plain HTTP call to `api.anthropic.com/v1/messages` — nothing else in the project depends on it being Claude specifically. Swap in OpenAI, Gemini, or any other model host by pointing that one request at their API instead (updating the URL, headers, and request body to match their format) and keeping everything else — `scraper.py`, `digest.py`, the workflow — exactly as is.

### 2. Set up an email account to send from

Any provider that supports SMTP with an app password works. A few common ones:

| Provider   | SMTP host               | Port | Where to generate an app password                                                                                           |
| ---------- | ----------------------- | ---- | --------------------------------------------------------------------------------------------------------------------------- |
| Gmail      | `smtp.gmail.com`        | 587  | [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (requires 2-Step Verification enabled first) |
| iCloud     | `smtp.mail.me.com`      | 587  | [appleid.apple.com](https://appleid.apple.com) → Sign-In and Security → App-Specific Passwords                              |
| Outlook    | `smtp-mail.outlook.com` | 587  | [account.microsoft.com/security](https://account.microsoft.com/security) → Advanced security options → App passwords        |
| Yahoo Mail | `smtp.mail.yahoo.com`   | 587  | Yahoo Account Info → Account Security → Generate app password                                                               |

If your provider isn't listed, search "`<provider name>` SMTP settings app password".

### 3. Decide what you want this digest to cover

Three things to write out:

- `RESEARCH_INTERESTS` — plain-language description of what you want surfaced. Can be a couple of keywords or a full paragraph; this is what gets sent to Claude to judge relevance.
- `ARXIV_QUERIES` — comma-separated arXiv search terms.
- `OSTI_KEYWORDS` — comma-separated OSTI.gov keywords (leave blank if you don't care about DOE publications specifically).

### 4. Add everything as GitHub secrets

Go to your repo → Settings → Secrets and variables → Actions, and add:

| Secret               | Value                        |
| -------------------- | ---------------------------- |
| `ANTHROPIC_API_KEY`  | From step 1                  |
| `RESEARCH_INTERESTS` | From step 3                  |
| `ARXIV_QUERIES`      | From step 3                  |
| `OSTI_KEYWORDS`      | From step 3 (can be empty)   |
| `EMAIL_ADDRESS`      | Your full email address      |
| `EMAIL_APP_PASSWORD` | The app password from step 2 |
| `SMTP_HOST`          | From the table in step 2     |
| `SMTP_PORT`          | Usually `587`                |

**Example values**:

```
ANTHROPIC_API_KEY:   sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXXXXXX

RESEARCH_INTERESTS: Adversarial machine learning, computer vision security, robotics perception attacks, autonomous systems security

ARXIV_QUERIES: adversarial attack computer vision, acoustic attack camera sensor, object detection adversarial

OSTI_KEYWORDS: adversarial machine learning, AI, cybersecurity

EMAIL_ADDRESS: example@email.com

EMAIL_APP_PASSWORD: abcd-efgh-ijkl-mnop

SMTP_HOST: smtp.gmail.com

SMTP_PORT: 587
```

`ARXIV_QUERIES` and `OSTI_KEYWORDS` are plain-text, comma-separated lists, exactly like the example above. `EMAIL_APP_PASSWORD` won't look like your normal password as most providers generate them as a short string of random letters..

### 5. Schedule

Defaults to 7:00am Mountain Time. Change the cron line in `.github/workflows/daily.yml`:

- MDT (summer): `0 14 * * *`
- MST (winter): `0 15 * * *`
- Or use [crontab.guru](https://crontab.guru) to work out any other time. Cron always runs in UTC.

### 6. Manual test run

Go to the Actions tab in your repo → "Daily Research Digest" → "Run workflow" and you should recieve an email within 10 minutes to test everything works well.

## Local testing

```bash
python -m venv venv
source venv/bin/activate
pip install requests

export ANTHROPIC_API_KEY=your_key_here
export RESEARCH_INTERESTS="describe what you care about here"
export ARXIV_QUERIES="term one, term two, term three"
export OSTI_KEYWORDS="keyword one, keyword two"
export EMAIL_ADDRESS=you@example.com
export EMAIL_APP_PASSWORD=your_app_password
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587

python main.py
```
