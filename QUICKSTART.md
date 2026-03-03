# gdoc-fetch Quick Start Guide

Get up and running with gdoc-fetch in 5 minutes!

## 🚀 Quick Installation (3 steps)

### 1. Install the tool

```bash
# Navigate to the project
cd /path/to/gdoc-skill

# Install
pip3 install --user -e .
```

### 2. Authenticate with Google

```bash
# One-time authentication
gcloud auth login --enable-gdrive-access
```

### 3. Test it!

```bash
# Fetch a public Google Doc
gdoc-fetch "https://docs.google.com/document/d/YOUR_DOC_ID/edit"
```

Done! ✅

---

## 📋 Common Usage Patterns

### Fetch to current directory
```bash
gdoc-fetch "<url>" --output-dir .
```

### Skip images (faster)
```bash
gdoc-fetch "<url>" --no-images
```

### Use with Claude Code

Just paste a Google Docs URL in your conversation:
```
You: "Review this spec: https://docs.google.com/document/d/..."
Claude: [automatically fetches and reads the document]
```

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
pip3 install --user google-api-python-client google-auth markdownify
```

---

## 📚 Learn More

- **Full Installation Guide**: [INSTALLATION.md](INSTALLATION.md)
- **Claude Code Integration**: [SKILL.md](SKILL.md)
- **Usage Examples**: [README.md](README.md)

---

## 💡 Pro Tips

1. **Alias for convenience**:
   ```bash
   alias gfetch='gdoc-fetch'
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
