# ⚡ Smart Energy Meter based on IoT

[![IoT](https://img.shields.io/badge/IoT-ESP32--S3-blue)]()
[![Python](https://img.shields.io/badge/Backend-Python%20%7C%20Django-green)]()
[![React](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript-blueviolet)]()
[![Database](https://img.shields.io/badge/Database-PostgreSQL-lightgrey)]()

## 📌 Overview
This project presents the development of a **smart energy meter** capable of identifying the nature of electrical loads connected to the grid (**resistive, inductive, capacitive**) and performing real-time measurements.  

The system was designed to be **robust, low-cost, and adaptable**, integrating **IoT, digital signal processing, and spectral analysis**.

---

## ⚙️ System Architecture

### 🔧 Hardware
- **ESP32-S3** (dual-core, Wi-Fi, Bluetooth, FreeRTOS).
- **ZMPT101b voltage sensor**.
- **SCT-013 current sensor** (non-invasive).
- Auxiliary circuit (resistive divider + coupling capacitor).
- Wooden enclosure with power extension for user connection.

📷 **Circuit Schematic**  
![Circuit](docs/img/figura1_circuito.png)

📷 **Hardware Assembly**  
| Circuit Board | Final Enclosure |
|---------------|-----------------|
| ![Circuit](docs/img/figura2a_circuito.png) | ![Enclosure](docs/img/figura2b_invólucro.png) |

---

### 💻 Embedded Software (ESP32-S3 + FreeRTOS)
- Simultaneous acquisition of voltage and current (**500 Hz**).
- Multithreading for concurrent measurements + synchronization via **NTP**.
- Data sent in **JSON** format to a central server.

### 🌐 Server
- API built with **Django (Python)**.
- **PostgreSQL** database.
- Data processing:
  - Calculation of **RMS values**.
  - **Energy consumption (Wh)**.
  - **FFT** for spectral analysis.
  - Phase shift calculation for load classification.

### 📊 Front-End
- Developed in **React + TypeScript**.
- Features:
  - Displays RMS values, instantaneous power, and consumption.
  - Waveform plots and FFT spectrum.
  - Automatic classification of loads (**resistive, inductive, capacitive**).

📷 **Front-End Dashboard**  
![Dashboard](docs/img/figura3_frontend.png)

---

## 🔬 Methodology
- Data collected → sent to server → stored in **PostgreSQL**.
- Processing includes:
  - **RMS calculation** for voltage and current.
  - **FFT** for frequency-domain analysis.
  - **Phase angle calculation** for load identification.
- Classification rules:
  - ⚡ **Capacitive** → current leads voltage.  
  - 🔩 **Inductive** → current lags voltage.  
  - 🔥 **Resistive** → no phase shift.  

---

## 📊 Experimental Results
Three real loads were tested:

📷 **Laptop charger (capacitive load)**  
![Capacitive](docs/img/figura4_capacitiva.png)

📷 **Vacuum cleaner (inductive load)**  
![Inductive](docs/img/figura5_indutiva.png)

📷 **Soldering iron (resistive load)**  
![Resistive](docs/img/figura6_resistiva.png)

| Device             | Detected Load | Phase Shift |
|--------------------|---------------|-------------|
| 💻 Laptop charger  | Capacitive    | +18.12°     |
| 🌀 Vacuum cleaner  | Inductive     | -30.45°     |
| 🔧 Soldering iron  | Resistive     | +1.92°      |

✅ The system correctly classified all loads and produced consistent spectral analysis results.  

---

## ✅ Conclusion
The smart energy meter proved to be a **reliable, efficient, and low-cost solution** for real-time energy monitoring.  
The integration of **hardware, firmware, server, and front-end** provided a practical and scalable tool for load analysis and classification.

---

## 🚀 Future Work
- Test with a **larger and more diverse set of loads**.  
- Implement **automatic alerts** for sudden consumption changes.  
- Use **harmonic signatures** to identify specific appliances.  
- Apply **neural networks and machine learning** for consumption prediction.  

---

## 📂 Repository
All project code can be found at:  
👉 [GitHub - RT-Electrical-Measurement](https://github.com/joaoBatista04/RT-Electrical-Measurement)

---

👨‍💻 **Authors**:  
- David Marques de Oliveira Leal  
- João Pedro Camargo Batista – [@joaoBatista04](https://github.com/joaoBatista04)  
