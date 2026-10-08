# 🏇 Horse Race Analysis Tool - Last Row

A powerful web application for analyzing horse racing data from PDF race cards. Supports both text-based and image-based PDFs with automatic OCR extraction.

## ✨ Features

- **📄 PDF Parsing**: Extracts race data from both text and image-based PDFs
- **🔍 OCR Support**: Automatic text extraction from scanned/image PDFs using EasyOCR
- **📊 Speed Rating Calculation**: Uses each horse's latest historical race record
- **⚖️ Weight Allowance Handling**: Automatically adjusts for jockey weight allowances
- **🎯 Smart Time Calculation**: Accurate horse timing with rollover detection
- **📈 Multi-Race Analysis**: Process multiple races from a single PDF
- **💾 CSV Export**: Download results for further analysis
- **🎨 Modern UI**: Clean, responsive interface with dark theme

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/race-analysis.git
cd race-analysis
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Open your browser**
```
http://localhost:5051
```

## 📦 Dependencies

- **Flask**: Web framework
- **pdfplumber**: PDF text extraction
- **PyMuPDF (fitz)**: PDF rendering for OCR
- **EasyOCR**: Optical character recognition
- **Pillow**: Image processing
- **pandas**: Data manipulation (optional)

## 🎯 How It Works

### 1. PDF Upload
Upload your race card PDF through the web interface.

### 2. Automatic Text Extraction
- **Text-based PDFs**: Direct extraction using pdfplumber
- **Image-based PDFs**: OCR extraction using EasyOCR

### 3. Data Parsing
Extracts:
- Horse names and numbers
- Current race distance
- Horse weights with jockey allowances
- Historical race records (distance, weight, time, PNR)

### 4. Calculations

#### Weight Adjustment
```
If jockey has allowance like (-2.5):
  Final Weight = Horse Weight - Allowance
  Example: 59 kg - 2.5 kg = 56.5 kg
```

#### Time Calculation
```
Winner time: 1-41.83 (1 minute 41.83 seconds)
Horse time: 11.39f (shown as seconds only)

Since 11.39 < 41.83, horse must be in next minute:
  Horse time = 2:11.39 = 131.39 seconds
```

#### Adjusted Time (latest historical race record)
```
Adjusted Time = Latest Race Time 
  - (Old Distance - Current Distance) × 0.0625
  - (Old Weight - New Weight) / 10
  - (PNR Race - Standard PNR) × 2
```

#### Speed Rating
```
Speed Rating = (Current Distance / Adjusted Time) × 100 - 1000
```

### 5. Ranking
- **Speed Rank**: Based on speed rating (higher is better)
- **Odds Rank**: Based on betting odds (lower is better)
- **Final Rating**: Speed Rating × (1 / (Odds + 1))
- **Value Score**: Speed Rank / Odds Rank

## 📋 Supported PDF Formats

### Mumbai Race Cards (ANK.pdf format)
✅ Fully supported with direct text extraction

### Bangalore Race Cards
✅ Supported with OCR extraction

### Other Formats
The parser uses regex patterns to identify:
- Race numbers and names
- Horse entries (format: `1. HORSE NAME 59.5`)
- Distance markers (`1500 Mts.`)
- Historical records with dates, distances, weights, and times

## 🛠️ Configuration

### Historical Record Selection
Calculations use each horse's final historical record as it appears in the parsed race card.

### Standard PNR
```python
std_pnr = 3.5  # Default in compute_race()
```

## 📁 Project Structure

```
race-analysis/
├── app.py                 # Flask web application (default port 5051)
├── race_parser.py         # PDF parsing and calculations using each horse's latest record
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── uploads/              # Uploaded PDFs (auto-created)
└── README.md            # This file
```

## 🔧 Development

### Adding Debug Output
```python
# In race_parser.py
print(f"[DEBUG] Processing: {horse_name}")
```

### Testing with CLI
```bash
python -c "from race_parser import parse_pdf; races = parse_pdf('test.pdf'); print(len(races))"
```

## 🐛 Troubleshooting

### OCR Not Working
```bash
# Reinstall EasyOCR
pip uninstall easyocr
pip install easyocr
```

### PDF Not Parsing
- Check if PDF has extractable text (try selecting text in PDF viewer)
- For image PDFs, ensure EasyOCR is installed
- Check console output for parsing errors

### Negative Weights Showing
- Ensure jockey allowances are in format `(-2.5)` with negative sign
- Check that horse weight appears on first line of horse entry

## 📄 License

MIT License - feel free to use and modify

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues or questions, please open a GitHub issue.

## 🙏 Acknowledgments

- EasyOCR team for excellent OCR library
- Flask community for the web framework
- pdfplumber for PDF parsing capabilities
