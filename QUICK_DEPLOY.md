# Quick Deploy to Hugging Face Spaces

## 🚀 Fast Track (5 minutes)

1. **Create Space on HF**:
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Name: `kebele-service-agent`
   - SDK: **Gradio**
   - Hardware: **CPU Basic** (free)

2. **Push Code**:
```bash
# Add HF remote (replace YOUR_USERNAME and SPACE_NAME)
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/kebele-service-agent

# Push code
git push hf main
```

3. **Add API Key Secret**:
   - Go to Space → Settings → Variables and secrets
   - Add secret: `OPENAI_API_KEY` = `your_openai_key`

4. **Wait 2-5 minutes** for build

5. **Done!** Your app is live at:
   `https://huggingface.co/spaces/YOUR_USERNAME/kebele-service-agent`

## 📋 Required Files (Already Created)

✅ `app.py` - Entry point  
✅ `requirements.txt` - Dependencies  
✅ `README_HF.md` - Space description (rename to README.md if needed)  
✅ All `src/` files  

## ⚠️ Important

- **API Key**: Must be added as a secret named `OPENAI_API_KEY`
- **Python Version**: Requires Python 3.12+ (HF Spaces default is usually fine)
- **Data Directories**: Created automatically on first run

## 🔧 Troubleshooting

**Build fails?** Check Logs tab for errors  
**API key error?** Verify secret name is exactly `OPENAI_API_KEY`  
**Import errors?** Ensure all files in `src/` are uploaded  

See `DEPLOY_HF.md` for detailed instructions.

