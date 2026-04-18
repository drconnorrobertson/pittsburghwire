# The Pittsburgh Wire — GitHub + Vercel Setup & Daily Publishing Skill

## Step 1: Create Your GitHub Repository

1. Go to github.com and sign up for a free account (or log in)
2. Click the green "New" button to create a new repository
3. Name it: `pittsburghwire`
4. Set it to **Public** (Vercel's free tier works with public repos)
5. Click "Create repository"

## Step 2: Upload Your Site Files

The easiest way with no command line:

1. On your new repo page, click "uploading an existing file"
2. Drag your entire `pittsburghwire` folder contents in
3. Click "Commit changes"

Your repo structure should look like this:
```
pittsburghwire/
  index.html
  about/index.html
  sitemap.xml
  robots.txt
  directory/
    index.html
    primanti-brothers/index.html
    alphabet-city-coffee/index.html
    ... (all 12 business profiles)
  news/
    2026-nfl-draft-pittsburgh-business-impact/index.html
```

## Step 3: Deploy on Vercel

1. Go to vercel.com and sign up with your GitHub account
2. Click "Add New Project"
3. Import your `pittsburghwire` repo
4. Vercel auto-detects it as a static site — click "Deploy"
5. Done. You'll get a live URL like `pittsburghwire.vercel.app` in under 60 seconds

Every time you (or the daily skill) pushes a new file to GitHub, Vercel auto-deploys it. Zero manual steps.

## Step 4: Connect Your Custom Domain

Once you have your domain (pittsburghwire.com or thepittsburghwire.com):

1. In Vercel: Project Settings > Domains > Add Domain
2. Enter your domain
3. Vercel gives you DNS records to add at your registrar (Namecheap/GoDaddy)
4. Add those records, wait up to 1 hour, done

## Step 5: Submit to Google Search Console

1. Go to search.google.com/search-console
2. Add Property > URL prefix > enter your domain
3. Verify ownership via the HTML file method (Vercel makes this easy)
4. Go to Sitemaps > submit `https://yourdomain.com/sitemap.xml`
5. Google will begin crawling within 24-72 hours

---

## The Daily Publishing Skill

Once GitHub + Vercel are live, we build a CoWork skill that runs every morning and does this automatically:

### What it monitors
- Pittsburgh Business Journal new filings
- Allegheny County real estate permits and transactions
- Pittsburgh City Council development approvals
- New business license filings
- Press releases from CMU, UPMC, Pittsburgh Mayor's office

### What it generates each day
- 1 new news article (500-700 words, SEO-optimized, full article template)
- 1 new business profile page if a new business is identified
- Updated sitemap.xml with new URLs added

### How it publishes
1. Skill generates the HTML file
2. Skill calls GitHub API with a personal access token to commit the file
3. Vercel detects the commit and auto-deploys
4. Skill calls Google Search Console API to ping the new URL for indexing
5. Skill posts a Slack notification with what was published

### What you need to give the skill
- GitHub personal access token (Settings > Developer settings > Personal access tokens)
- Google Search Console API key
- Slack webhook URL for the notification

### Files the skill will create
New articles:
`/news/[article-slug]/index.html`

New business profiles:
`/directory/[business-slug]/index.html`

Updated sitemap (appends new URLs):
`/sitemap.xml`

---

## Adding New Business Profiles Manually

Until the skill is live, to add a new business:

1. Copy any existing business profile folder (e.g. `primanti-brothers/`)
2. Rename the folder to the new business slug (e.g. `steel-valley-roasters/`)
3. Edit `index.html` inside:
   - Update all business details (name, owner, category, neighborhood, etc.)
   - Update the JSON-LD structured data block
   - Update the canonical URL
   - Write the story paragraphs
   - Update related businesses
4. Add the new URL to `sitemap.xml`
5. Commit to GitHub
6. Vercel deploys automatically

Naming convention for slugs: all lowercase, words separated by hyphens, no special characters.
Example: "Three Rivers HVAC" = `three-rivers-hvac`

---

## Content Guidelines for The Pittsburgh Wire

**Every article must:**
- Cover something positive about Pittsburgh business, real estate, or development
- Name the specific people involved (owners, founders, operators)
- Include a neighborhood reference
- Have proper SEO meta tags (title, description, canonical)
- Have JSON-LD structured data (NewsArticle schema)
- Be added to sitemap.xml

**Never publish:**
- Crime or legal problems
- Political conflict
- Business closures (unless the building is being replaced by something positive)
- Negativity about the city or its prospects

**Article naming convention:**
`/news/[descriptive-slug]/index.html`
Example: `/news/lawrenceville-coffee-roaster-opens-second-location/index.html`
