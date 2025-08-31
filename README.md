# RT-Electrical-Measurement

A project for real-time electrical measurement and monitoring, featuring a web-based frontend, a backend server, and ESP-based firmware.

Made by: Arthur Trarbach and João Batista

## Project Structure

- **frontend/**  
    React-based web application for real-time data visualization.

- **backend/**  
    Server-side code handling sensor data acquisition, processing, and communication with the frontend.

- **appr1.ino**  
    ESP32 code for interfacing with electrical sensors and transmitting measurements to the backend.

## Features

- Real-time electrical parameter monitoring (voltage, current, etc.)
- Web dashboard for live data and historical trends
- Wireless communication between hardware and frontend

## Getting Started

1. **Clone the repository**
     ```bash
     git clone https://github.com/joaoBatista04/RT-Electrical-Measurement.git
     ```

2. **Frontend**
     - Navigate to `frontend/`
     - Install dependencies: `npm install`
     - Start development version with `npm run dev`

3. **Backend**
     - Navigate to `backend/`
     - Install dependencies and configure settings as needed
     - Make sure you have installed and configured your database (PostgreSQL in this case)
     - Run `python manage.py makemigrations` followed by `python manage.py migrate` to make sure your database is properly setup
     - Start the backend server: `python manage.py runserver 0.0.0.0:8000`

4. **ESP Firmware**
     - Open `appr1.ino` in Arduino IDE
     - Properly configure Wi-Fi connection and correct server IP
     - Select the correct ESP board and port
     - Upload to your ESP32 device

## Requirements

- Node.js & npm (for frontend)
- Django & Python (for frontend)
- ESP32 board