# 🕸️ Web Data Harvesting & Scanning Tool

[![Angular](https://img.shields.io/badge/Frontend-Angular%2021-DD0031?style=flat-square&logo=angular)](https://angular.io/)
[![TypeScript](https://img.shields.io/badge/Language-TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Sass](https://img.shields.io/badge/Styles-SCSS-CC6699?style=flat-square&logo=sass&logoColor=white)](https://sass-lang.com/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Language-Python%203.14+-3776AB?style=flat-square&logo=python)](https://www.python.org/)

An enterprise-grade, **Multithreaded** web crawling solution designed for high-performance link extraction and site analysis. This project demonstrates a decoupled microservice architecture, utilizing a reactive **Angular** frontend and a high-concurrency **FastAPI** backend optimized for parallel data processing.

---

## 🏛️ System Architecture & Concurrency Model

The application utilizes a hybrid execution model to maximize throughput and minimize latency:

1.  **Asynchronous API Gateway (FastAPI)**: Leveraging Python’s `asyncio` to handle incoming HTTP requests without blocking, ensuring the server remains responsive under high load.
2.  **Multithreaded Crawling Engine**: The core logic implements **Parallel Execution**. By utilizing multiple threads, the system can fetch and parse multiple URLs simultaneously, significantly reducing the total time required for deep-site scans.
3.  **Reactive Presentation Layer (Angular)**: Uses RxJS observables to manage asynchronous data streams, providing a real-time, flicker-free update of crawled results.
4.  **Decoupled Data Flow**: Structured JSON exchange between the Python backend and TypeScript frontend ensures a clean separation of concerns.

---

## 🛠️ Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | Angular, TypeScript, SCSS | Reactive UI & State Management |
| **Backend** | FastAPI, Python 3.14+ | Async Request Handling & API Routing |
| **Concurrency** | `threading` / `concurrent.futures` | **Multithreaded** parallel crawling logic |
| **Server** | Uvicorn | ASGI High-Performance Server |

---

## 🚀 Key Features

* **High-Speed Multithreading**: Process multiple pages in parallel to harvest data at scale.
* **Real-time Link Discovery**: Instantly extract and categorize internal and external links.
* **Non-blocking UI**: Angular-based dashboard remains fully interactive during heavy backend scans.
* **Error Resiliency**: Robust handling of broken links, timeouts, and restricted domains.

---

## 🚀 User Flow

1. **Input**: User enters a target URL into the input field.
2. **Action**: User clicks the **"Start Crawl"** button.
3. **Backend Processing**: The FastAPI server receives the URL and executes the Python crawler.
4. **Data Return**: Discovered links are structured and sent back to the client.
5. **Display**: Angular updates the view to list all crawled links.
---

## 📸 Technical Walkthrough

### 1. Initialization
Users provide a seed URL to begin the parallel discovery process.
<img width="1876" alt="Start Screen" src="https://github.com/user-attachments/assets/2226ae66-61a1-4b0c-b4bc-a50a416a24db" />

### 2. Live Data Extraction
The multithreaded engine parses the target and returns a structured link hierarchy.
<img width="1877" alt="Results Overview" src="https://github.com/user-attachments/assets/5a755ca8-8af8-4496-a053-949bee1668d6" />
<img width="1858" alt="Detailed Results" src="https://github.com/user-attachments/assets/a58a49aa-634d-4c78-8bf9-b2c272c3838b" />

---

## 🏁 Installation & Setup

### 📋 Prerequisites

To develop or run this project locally, you need the following environment:

* **Runtime**: [Node.js](https://nodejs.org/) `v20.x` or higher (LTS recommended).
* **Package Manager**: `npm v10.9.4` (included with Node).
* **Language Engine**: [Python](https://www.python.org/) `3.14+` for the backend crawler.
* **Global CLI**: [Angular CLI](https://angular.io/cli) `v21.2.2` (Install via `npm install -g @angular/cli`).
* **Styling**: SCSS (Processed via Angular's built-in build pipeline).

### 1. Frontend Deployment
```bash
cd Frontend/crawler-ui
npm install
npm start
```

### 2. Backend Deployment
```bash
cd Web-Data-Harvesting-and-Scanning-Tool/Backend
python -m venv venv
# Activate environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn api:app --reload
```
---

## Comparison with Existing Tools
<img width="830" height="710" alt="image" src="https://github.com/user-attachments/assets/b19d1b60-89f3-45fb-a142-5f2d548237f2" />
<img width="829" height="553" alt="image" src="https://github.com/user-attachments/assets/646e15a0-302e-4ed3-bcee-e63a29405583" />
