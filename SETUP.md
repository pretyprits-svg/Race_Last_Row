# Setup Guide for Horse Race Analysis Tool

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **pip** package manager
- **Git** (for cloning the repository)
- Internet connection (for first-time OCR model download)

## 🚀 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/race-analysis.git
cd race-analysis
```

### 2. Create Virtual Environment (Recommended)

#### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: First time installation may take 5-10 minutes as it downloads:
- EasyOCR models (~100MB)
- PyTorch (if not already installed)
- Other dependencies

### 4. Verify Installation

```bash
python -c "from race_parser import parse_pdf; print('✅ Installation successful!')"
```

### 5. Run the Application

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

### 6. Open in Browser

Navigate to: `http://localhost:5000`

## 🎯 First Use

### Upload a PDF

1. Click "Choose File" or drag-and-drop a race card PDF
2. Click "Upload and Analyze"
3. Wait for processing (image PDFs take longer ~1-2 min)
4. View results in interactive tables

### Download Results

Click "Download CSV" to export data to Excel/CSV format

## ⚙️ Configuration

### Change Port

Edit `app.py`:
```python
if __name__ == "__main__":
    app.run(debug=True, port=8080)  # Change 5000 to 8080
```

### Disable Debug Mode

For production:
```python
app.run(debug=False, host='0.0.0.0')
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :5000
kill -9 <PID>
```

Or change the port in `app.py`.

### EasyOCR Installation Failed

Try installing PyTorch first:
```bash
pip install torch torchvision
pip install easyocr
```

### PDF Not Parsing

- Ensure PDF is a race card with expected format
- Check console for error messages
- Try with the sample `ANK.pdf` first

### Slow Processing

- Image PDFs require OCR (slower)
- First run downloads OCR models
- Subsequent runs are faster
- Consider using text-based PDFs for speed

## 📦 Dependencies Explained

| Package | Purpose |
|---------|---------|
| Flask | Web server |
| pdfplumber | Extract text from PDFs |
| PyMuPDF | Render PDF pages as images |
| EasyOCR | Extract text from images |
| Pillow | Image processing |
| numpy | Numerical operations |

## 🔄 Updating

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## 🌐 Deployment

### Heroku

See `Procfile` and `runtime.txt` (already configured)

```bash
heroku create your-app-name
git push heroku main
```

### Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 📞 Support

If you encounter issues:

1. Check this guide first
2. Review error messages in terminal
3. Open a GitHub issue with error details
4. Include Python version: `python --version`

## ✅ System Requirements

- **RAM**: 2GB minimum (4GB recommended for OCR)
- **Storage**: 500MB for dependencies
- **CPU**: Any modern processor
- **OS**: Windows, Mac, or Linux

## 🎓 Next Steps

- Try with sample PDFs
- Explore the calculation formulas
- Customize the UI (templates/index.html)
- Add more features!

---

Happy analyzing! 🏇
