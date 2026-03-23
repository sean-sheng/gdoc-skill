# gdoc-skill Installation Tutorial

Complete guide to installing and configuring **gdoc-fetch** and **gdoc-upload** for Claude Code and Gemini CLI.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Google Cloud Authentication](#google-cloud-authentication)
4. [Claude Code & Gemini CLI Integration](#claude-code--gemini-cli-integration)
5. [Testing Your Installation](#testing-your-installation)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before installing gdoc-skill (gdoc-fetch and gdoc-upload), ensure you have:

### Required Software

1. **Python 3.10 or higher**
   ```bash
   python3 --version
   # Should show: Python 3.10.x or higher
   ```

2. **pip (Python package manager)**
   ```bash
   pip3 --version
   # Should show: pip 21.x or higher
   ```

3. **Google Cloud SDK (gcloud CLI)**
   ```bash
   gcloud --version
   # Should show gcloud version info
   ```

   If not installed:
   ```bash
   # macOS
   brew install google-cloud-sdk

   # Linux
   curl https://sdk.cloud.google.com | bash

   # Windows
   # Download from: https://cloud.google.com/sdk/docs/install
   ```

4. **Git**
   ```bash
   git --version
   ```

### System Requirements

- **Operating System**: macOS, Linux, or Windows 10+
- **Disk Space**: ~50MB for installation
- **Internet Connection**: Required for Google Docs API access

---

## Installation Methods

### Method 1: Install from Source (Recommended)

This method gives you the most control and is best for development or customization.

#### Step 1: Clone the Repository

```bash
# Navigate to your preferred installation directory
cd ~/projects  # or wherever you keep your projects

# Clone the repository
git clone https://github.com/sean-sheng/gdoc-fetcher.git
cd gdoc-fetcher
```

#### Step 2: Install the Package

**Option A: User Installation (Recommended)**

```bash
pip3 install --user -e .
```

**Option B: Virtual Environment (Isolated)**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
.\venv\Scripts\activate   # Windows

# Install
pip install -e ".[dev]"
```

**Option C: System-wide (Not Recommended)**

```bash
pip3 install --break-system-packages -e .
```

#### Step 3: Verify Installation

```bash
# Check both commands are available
which gdoc-fetch
which gdoc-upload

# Test the commands
gdoc-fetch --help
gdoc-upload --help
```

You should see help for both: `gdoc-fetch` (fetch Docs → Markdown) and `gdoc-upload` (upload Markdown → Docs).

---

### Method 2: Install via pip (When Published)

Once published to PyPI (not yet done for this project):

```bash
pip3 install --user gdoc-fetch
```

---

## Google Cloud Authentication

Both gdoc-fetch and gdoc-upload use Google Cloud SDK for authentication. This is a **one-time setup**.

### Step 1: Initialize gcloud (First Time Only)

```bash
gcloud init
```

Follow the prompts to:
1. Log in with your Google account
2. Select or create a Cloud project (any project works)

### Step 2: Enable Drive Access

```bash
gcloud auth login --enable-gdrive-access
```

This command:
- Opens a browser window
- Asks you to grant permissions for Google Drive access
- Stores credentials locally at `~/.config/gcloud/`

### Step 3: Verify Authentication

```bash
# Check which account is active
gcloud auth list

# Test token retrieval
gcloud auth print-access-token
```

You should see a long token string (starting with `ya29.`).

### Important Notes

- **Credentials are stored locally** - No API keys needed
- **Shared documents only** - You can only fetch docs shared with your Google account
- **Public docs** - Public documents don't require authentication
- **Organization restrictions** - Respect your org's document sharing policies

---

## Claude Code & Gemini CLI Integration

To use gdoc-skill (gdoc-fetch and gdoc-upload) within Claude Code and Gemini CLI conversations:

### Step 1: Locate Your Skills Directory

```bash
# Find where skills should be installed
# Default location:
ls ~/.claude/skills/

# If it doesn't exist, create it:
mkdir -p ~/.claude/skills/
```

### Step 2: Create a Skill Symlink

**Option A: Symlink (Best for Development)**

```bash
# Create a symlink to your installation
ln -s ~/path/to/gdoc-fetcher ~/.claude/skills/gdoc-fetch

# Verify
ls -la ~/.claude/skills/
```

**Option B: Copy Files**

```bash
# Copy the entire directory
cp -r ~/path/to/gdoc-fetcher ~/.claude/skills/gdoc-fetch

# Verify
ls ~/.claude/skills/gdoc-fetch/SKILL.md
```

### Step 3: Verify the Assistant Can See It

The skill should now be automatically available in Claude Code. For Gemini CLI, run `gemini skills install ~/.claude/skills/gdoc-fetch/SKILL.md --scope user` and then `/skills reload`. The SKILL.md file tells the assistant:
- When to use gdoc-fetch (e.g. when user provides a Google Docs URL)
- When to use gdoc-upload (e.g. when user wants a Markdown file as a Google Doc)
- How to invoke each command and what to expect

### Step 4: Test in Claude Code or Gemini CLI

Start a new conversation in Claude Code or Gemini CLI and try:

```
User: "Here's a spec I need you to review:
       https://docs.google.com/document/d/YOUR_DOC_ID/edit"
```

The assistant should automatically:
1. Recognize the Google Docs URL
2. Invoke `gdoc-fetch` to download it
3. Read the generated markdown
4. Discuss the content with you

For uploads, you can say e.g. "Create a Google Doc from docs/report.md" and the assistant can run `gdoc-upload` and share the new doc link.

---

## Testing Your Installation

### Test 1: Command Line Test

```bash
# Test with a public Google Doc
gdoc-fetch "https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/edit"

# Check the output
ls -la output/
```

Expected output:
```
Extracting document ID from: https://docs.google.com/document/...
Document ID: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms

Authenticating with gcloud...
Authentication successful

Fetching document 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms...
Fetched: Document Title

Converting to Markdown...
Conversion complete

Downloading images...
Found 2 images
Downloaded 2 images successfully

Success! Document written to: output/document-title/document-title.md
```

### Test 2: Authentication Test

```bash
# This should work without errors
gcloud auth print-access-token
```

### Test 3: Python Import Test

```bash
python3 -c "from gdoc_fetch.cli import main; print('✓ gdoc-fetch import OK')"
python3 -c "from gdoc_fetch.cli_upload import main; print('✓ gdoc-upload import OK')"
```

### Test 4: Run Full Test Suite

```bash
cd ~/path/to/gdoc-fetcher

# Install dev dependencies if not already installed
pip3 install --user -e ".[dev]"

# Run tests
PYTHONPATH=. pytest tests/ -v

# Should show: 121 tests passed
```

---

## Troubleshooting

### Issue: "Command not found: gdoc-fetch" or "gdoc-upload"

**Solution 1: Check PATH**
```bash
# Add to your ~/.bashrc or ~/.zshrc:
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

**Solution 2: Use Full Path**
```bash
python3 -m gdoc_fetch.cli "<url>"
python3 -m gdoc_fetch.cli_upload document.md
```

**Solution 3: Reinstall**
```bash
pip3 uninstall gdoc-fetch
pip3 install --user -e ~/path/to/gdoc-fetcher
```

---

### Issue: "ModuleNotFoundError: No module named 'googleapiclient'"

**Problem**: Dependencies not installed

**Solution**:
```bash
cd ~/path/to/gdoc-fetcher
pip3 install --user google-api-python-client google-auth markdownify markdown
```

---

### Issue: "Authentication Error: Could not obtain gcloud access token"

**Problem**: gcloud not authenticated or Drive access not enabled

**Solution**:
```bash
# Re-authenticate with Drive access
gcloud auth login --enable-gdrive-access

# Verify
gcloud auth list
```

---

### Issue: "Document not found (404)" or "Permission denied (403)"

**Problem**: Document not shared with your account

**Solution**:
1. Check that the document URL is correct
2. Make sure the document is shared with your Google account
3. For private docs, ensure you're logged into the right Google account:
   ```bash
   gcloud auth list
   # The ACTIVE account should match the one with document access
   ```

---

### Issue: "Failed to download image"

**Problem**: Image URLs might be expired or restricted

**Solution**:
- The document will still be created without images
- Images are downloaded with authentication, but some may fail
- Check your internet connection
- Try running again (sometimes temporary network issues)

---

### Issue: Claude Code or Gemini CLI doesn't recognize the skill

**Problem**: SKILL.md not in correct location or format issue

**Solution 1: Verify skill location**
```bash
ls ~/.claude/skills/gdoc-fetch/SKILL.md
# Should exist
```

**Solution 2: Check SKILL.md format**
```bash
head -10 ~/.claude/skills/gdoc-fetch/SKILL.md
# Should start with frontmatter (name: gdoc-skill or gdoc-fetch, description mentioning fetch and upload)
```

**Solution 3: Restart the Assistant**
- Exit Claude Code or Gemini CLI completely
- Restart it
- Try again in a new conversation

---

### Issue: Python version too old

**Problem**: Need Python 3.10+

**Solution (macOS)**:
```bash
brew install python@3.11
```

**Solution (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install python3.11
```

---

## Advanced Configuration

### Custom Output Directory

Create a default output directory:

```bash
# In your ~/.bashrc or ~/.zshrc
export GDOC_OUTPUT_DIR="$HOME/Documents/google-docs"
mkdir -p "$GDOC_OUTPUT_DIR"

# Use it:
gdoc-fetch "<url>" --output-dir "$GDOC_OUTPUT_DIR"
```

### Alias for Quick Access

Add to your shell configuration:

```bash
# In ~/.bashrc or ~/.zshrc
alias gfetch='gdoc-fetch'
alias gfetch-here='gdoc-fetch --output-dir .'
alias gupload='gdoc-upload'

# Reload
source ~/.bashrc
```

Now you can use:
```bash
gfetch "<url>"
gfetch-here "<url>"
gupload document.md
```

### Skip Images by Default

Create a wrapper script `~/bin/gdoc-fetch-fast`:

```bash
#!/bin/bash
gdoc-fetch "$@" --no-images
```

```bash
chmod +x ~/bin/gdoc-fetch-fast
```

---

## Uninstallation

If you need to remove gdoc-skill (gdoc-fetch and gdoc-upload):

```bash
# Uninstall the package (removes both CLIs)
pip3 uninstall gdoc-fetch

# Remove the skill from the Assistant
rm -rf ~/.claude/skills/gdoc-fetch
# For Gemini CLI: gemini skills uninstall gdoc-skill

# Remove source directory (optional)
rm -rf ~/path/to/gdoc-fetcher

# Remove gcloud credentials (optional, affects other gcloud tools)
gcloud auth revoke
```

---

## Getting Help

### Check Version and Status

```bash
# Check installation
gdoc-fetch --help

# Check gcloud status
gcloud auth list

# Check Python packages
pip3 list | grep -E 'google|markdownify'
```

### Common Commands Summary

```bash
# Fetch: Docs → Markdown
gdoc-fetch "<url>"
gdoc-fetch "<url>" --output-dir ./my-docs
gdoc-fetch "<url>" --no-images
gdoc-fetch "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"

# Upload: Markdown → Docs
gdoc-upload document.md
gdoc-upload document.md --title "My Doc"
gdoc-upload document.md --no-images

# Re-authenticate
gcloud auth login --enable-gdrive-access

# Test installation
gdoc-fetch --help
gdoc-upload --help
```

---

## Next Steps

Once installed and working:

1. **Try it with your own documents** - Start with a simple doc
2. **Use it in Claude Code or Gemini CLI** - Let the assistant fetch and analyze docs for you
3. **Explore the code** - The codebase is well-documented and tested
4. **Contribute improvements** - Found a bug or have a feature idea? Contribute!

---

## Support & Resources

- **GitHub**: https://github.com/sean-sheng/gdoc-fetcher
- **Documentation**: `SKILL.md` - Claude Code & Gemini CLI integration guide
- **Tests**: `tests/` - 121 comprehensive unit tests
- **Google Cloud SDK**: https://cloud.google.com/sdk/docs
- **Issues**: https://github.com/sean-sheng/gdoc-fetcher/issues

---

**Happy fetching and uploading! 📄✨**
