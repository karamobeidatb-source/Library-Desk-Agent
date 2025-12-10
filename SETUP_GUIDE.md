# Quick Setup Guide

## Step-by-Step Instructions

### 1️⃣ Install Python
- Download Python 3.9+ from https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

### 2️⃣ Create Virtual Environment
Open terminal/command prompt in the project folder:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Get OpenAI API Key
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

### 5️⃣ Configure Environment
**Windows:**
```bash
copy env.example .env
notepad .env
```

**macOS/Linux:**
```bash
cp env.example .env
nano .env
```

Paste your API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### 6️⃣ Initialize Database
```bash
python db/init_db.py
```

### 7️⃣ Run the Application

**Option A: Manual (Recommended first time)**

Terminal 1 - Backend:
```bash
python server/main.py
```

Terminal 2 - Frontend:
```bash
streamlit run app/main.py
```

**Option B: Using Scripts**

**Windows:**
- Double-click `run_backend.bat`
- Double-click `run_frontend.bat` (in new window)

**macOS/Linux:**
```bash
chmod +x run_backend.sh run_frontend.sh
./run_backend.sh        # Terminal 1
./run_frontend.sh       # Terminal 2
```

### 8️⃣ Access the App
The Streamlit UI will automatically open in your browser at:
```
http://localhost:8501
```

## Verification Checklist

✅ Python 3.9+ installed  
✅ Virtual environment created and activated  
✅ Dependencies installed (`pip install -r requirements.txt`)  
✅ `.env` file created with OpenAI API key  
✅ Database initialized (`python db/init_db.py`)  
✅ Backend server running (Terminal 1)  
✅ Frontend running (Terminal 2)  
✅ Browser opened to http://localhost:8501  

## Common Issues

**"python not recognized"**
- Reinstall Python and check "Add to PATH"
- Try `python3` instead of `python`

**"pip not recognized"**
- Use `python -m pip` instead of `pip`

**"OPENAI_API_KEY not found"**
- Make sure `.env` file exists (not `env.example`)
- Check the key starts with `sk-`

**"Backend not running" in Streamlit**
- Make sure backend is running in another terminal
- Check http://127.0.0.1:8000/health in browser

**Need help?**
- Check the full README.md
- Review the Troubleshooting section

