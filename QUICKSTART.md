# gdoc-skill Quick Start Guide

Get up and running with **gdoc-fetch** and **gdoc-upload** in 5 minutes!

## 🚀 Quick Installation (3 steps)

### 1. Install the tools

```bash
# Clone the repository
git clone https://github.com/sean-sheng/gdoc-fetcher.git
cd gdoc-fetcher

# Install (installs both gdoc-fetch and gdoc-upload)
pip3 install --user -e .
```

### 2. Authenticate with Google

```bash
# One-time authentication
gcloud auth login --enable-gdrive-access
```

### 3. Test it!

```bash
# Fetch a Google Doc to Markdown
gdoc-fetch "https://docs.google.com/document/d/YOUR_DOC_ID/edit"

# Or upload a Markdown file to create a new Google Doc
gdoc-upload document.md
```

Done! ✅

---

## 📋 Common Usage Patterns

### Fetch (Docs → Markdown)
```bash
gdoc-fetch "<url>" --output-dir .
gdoc-fetch "<url>" --no-images   # skip images (faster)
```

### Upload (Markdown → Docs)
```bash
gdoc-upload document.md
gdoc-upload document.md --title "My Doc"
gdoc-upload document.md --no-images   # skip images (faster)
```

### Use with Claude Code & Gemini CLI

- **Fetch:** Paste a Google Docs URL — the assistant can fetch and read it.
- **Upload:** Ask the assistant to create a Google Doc from a Markdown file — it can run `gdoc-upload` and share the link.

---

## 🔧 Prerequisites Checklist

- [ ] Python 3.10+ installed (`python3 --version`)
- [ ] pip3 installed (`pip3 --version`)
- [ ] gcloud CLI installed (`gcloud --version`)
- [ ] Internet connection

Missing something? See [INSTALLATION.md](INSTALLATION.md) for detailed setup.

---

## 🆘 Quick Troubleshooting

### Command not found?
```bash
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

### Authentication error?
```bash
gcloud auth login --enable-gdrive-access
```

### Module not found?
```bash
pip3 install --user google-api-python-client google-auth markdownify markdown
```

---

## 📚 Learn More

- **Full Installation Guide**: [INSTALLATION.md](INSTALLATION.md)
- **Claude Code & Gemini CLI Integration**: [SKILL.md](SKILL.md)
- **Usage Examples**: [README.md](README.md)

---

## 💡 Pro Tips

1. **Aliases for convenience**:
   ```bash
   alias gfetch='gdoc-fetch'
   alias gupload='gdoc-upload'
   ```

2. **Check what's shared with you**:
   ```bash
   gcloud auth list
   # Make sure the active account matches your Google Docs access
   ```

3. **Use document IDs directly**:
   ```bash
   gdoc-fetch "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
   ```

---

**Need help?** Check [INSTALLATION.md](INSTALLATION.md) for comprehensive troubleshooting.
