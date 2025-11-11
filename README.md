# 🚀 AI Resume Optimizer

**Transform your resume into a job-winning document in 3 minutes.**

Upload your resume, paste any job posting URL, and get a perfectly tailored resume optimized for both ATS systems and human recruiters.

![Main Interface](public/main-interface.png)

---

## ⚡ Quick Start (2 Minutes Setup)

### 1. **Download & Install**
```bash
# Clone the project
git clone https://github.com/yourusername/resume-optimization-crew.git
cd resume-optimization-crew

# Install Python dependencies
pip install -r requirements.txt

# Start the app (cleans cache automatically)
python3 start.py
```

**Why use `start.py`?** It automatically cleans ChromaDB cache to prevent conflicts when switching between different resumes. Much easier than manual cleanup!

### 2. **Get Your API Keys** (Free/Cheap)
- **OpenAI**: [Get key here](https://platform.openai.com/api-keys) (~$1 per resume)
- **Serper**: [Get key here](https://serper.dev/api-key) (Free for 2,500 searches)

### 3. **Use the App**
1. Open `http://localhost:8501` (opens automatically)
2. Enter your API keys in the sidebar
3. Upload your resume PDF
4. Paste the job posting URL
5. Click "Optimize Resume" ✨

**That's it!** You'll get a complete analysis and optimized resume in 2-3 minutes.

---

## 🎯 What You Get

### 📊 **Complete Analysis**
- **Match score** between your resume and job requirements
- **Skills gap analysis** - what's missing vs what you have
- **ATS optimization** - keywords and formatting suggestions

### 📄 **New Optimized Resume**
- **Completely rewritten** to match the job
- **ATS-friendly** formatting and keywords
- **Downloadable** in Markdown format (convert to PDF easily)

### 🏢 **Company Intelligence**
- **Recent company news** for interview talking points
- **Company culture insights** to tailor your approach
- **Strategic interview questions** to ask

### 💡 **Before vs After Example**
```
BEFORE: "Software Engineer with programming experience"

AFTER:  "Senior Full-Stack Developer with 5+ years building
         scalable web applications using React, Node.js, and
         AWS, specializing in microservices architecture"
```

---

## 💰 Costs (Very Affordable)

| Service | Cost | What It's For |
|---------|------|---------------|
| **OpenAI** | ~$1-2 per resume | AI analysis & writing |
| **Serper** | Free (2,500/month) | Company research |
| **Total** | **~$1-2 per job application** | Complete optimization |

*Most users spend less than $2 per optimized resume. No monthly subscriptions.*

---

## 🔄 Using for Multiple Jobs

### **Same Resume, Different Jobs**
- Just change the job URL and company name
- Click "Optimize Resume" again
- No restart needed!

### **Different Resume Files**
1. Stop the app (`Ctrl+C`)
2. Run `python3 start.py` again
3. Upload new resume

💡 **Why restart?** The `start.py` script automatically cleans ChromaDB cache, preventing memory conflicts between different resumes. Without this cleanup, the app might mix data from your previous resume with the new one.

---

## 🛠️ Troubleshooting

### **Common Issues & Quick Fixes**

| Problem | Quick Fix |
|---------|-----------|
| **"Invalid API key"** | Copy the full key exactly from the website |
| **"ChromaDB error"** | Restart with `python3 start.py` |
| **"File upload failed"** | Ensure PDF is under 200MB and text-readable |
| **"No results"** | Check that job URL is public and accessible |
| **App won't start** | Run `pip install streamlit` |

### **Need Help?**
1. Check your API keys are correctly copied
2. Ensure your resume PDF contains readable text (not just images)
3. Verify the job URL loads in your browser
4. Try restarting the app with `python3 start.py`

---

## 🔒 Privacy & Security

### **Your Data Stays Private**
- ✅ **Runs locally** - everything happens on your computer
- ✅ **No cloud storage** - files are deleted after analysis
- ✅ **API keys not saved** - enter fresh each session
- ✅ **No tracking** - your usage is completely private

### **API Key Safety**
- Never share your API keys with anyone
- Keys are only sent to OpenAI/Serper for processing
- Regenerate keys if compromised
- Monitor usage on OpenAI dashboard

---

## 📋 Requirements

- **Python 3.10+** (check with `python3 --version`)
- **2GB free space** for dependencies
- **Internet connection** for AI processing
- **PDF resume** (text-readable, not scanned image)

---

## ❓ FAQ

**Q: How much does this cost?**
A: ~$1-2 per resume. OpenAI charges for AI usage, Serper is free.

**Q: How long does it take?**
A: 2-3 minutes for complete analysis and optimization.

**Q: What if I don't have API keys?**
A: Get them free/cheap from the links above. Takes 2 minutes.

**Q: Can I use this offline?**
A: No, it needs internet to connect to AI services.

**Q: What file formats work?**
A: PDF resumes only. Output is Markdown (easily convert to PDF).

**Q: Is my resume data safe?**
A: Yes, everything runs locally. No data is stored anywhere.

---

## 🏗️ Technical Details

**Built with:**
- **CrewAI** - Multi-agent AI framework
- **Streamlit** - Web interface
- **OpenAI GPT-4** - Resume analysis and optimization
- **ChromaDB** - Vector database for resume processing

**Architecture:** Multiple specialized AI agents work together to analyze job requirements, evaluate your resume, research the company, and generate optimized content.

---

## 🙏 Credits

**Original Creator:** [Tony Kipkemboi](https://github.com/tonykipkemboi/resume-optimization-crew)

**Enhancements Added:**
- 🖥️ **User-friendly Streamlit interface**
- 🧹 **Automatic cache cleanup** for seamless operation
- 📊 **Enhanced results display** with organized tabs
- 🔒 **Local-only operation** for maximum privacy
- 📚 **Simplified setup** with one-command start

---

**Ready to get more interviews?** ⬆️ [Jump to Quick Start](#-quick-start-2-minutes-setup)