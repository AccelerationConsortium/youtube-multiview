# Deployment Guide - AC Hardware Streams

## 🚀 Deployment Options

This application supports multiple deployment platforms with different interfaces and features.

---

## 🤗 Deploy to Hugging Face Spaces (New - Recommended)

### Features
- **Modern Gradio Interface**: Clean, tabbed interface with dark theme
- **Auto-deployment**: GitHub Actions automatically sync changes
- **Embeddable**: Easy to embed in other applications and websites
- **Direct URL**: Clean URLs like `https://accelerationconsortium-youtube-multiview.hf.space`
- **No server management**: Fully managed by Hugging Face

### Prerequisites
1. Create a [Hugging Face](https://huggingface.co) account
2. Create a new Space at https://huggingface.co/new-space
3. Choose "Gradio" as the SDK
4. Get your HF token from https://huggingface.co/settings/tokens

### Setup Steps
1. **Create HF Space**:
   - Go to https://huggingface.co/new-space
   - Name: `youtube-multiview`
   - Owner: `AccelerationConsortium` (or your username)
   - SDK: `Gradio`
   - Visibility: `Public`

2. **Configure GitHub Secrets**:
   - Go to your GitHub repository settings
   - Add secret: `HF_TOKEN` with your HuggingFace token

3. **Automatic Deployment**:
   - Push changes to the main branch
   - GitHub Actions will automatically deploy to HF Spaces
   - Files used: `gradio_app.py`, `requirements-gradio.txt`, `README_HF.md`

### Manual Deployment
```bash
# Clone your HF Space
git clone https://huggingface.co/spaces/your-username/youtube-multiview
cd youtube-multiview

# Copy files
cp gradio_app.py app.py
cp requirements-gradio.txt requirements.txt  
cp README_HF.md README.md

# Deploy
git add .
git commit -m "Deploy Gradio app"
git push
```

---

## ▲ Deploy to Vercel (Original)

### Features
- **Custom Flask Interface**: Advanced UI with modals and zoom functionality
- **Responsive Design**: Optimized for desktop and mobile
- **Fast CDN**: Global edge network for optimal performance

### Prerequisites
1. Push your code to GitHub
2. Create a Vercel account at [vercel.com](https://vercel.com)

### Steps
1. **Connect GitHub to Vercel**
   - Sign up/login to Vercel
   - Click "Import Project"
   - Connect your GitHub account
   - Select the `youtube-multiview` repository

2. **Configure Deployment**
   - Framework: `Other`
   - Root Directory: `./` (default)
   - Build Command: Leave empty
   - Output Directory: Leave empty
   - Install Command: `pip install -r requirements.txt`

3. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Your app will be live at `https://your-project-name.vercel.app`

### Environment Variables (Optional)
If you need any environment variables:
- Go to Project Settings → Environment Variables
- Add any needed variables

---

## 🔄 Deploy to Heroku

### Prerequisites
1. Install Heroku CLI
2. Create Heroku account

### Steps
```bash
# Login to Heroku
heroku login

# Create new app
heroku create ac-hardware-streams

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Open your app
heroku open
```

---

## 🚂 Deploy to Railway

### Steps
1. Go to [railway.app](https://railway.app)
2. Connect GitHub account
3. Click "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Python and deploys

---

## 📄 Static Version (GitHub Pages)

If you want a simpler version that works on GitHub Pages (no add/delete streams):

### Steps
1. Use the `static-index.html` file
2. Enable GitHub Pages in repository settings
3. Select source branch
4. Access at `https://yourusername.github.io/youtube-multiview`

**Note**: Static version will have predefined streams only, no dynamic management.

---

## 🔧 Custom Domain (Any Platform)

After deployment, you can add a custom domain:
- **Vercel**: Project Settings → Domains
- **Heroku**: Settings → Domains  
- **Railway**: Settings → Domains
- **HF Spaces**: Not supported directly

---

## 📊 Comparison Table

| Feature | HF Spaces (Gradio) | Vercel (Flask) | Heroku | Railway |
|---------|-------------------|----------------|---------|---------|
| **Interface** | Modern Gradio tabs | Custom Flask UI | Custom Flask UI | Custom Flask UI |
| **Embedding** | ✅ Easy | ❌ Complex | ❌ Complex | ❌ Complex |
| **Auto-deploy** | ✅ GitHub Actions | ✅ GitHub Integration | ❌ Manual | ✅ GitHub Integration |
| **Cost** | 🆓 Free | 🆓 Free tier | 💰 Paid | 🆓 Free tier |
| **Custom Domain** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| **Performance** | 🔥 Fast | 🔥 Very Fast | 🔄 Medium | 🔥 Fast |
| **Maintenance** | 🔧 Zero | 🔧 Low | 🔧 Medium | 🔧 Low |

---

## 📝 Next Steps

1. **Choose your deployment method** based on your needs:
   - **HF Spaces**: For easy embedding and modern UI
   - **Vercel**: For custom domains and advanced UI features
   
2. **Push to GitHub** (if not already done)
3. **Follow the deployment steps** for your chosen platform
4. **Add your AC logo** to `/static/images/ac-logo.png` (for Vercel)
5. **Test the deployed application**

**Recommendation**: Start with HF Spaces for its ease of use and embedding capabilities, or use Vercel if you need custom domains and advanced UI features.
