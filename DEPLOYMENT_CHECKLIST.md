# 🚀 Render.com Deployment Checklist

## Quick Start Guide

Follow these steps in order:

---

## ☁️ Step 1: Setup MongoDB Atlas (5 min)

1. [ ] Go to https://www.mongodb.com/cloud/atlas/register
2. [ ] Create free account
3. [ ] Create free cluster (M0)
4. [ ] Create database user:
   - Username: `codelens`
   - Password: (save it!)
5. [ ] Allow network access: 0.0.0.0/0
6. [ ] Get connection string
7. [ ] Save connection string (you'll need it!)

**Connection String Format:**
```
mongodb+srv://codelens:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/codelens_ai
```

---

## 🔧 Step 2: Deploy Backend (10 min)

1. [ ] Go to https://render.com
2. [ ] Sign up with GitHub
3. [ ] Click "New +" → "Web Service"
4. [ ] Connect repository: `jshree14/CodeLens-`
5. [ ] Configure:
   ```
   Name: codelens-backend
   Root Directory: backend
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
6. [ ] Add Environment Variables:
   ```
   GEMINI_API_KEY = (your Gemini API key)
   MONGODB_URL = (your MongoDB connection string)
   DATABASE_NAME = codelens_ai
   DEBUG = False
   CORS_ORIGINS = *
   ```
7. [ ] Click "Create Web Service"
8. [ ] Wait for deployment (5-10 min)
9. [ ] Save backend URL: `https://codelens-backend.onrender.com`
10. [ ] Test: Visit `https://codelens-backend.onrender.com/api/health`

---

## 🎨 Step 3: Deploy Frontend (10 min)

1. [ ] Click "New +" → "Web Service"
2. [ ] Select same repository
3. [ ] Configure:
   ```
   Name: codelens-frontend
   Root Directory: (leave empty)
   Build Command: npm install && npm run build
   Start Command: npm run preview -- --host 0.0.0.0 --port $PORT
   ```
4. [ ] Add Environment Variable:
   ```
   VITE_API_URL = https://codelens-backend.onrender.com
   ```
5. [ ] Click "Create Web Service"
6. [ ] Wait for deployment (5-10 min)
7. [ ] Save frontend URL: `https://codelens-frontend.onrender.com`

---

## 🔄 Step 4: Update CORS (2 min)

1. [ ] Go to backend service on Render
2. [ ] Click "Environment"
3. [ ] Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS = https://codelens-frontend.onrender.com
   ```
4. [ ] Save (auto-redeploys)

---

## ✅ Step 5: Test Your App (5 min)

1. [ ] Visit your frontend URL
2. [ ] Paste test code:
   ```python
   print("Hello World")
   ```
3. [ ] Click "Analyze Code"
4. [ ] Wait 30-60 seconds (first request)
5. [ ] See results! 🎉

---

## 📝 Your Deployment Info

Fill this in as you deploy:

```
Backend URL: https://codelens-backend.onrender.com
Frontend URL: https://codelens-frontend.onrender.com
MongoDB URL: mongodb+srv://codelens:PASSWORD@cluster0.xxxxx.mongodb.net/
Gemini API Key: AIza...
```

---

## ⚠️ Important Notes

### Free Tier Limits
- Services sleep after 15 min of inactivity
- First request takes 30-60 seconds
- Subsequent requests are fast

### Keep Services Awake (Optional)
Use UptimeRobot to ping every 14 minutes:
- https://uptimerobot.com
- Add monitor for your frontend URL

---

## 🐛 Troubleshooting

### Backend won't start?
- Check logs in Render dashboard
- Verify all environment variables
- Test MongoDB connection string

### Frontend can't connect?
- Check CORS settings
- Verify VITE_API_URL is correct
- Check browser console for errors

### MongoDB connection failed?
- Verify connection string
- Check IP whitelist (0.0.0.0/0)
- Ensure password is correct

---

## 🎉 Success!

Once deployed, you'll have:
- ✅ Live backend API
- ✅ Live frontend app
- ✅ MongoDB database
- ✅ AI-powered code analysis
- ✅ Portfolio-ready project!

**Share your app:** `https://codelens-frontend.onrender.com`

---

## 📚 Full Documentation

See `DEPLOYMENT.md` for detailed instructions and troubleshooting.

---

**Estimated Total Time: 30 minutes**

Good lu