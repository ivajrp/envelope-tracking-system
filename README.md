# Barcode-Based Envelope Tracking System

## 📌 Overview
This project presents a web-based system developed to manage and track envelopes within a public service environment. The system replaces a manual paper-based process with a digital solution, improving efficiency, accuracy, and accessibility.

## 🎯 Objectives
- Digitise envelope tracking operations
- Improve search and retrieval speed
- Reduce human error
- Enable multi-user access across the organisation

## ⚙️ Features
- Register incoming envelopes (barcode scanning supported)
- Record outgoing (dispatch) envelopes
- Search by barcode, client name, or service type
- Track envelope status (Received / Dispatched)
- Store document checklist per envelope
- Role-based access:
  - Admin: full access
  - User: view/search only

## 🛠️ Technologies Used
- Python (Flask)
- SQLite Database
- HTML5 / CSS3
- JavaScript (barcode input handling)

## 🧱 System Architecture
The system follows a simple three-layer architecture:

User Interface (Browser)  
↓  
Flask Web Application  
↓  
SQLite Database  

## ▶️ How to Run the System

1. Install Python (3.x)
2. Install Flask:
   ```bash
   pip install flask
