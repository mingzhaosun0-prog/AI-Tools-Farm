# 🧩 App Framework Hub

A modular **Streamlit** workspace with a collection of mini-apps for travel planning, data visualization, image processing, and more.

## 🚀 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-tools-farm.streamlit.app)

## 📱 Apps

| App | Description |
|---|---|
| 🇨🇳 **China Travel Guide** | Discover Beijing's top attractions with rich guides, cost calculators, section comparisons & interactive planning tools |
| 📱 **QR Code Generator** | Create custom QR codes with colour picker & download |
| 📐 **Unit Converter** | Convert between 50+ units: length, weight, temperature, volume, speed & data |
| 📊 **Data Visualizer** | Upload CSV/Excel & create interactive plots (line, bar, scatter) |
| 🖼️ **Image Processor** | Adjust brightness, grayscale, flip, rotate & download |
| ✍️ **Text Analyzer** | Word count, character stats, and most frequent words |

## 🛠️ Local Development

```bash
# Clone the repo
git clone https://github.com/f4register/AI-Tools-Farm.git
cd AI-Tools-Farm

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 🚢 Deployment

This app is designed to deploy instantly on [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push the code to a **public GitHub repo**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub and select the repo
4. Set the main file to `app.py`
5. Click **Deploy** — it's live in minutes!
