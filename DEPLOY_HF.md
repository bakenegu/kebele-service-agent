# Deploying to Hugging Face Spaces

This guide will help you deploy the Kebele Service Agent to Hugging Face Spaces for free.

## Step 1: Prepare Your Repository

1. Make sure all files are committed to git:
```bash
git add .
git commit -m "Prepare for Hugging Face Spaces deployment"
```

## Step 2: Create a Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in the details:
   - **Space name**: `kebele-service-agent` (or your preferred name)
   - **SDK**: Select **Gradio**
   - **Hardware**: CPU (free tier) is sufficient
   - **Visibility**: Public or Private (your choice)
4. Click "Create Space"

## Step 3: Push Your Code

You have two options:

### Option A: Using Git (Recommended)

1. In your Space, you'll see instructions to add a remote
2. Add the Hugging Face remote:
```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
# or if using SSH:
git remote add hf git@hf.co:spaces/YOUR_USERNAME/YOUR_SPACE_NAME
```

3. Push your code:
```bash
git push hf main
# or
git push hf master
```

### Option B: Upload Files Directly

1. Go to your Space's "Files" tab
2. Click "Add file" → "Upload files"
3. Upload all necessary files (excluding `.venv`, `__pycache__`, etc.)

## Step 4: Add OpenAI API Key as Secret

1. Go to your Space settings
2. Navigate to "Variables and secrets" tab
3. Click "New secret"
4. Add:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: Your OpenAI API key
5. Click "Add secret"

## Step 5: Wait for Build

Hugging Face Spaces will automatically:
- Install dependencies from `requirements.txt`
- Build your Space
- Launch your app

This usually takes 2-5 minutes. You can monitor the build logs in the "Logs" tab.

## Step 6: Test Your Deployment

Once built, your app will be available at:
```
https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
```

## Important Files for HF Spaces

The following files are required:
- ✅ `app.py` - Entry point (already created)
- ✅ `requirements.txt` - Dependencies (already created)
- ✅ `README.md` or `README_HF.md` - Space description (you can rename)
- ✅ All source files in `src/` directory

## Troubleshooting

### Build Fails
- Check the "Logs" tab for error messages
- Ensure `requirements.txt` has all dependencies
- Verify Python version compatibility (requires Python 3.12+)

### API Key Not Working
- Double-check the secret name is exactly `OPENAI_API_KEY`
- Ensure the secret is set in Space settings, not in code
- Check logs for authentication errors

### App Crashes
- Check logs for runtime errors
- Verify all imports are correct
- Ensure data directories exist (they're created automatically)

## Optional: Custom Domain

If you want a custom domain:
1. Go to Space settings
2. Navigate to "Embed this Space"
3. Configure custom domain (requires Hugging Face Pro)

## Updating Your Space

To update your deployed Space:
```bash
git add .
git commit -m "Update description"
git push hf main
```

The Space will automatically rebuild with your changes.

