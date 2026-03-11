# 🧬 PatentSeq - Antibody Sequence Extractor

A professional web application for extracting and analyzing antibody sequences from patent documents with AI-powered classification.

## ✨ Features

- 🎨 **Beautiful Professional UI** - Clean, modern interface with IBM Plex Mono + Inter fonts
- 📁 **File Upload Support** - CSV, TXT files with mixed patent formats
- 🧬 **AI-Powered Classification** - Automatic detection of VH, VL, CDR sequences
- 📊 **Multi-Sheet Excel Export** - Comprehensive analysis with separate sheets
- 📱 **Mobile Responsive** - Works on any device
- ⚡ **Real-time Processing** - Live progress tracking

## 🚀 Live Demo

Visit the deployed app: [PatentSeq on Streamlit](https://patentseq.streamlit.app)

## 💻 Local Development
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📋 Supported Patent Formats

- **US Patents**: `US10123456`
- **US Applications**: `US20210123456A1`
- **PCT Applications**: `WO2021123456`
- **European Patents**: `EP3123456B1`
- **Simple numbers**: `10123456` (auto-converted to US patents)

## 🧬 Sequence Types Extracted

- Heavy Chain Variable Regions (VH)
- Light Chain Variable Regions (VL)
- CDR Sequences (CDR1, CDR2, CDR3)
- Framework Regions
- Full-Length Sequences

## 📊 Output Formats

- **Excel (.xlsx)**: Multi-sheet format with separate tabs for:
  - All sequences
  - Heavy chains only
  - Light chains only
  - CDR sequences only
- **CSV (.csv)**: Single table format for analysis

## 🏗️ Architecture

- **Frontend**: Streamlit with custom CSS styling
- **Backend**: Python with pandas for data processing
- **Export**: openpyxl for Excel generation
- **Classification**: AI-powered sequence type detection

---

*Built with ❤️ using Streamlit | Created by Nishanth Kandepedu*
