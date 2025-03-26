# Stock Volume Anomaly Detector

This repository contains a Python script that detects anomalies in stock trading volume and sends alerts via Telegram when unusual activity is detected. The script runs daily using GitHub Actions and retrieves stock data from Yahoo Finance.

 Features:

📊 Fetches historical stock data (1 year) from Yahoo Finance.

🔍 Identifies anomalies where high volume changes do not correspond to significant price changes.

📢 Sends Telegram alerts if anomalies are detected.

🔄 Automatically runs daily using GitHub Actions.
