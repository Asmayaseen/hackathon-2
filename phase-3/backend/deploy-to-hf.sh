#!/bin/bash
# Hugging Face Space Deployment Script
# Usage: ./deploy-to-hf.sh

set -e

echo "🚀 Deploying Evolution Todo Backend to Hugging Face Spaces"
echo "============================================================"

# Check if HF_USERNAME is set
if [ -z "$HF_USERNAME" ]; then
    echo "❌ Error: HF_USERNAME environment variable not set"
    echo "   Please set it: export HF_USERNAME=your-hf-username"
    exit 1
fi

# Space name
SPACE_NAME="evolution-todo-api"
HF_SPACE_URL="https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"

echo ""
echo "📝 Deployment Details:"
echo "   - Space: $HF_USERNAME/$SPACE_NAME"
echo "   - URL: $HF_SPACE_URL"
echo ""

# Check if huggingface_hub is installed
if ! python3 -c "import huggingface_hub" 2>/dev/null; then
    echo "📦 Installing huggingface_hub..."
    pip install -q huggingface_hub
fi

# Login to HF (if not already logged in)
echo "🔐 Checking Hugging Face authentication..."
if ! huggingface-cli whoami >/dev/null 2>&1; then
    echo "   Please login to Hugging Face:"
    huggingface-cli login
fi

# Create deployment directory
DEPLOY_DIR=$(mktemp -d)
echo "📁 Preparing deployment files in $DEPLOY_DIR"

# Copy necessary files
cp -r . "$DEPLOY_DIR/"
cd "$DEPLOY_DIR"

# Remove unnecessary files
rm -rf __pycache__ .pytest_cache .env deploy-to-hf.sh

# Ensure README_HF.md is named README.md for HF
mv README_HF.md README.md

echo "📤 Uploading to Hugging Face Space..."
python3 <<EOF
from huggingface_hub import HfApi, create_repo
import os

api = HfApi()
username = "$HF_USERNAME"
repo_id = f"{username}/$SPACE_NAME"

# Create repo if it doesn't exist
try:
    create_repo(repo_id, repo_type="space", space_sdk="docker", exist_ok=True)
    print(f"✅ Space created/verified: {repo_id}")
except Exception as e:
    print(f"❌ Error creating space: {e}")
    exit(1)

# Upload all files
try:
    api.upload_folder(
        folder_path=".",
        repo_id=repo_id,
        repo_type="space",
        commit_message="🚀 Deploy Phase 3: Voice + AI Chat + Language Support"
    )
    print(f"✅ Files uploaded successfully!")
except Exception as e:
    print(f"❌ Error uploading files: {e}")
    exit(1)
EOF

# Cleanup
cd -
rm -rf "$DEPLOY_DIR"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Go to: $HF_SPACE_URL/settings"
echo "   2. Add these secrets in 'Repository secrets':"
echo "      - DATABASE_URL (your Neon PostgreSQL connection string)"
echo "      - JWT_SECRET (any secure random string)"
echo "      - CORS_ORIGINS (your Vercel frontend URL)"
echo "      - GROQ_API_KEY (your Groq API key)"
echo "      - GROQ_BASE_URL=https://api.groq.com/openai/v1"
echo ""
echo "   3. Wait for the Space to build (check 'Logs' tab)"
echo "   4. Test your API at: https://$HF_USERNAME-$SPACE_NAME.hf.space/docs"
echo ""
echo "🎉 Happy deploying!"
