# Webflow Scheduled Publisher

Automatically publish Webflow CMS articles on a schedule using GitHub Actions.

**Cost:** FREE (public repository)

## How It Works

1. Articles are uploaded to Webflow as **drafts**
2. `schedule.json` contains the publish dates
3. GitHub Actions runs daily at 9 AM Montreal time
4. Script checks if any articles are scheduled for today
5. If yes → publishes them via Webflow API

## Setup Instructions

### Step 1: Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Name: `webflow-scheduler` (or any name you like)
3. **Important:** Select **Public** (for free Actions)
4. Click "Create repository"

### Step 2: Upload Files

**Option A: Via GitHub Web UI**
1. Click "uploading an existing file"
2. Drag all files from this folder
3. Commit

**Option B: Via Terminal**
```bash
cd "/Users/ariel/odrive/Dropbox Physioactif/Admin/Marketing/Site web 2025/webflow-scheduler"
git init
git add .
git commit -m "Initial commit: Webflow scheduler"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/webflow-scheduler.git
git push -u origin main
```

### Step 3: Add Webflow API Token as Secret

1. In your GitHub repo, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `WEBFLOW_API_TOKEN`
4. Value: Your Webflow API token (from Webflow Dashboard → Site Settings → Apps & Integrations → API Access)
5. Click "Add secret"

### Step 4: Get Your Site ID

Run this command to find your Webflow site ID:
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" https://api.webflow.com/v2/sites
```

Then update `schedule.json` with the `site_id`.

### Step 5: Upload Articles as Drafts

1. Upload your articles to Webflow CMS (they will be drafts by default)
2. Get each article's `item_id` from the Webflow CMS URL or API
3. Update `schedule.json` with the real `item_id` values

### Step 6: Verify Setup

1. Go to your GitHub repo → **Actions** tab
2. Click "Publish Scheduled Articles"
3. Click "Run workflow" → Check "Dry run" → "Run workflow"
4. This will show your schedule without publishing anything

## Schedule Format

```json
{
  "name": "Article Title",
  "slug": "article-slug",
  "collection": "Guide Complet",
  "collection_id": "67c0ab311dc962020babaa51",
  "item_id": "abc123def456",
  "publish_date": "2025-12-23",
  "published": false
}
```

## Collection IDs (Physioactif)

| Collection | ID |
|------------|-----|
| Guide Complet | `67c0ab311dc962020babaa51` |
| Ressources | `67165e64411a14330fa9c958` |
| Pathologies | `67100554f23d3e6c49ad7bbd` |

## Manual Trigger

You can manually run the workflow anytime:
1. Go to **Actions** → "Publish Scheduled Articles"
2. Click "Run workflow"
3. Uncheck "Dry run" to actually publish
4. Click "Run workflow"

## Modify Schedule

To add/change articles:
1. Edit `schedule.json` in GitHub
2. Commit the change
3. The new schedule takes effect immediately

## Timezone

The workflow runs at **9:00 AM Montreal time**.

- Winter (EST): 14:00 UTC
- Summer (EDT): 13:00 UTC

The current cron is set for winter. To adjust for summer, edit `.github/workflows/publish.yml`.

## Troubleshooting

**"No articles scheduled for today"**
- Check that `publish_date` in schedule.json matches today's date (YYYY-MM-DD format)

**"WEBFLOW_API_TOKEN not set"**
- Verify the secret is added in GitHub repo settings

**Articles not appearing on site**
- The script publishes items AND the site
- Check Webflow dashboard to verify

## Security Note

- API token is stored as a GitHub Secret (encrypted)
- Never commit API tokens to code
- Public repo is safe because secrets are not exposed

---

Created for Physioactif content publishing automation.
