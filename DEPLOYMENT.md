# Deploying CodeLens AI to Render.com

## Prerequisites

1. GitHub account with your code pushed
2. Render.com account (free tier available)
3. MongoDB Atlas account (free tier) - for database
4. Google Gemini API key

---

## Step-by-Step Deployment Guide

### Part 1: Setup MongoDB Atlas (5 minutes)

1. **Go to MongoDB Atlas**
   - Visit: https://www.mongodb.com/cloud/atlas/register
   - Sign up for free account

2. **Create a Cluster**
   - Click "Build a Database"
   - Choose "FREE" tier (M0)
   - Select region closest to you
   - Click "Create Cluster"

3. **Create Database User**
   - Go to "Database Access"
   - Click "Add New Database User"
   - Username: `codelens`
   - Password: Generate secure password (save it!)
   - Database User Privileges: "Read and write to any database"
   - Click "Add User"

4. **Allow Network Access**
   - Go to "Network Access"
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
   - Click "Confirm"

5. **Get Connection String**
   - Go to "Database" → "Connect"
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database password
   - Example: `mongodb+srv://codelens:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/codelens_ai?retryWrites=true&w=majority`

---

### Part 2: Deploy Backend to Render (10 minutes)

1. **Go to Render Dashboard**
   - Visit: https://render.com
   - Sign up / Log in with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `jshree14/CodeLens-`
   - Click "Connect"

3. **Configure Backend Service**
   ```
   Name: codelens-backend
   Region: Oregon (US West)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

4. **Add Environment Variables**
   Click "Advanced" → "Add Environment Variable"
   
   Add these variables:
   ```
   GEMINI_API_KEY = your_gemini_api_key_here
   MONGODB_URL = your_mongodb_connection_string_here
   DATABASE_NAME = codelens_ai
   DEBUG = False
   CORS_ORIGINS = *
   HOST = 0.0.0.0
   PORT = 10000
   ```

5. **Deploy Backend**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Note your backend URL: `https://codelens-backend.onrender.com`

6. **Test Backend**
   - Visit: `https://codelens-backend.onrender.com/api/health`
   - Should see: `{"status":"healthy",...}`

---

### Part 3: Deploy Frontend to Render (10 minutes)

1. **Create Another Web Service**
   - Click "New +" → "Web Service"
   - Select same repository: `jshree14/CodeLens-`

2. **Configure Frontend Service**
   ```
   Name: codelens-frontend
   Region: Oregon (US West)
   Branch: main
   Root Directory: (leave empty)
   Runtime: Node
   Build Command: npm install && npm run build
   Start Command: npm run preview -- --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

3. **Add Environment Variable**
   ```
   VITE_API_URL = https://codelens-backend.onrender.com
   ```

4. **Deploy Frontend**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Note your frontend URL: `https://codelens-frontend.onrender.com`

---

### Part 4: Update CORS Settings

1. **Update Backend Environment Variables**
   - Go to your backend service on Render
   - Click "Environment"
   - Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS = https://codelens-frontend.onrender.com
   ```
   - Click "Save Changes"
   - Backend will auto-redeploy

---

### Part 5: Update Frontend API URL

1. **Create API Configuration File**
   
   You need to update your frontend to use the backend URL.
   
   In `src/App.jsx`, update the API URL:
   ```javascript
   const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
   ```

2. **Push Changes to GitHub**
   ```bash
   git add .
   git commit -m "feat: add production API configuration"
   git push
   ```

3. **Render will auto-deploy** the changes

---

## Testing Your Deployment

1. **Visit Frontend**
   - Go to: `https://codelens-frontend.onrender.com`
   - Should see the CodeLens AI interface

2. **Test Code Analysis**
   - Paste some Python code
   - Click "Analyze Code"
   - Should see results (may take 30-60 seconds on free tier)

3. **Check Backend Health**
   - Visit: `https://codelens-backend.onrender.com/api/health`
   - Should return healthy status

---

## Important Notes

### Free Tier Limitations

1. **Cold Starts**
   - Services sleep after 15 minutes of inactivity
   - First request after sleep takes 30-60 seconds
   - Subsequent requests are fast

2. **Build Minutes**
   - Free tier: 750 hours/month
   - Enough for 2 services running 24/7

3. **Bandwidth**
   - 100 GB/month free
   - Should be sufficient for moderate use

### Performance Tips

1. **Keep Services Warm**
   - Use a service like UptimeRobot to ping your app every 14 minutes
   - Prevents cold starts

2. **Optimize Build Time**
   - Cache dependencies
   - Use smaller Docker images (if upgrading)

3. **Database Connection**
   - MongoDB Atlas free tier is sufficient
   - Consider upgrading if you have many users

---

## Troubleshooting

### Backend Won't Start

**Check Logs:**
- Go to Render Dashboard → Backend Service → Logs
- Look for errors

**Common Issues:**
- Missing environment variables
- MongoDB connection string incorrect
- Python version mismatch

**Solutions:**
- Verify all environment variables are set
- Test MongoDB connection string locally
- Check `runtime.txt` has correct Python version

### Frontend Can't Connect to Backend

**Check:**
- CORS settings in backend
- API URL in frontend environment variables
- Both services are deployed and running

**Solutions:**
- Update `CORS_ORIGINS` to include frontend URL
- Verify `VITE_API_URL` is set correctly
- Check browser console for errors

### MongoDB Connection Failed

**Check:**
- Connection string is correct
- Password doesn't have special characters (or is URL-encoded)
- IP whitelist includes 0.0.0.0/0

**Solutions:**
- Regenerate connection string from MongoDB Atlas
- URL-encode password if it has special characters
- Verify network access settings

### Code Execution Not Working

**Note:** 
- C++ execution requires g++ compiler
- Render free tier may not have all compilers
- Python and JavaScript should work fine

**Solutions:**
- Test with Python and JavaScript first
- Consider using Docker for full compiler support
- Upgrade to paid tier for more resources

---

## Monitoring Your Deployment

### Render Dashboard
- View logs in real-time
- Monitor resource usage
- Check deployment history

### MongoDB Atlas
- Monitor database connections
- View query performance
- Check storage usage

### Application Monitoring
- Add logging to track errors
- Monitor API response times
- Track user analytics

---

## Updating Your Deployment

### Automatic Deployment
Render auto-deploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "feat: add new feature"
git push

# Render automatically deploys!
```

### Manual Deployment
- Go to Render Dashboard
- Click "Manual Deploy" → "Deploy latest commit"

---

## Upgrading to Paid Tier

If you need better performance:

1. **Starter Plan ($7/month per service)**
   - No cold starts
   - More resources
   - Better performance

2. **Pro Plan ($25/month per service)**
   - Even more resources
   - Priority support
   - Advanced features

---

## Your Deployed URLs

After deployment, you'll have:

- **Frontend:** `https://codelens-frontend.onrender.com`
- **Backend:** `https://codelens-backend.onrender.com`
- **API Docs:** `https://codelens-backend.onrender.com/docs`

---

## Next Steps

1. ✅ Deploy backend
2. ✅ Deploy frontend
3. ✅ Test functionality
4. 📱 Share your live app!
5. 🎉 Add to your portfolio

---

## Support

If you encounter issues:
1. Check Render logs
2. Review this guide
3. Check Render documentation: https://render.com/docs
4. MongoDB Atlas docs: https://docs.atlas.mongodb.com

---

**Good luck with your deployment!** 🚀
