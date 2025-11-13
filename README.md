# 30 Days of Web Dev

Web development learning resources and documentation built with MkDocs.

## Local Setup

1. **Create and activate a virtual environment** (recommended to avoid permission issues):
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate it (Windows PowerShell)
   venv\Scripts\Activate.ps1
   
   # Or use the Python directly
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. **Install Python dependencies:**
   ```bash
   # If virtual environment is activated
   pip install -r requirements.txt
   
   # Or using venv Python directly
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. **Serve the documentation locally:**
   ```bash
   # If virtual environment is activated
   mkdocs serve
   
   # Or using venv Python directly
   .\venv\Scripts\python.exe -m mkdocs serve
   ```
   The site will be available at `http://127.0.0.1:8000`

4. **Build the static site:**
   ```bash
   # If virtual environment is activated
   mkdocs build
   
   # Or using venv Python directly
   .\venv\Scripts\python.exe -m mkdocs build
   ```
   The built site will be in the `site/` directory.

## Deploying to GitHub Pages

Your site is configured for automatic deployment to GitHub Pages!

### First-time Setup:

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Initial MkDocs setup"
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Click **Settings** → **Pages**
   - Under **Source**, select **GitHub Actions**
   - The workflow will automatically deploy your site

3. **Update repository URL in `mkdocs.yml`:**
   - Open `mkdocs.yml`
   - Replace `yourusername` with your actual GitHub username
   - Uncomment and update the `site_url` line with your GitHub Pages URL
   - Format: `https://yourusername.github.io/30DaysOfWebDev`

4. **Commit and push the changes:**
   ```bash
   git add mkdocs.yml
   git commit -m "Update repository URL"
   git push origin main
   ```

### Automatic Deployment:

After the initial setup, every time you push to the `main` branch, GitHub Actions will automatically:
- Build your MkDocs site
- Deploy it to GitHub Pages

Your site will be available at: `https://yourusername.github.io/30DaysOfWebDev`

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── deploy.yml    # GitHub Actions deployment workflow
├── docs/                 # Documentation source files
│   ├── images/          # Image assets
│   └── index.md         # Main documentation page
├── mkdocs.yml           # MkDocs configuration
└── requirements.txt     # Python dependencies
```

## Adding New Content

1. Add markdown files to the `docs/` directory
2. Update `mkdocs.yml` to include new pages in the navigation
3. Add images to `docs/images/` and reference them with `images/filename.png`
4. Commit and push - deployment happens automatically!

