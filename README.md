# Adif Oposiciones AI Engine 🚆📚

> **Autonomous Multi-Agent Legal Document Processing Pipeline & Active-Recall Study Platform for Spanish Railway Administration (Adif) Civil Service Examinations.**

[![Architecture: Multi-Agent](https://img.shields.io/badge/Architecture-Multi--Agent%20Pipeline-blue.svg)](AGENTS.md)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Web App: Vanilla ES6+](https://img.shields.io/badge/Frontend-Vanilla%20ES6%2B%20%7C%20CSS3-success.svg)](web_app/)
[![PWA: Offline First](https://img.shields.io/badge/PWA-100%25%20Offline%20First-green.svg)](web_app/sw.js)
[![Questions: 210 Verified](https://img.shields.io/badge/Verified%20Questions-210%20Official-orange.svg)](web_app/adif_questions_db.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 1. Executive Summary & Problem Space

Candidates preparing for the **Adif (Administrador de Infraestructuras Ferroviarias)** and Spanish Public Sector civil service examinations must master thousands of pages of dense, rapidly shifting regulatory and technical documentation. Traditional study methods suffer from:
1. **Information Loss & Extraction Bottlenecks**: Complex multi-column legal PDFs, nested regulatory tables, and amendments lose layout fidelity when copied or fed into generic LLM wrappers.
2. **Hallucination & Lack of Auditability**: Synthetic quiz generators frequently hallucinate legal articles or fail to cite specific page boundaries.
3. **Static & Monotonous Drills**: Fixed test sets lead to position-memorization rather than genuine conceptual mastery.

### The Solution
This project implements a **two-stage decoupled multi-agent architecture**:
* **Agent 1 (Lossless Ingestion Agent)**: Converts raw legal PDFs into GitHub Flavored Markdown (GFM) preserving typographic hierarchies, tables, and page boundaries (`<!-- PAGE X OF Y -->`).
* **Agent 2 (Domain Specialist Examination Agent)**: Synthesizes a structured bank of **210 authentic opposition questions** (10 questions across all 21 legal topics), complete with legal reasoning and article citations, packaged into an ultra-fast, zero-dependency **Progressive Web App (PWA)** that runs 100% offline on any desktop or mobile device.

---

## 2. System Architecture

```mermaid
flowchart TD
    subgraph Ingestion["Stage 1: Lossless Document Ingestion (Agent 1)"]
        PDFs["Source PDFs (21 Laws, Decrees & Adif Reports)"] --> Agent1["pdf_to_md_agent.py\n(PyMuPDF / PyMuPDF4LLM / Tesseract OCR)"]
        Agent1 --> RatioCheck{"Lossless Ratio\nValidation (>= 0.95)"}
        RatioCheck -- Success --> MDOutput["markdown_output/*.md\n- YAML Frontmatter\n- GFM Tables\n- Page Boundary Delimiters\n- INDEX.md & manifest.json"]
        RatioCheck -- Scanned Fallback --> OCR["Tesseract Optical Recognition"] --> MDOutput
    end

    subgraph Downstream["Stage 2: Specialist Synthesis & Active Recall (Agent 2)"]
        MDOutput --> Agent2["adif_exam_agent.py\n(Domain Specialist Agent)"]
        Agent2 --> BankJSON["web_app/adif_questions_db.json\n(210 Verified Questions)"]
        Agent2 --> OfflineBundle["web_app/questions_data.js\n(Inlined Offline Bundle)"]
        Agent2 --> PaperMocks["simulacros/*.md\n(Printable Mock Exams)"]
    end

    subgraph ClientApp["Stage 3: Offline-First Client Engine (web_app/)"]
        OfflineBundle --> PWAEngine["Client Study Engine (app.js)\n- Fisher-Yates Randomizer\n- Official Scoring (-0.33 Penalty)\n- 3D Flippable Flashcards\n- Smart Mistakes Notebook (localStorage)\n- 21-Topic Explorer"]
        BankJSON --> PWAEngine
        PWAEngine --> Desktop["Desktop Browser\n(http://localhost:8080)"]
        PWAEngine --> MobilePWA["Mobile Standalone PWA\n(iOS Safari / Android Chrome)"]
    end
```

---

## 3. Product Features & Technical Capabilities

### 🎯 Dynamic Randomized Exam Engine
* **Non-Deterministic Sessions**: Uses the Fisher-Yates shuffle algorithm on every page refresh or click on `🎲 New Exam`. No two study sessions present the same sequence.
* **Configurable Battery Sizes**: Select between 25 questions (Official Adif Simulation), 10 questions (5-min Sprint), 50 questions (Intensive), 100 questions (Macro Drill), or the full 210-question master battery.
* **Official Scoring Rubric**: Real-time timer tracking with the official Spanish civil service scoring formula:
  $$\text{Score} = \text{Correct} - (\text{Incorrect} \times 0.33)$$
* **Uncompromising Legal Auditability**: Every question includes immediate feedback displaying the exact statutory article, official document title, and original PDF page number.

### 🗂 3D Active-Recall Flashcards
* **Complete 210-Card Deck**: Fluid spatial 3D card flipping via CSS transforms (`preserve-3d`, `rotateY(180deg)`).
* **Instant Shuffle (`🔀 Shuffle`)**: Re-indexes the card array dynamically to prevent order bias.
* **Ergonomic Keyboard Shortcuts**:
  * `Space`: Flip card (front/back).
  * `Arrow Right` / `Enter`: Next card / Next question.
  * `Arrow Left`: Previous card / Previous question.
  * Keys `1`, `2`, `3`, `4` or `A`, `B`, `C`, `D`: Select answer option.

### 🧠 Smart Mistakes Notebook (Persistent Spaced Repetition)
* Automatically intercepts incorrect answers and stores their unique IDs in `localStorage`.
* Dedicated **"Preguntas Falladas"** tab allows focused re-testing of weak spots until cleared.
* Tracks daily streaks, cumulative question volume, and real-time accuracy percentages.

### 📚 21-Topic Syllabus Explorer
* Complete catalog of the 21 official Adif competition topics, grouped into 5 macro-blocks:
  1. **Block 1**: State Organization & Public Administration (LPAC 39/2015, LRJSP 40/2015, Budgetary Law 47/2003, Fiscal Stability LO 2/2012, Electronic Public Sector RD 203/2021).
  2. **Block 2**: Civil Service, Employment & Ethics (TREBEP RD Leg. 5/2015, Incompatibilities Law 53/1984, Workers' Statute, Social Security).
  3. **Block 3**: Equality, Diversity & Workplace Safety (LO 3/2007 Gender Equality, Law 4/2023 Trans Rights, Occupational Risk Prevention Law 31/1995).
  4. **Block 4**: Railway Sector & Adif (Railway Sector Law 38/2015, Adif Statute RD 2395/2004, Adif Network Statement 2027, Sustainability Report 2025).
  5. **Block 5**: Railway Safety, Public Contracts & Digital Rights (Common Safety Methods UE 402/2013, Safety Management Systems Delegated Reg. UE 2018/762, Public Sector Contracts Law 9/2017, National Security Scheme ENS RD 311/2022, Data Protection LOPDGDD 3/2018).
* Deep-dive trigger buttons: launch a 10-question test or dedicated flashcard deck for any individual topic with a single click.

### 📱 100% Offline-First PWA (Zero Network Dependency)
* **Standalone Mobile Mode**: Includes `manifest.webmanifest`, Apple touch icons, and a custom Service Worker (`sw.js` v4) that caches all static assets locally.
* **Zero External CDN Dependencies**: Uses pure Vanilla ES6+ and native system fonts (`-apple-system`, San Francisco / Inter) ensuring zero degradation when offline.
* **Instant LAN Connect**: Built-in HTTP server generates a dynamic Wi-Fi QR code in both the terminal and in-app modal for instant mobile onboarding.

---

## 4. Engineering Decisions & Architecture Trade-offs

| Decision | Rationale | Alternatives Considered |
|---|---|---|
| **Vanilla ES6+ & CSS Custom Properties** | Zero build step, instant load time (<150ms), sub-megabyte footprint (~550 KB total), runs directly on any browser or static host. | React/Next.js (rejected due to excessive bundle size, dependency overhead, and unnecessary hydration lag for a local study tool). |
| **Dual Storage (JSON + Global JS Bundle)** | `questions_data.js` exposes `window.ADIF_EXAM_DATA`, completely bypassing browser `file://` CORS restrictions when opened without an HTTP server. | Fetch-only JSON (rejected because strict CORS policies block `fetch()` on `file:///` URLs on desktop). |
| **Deterministic Page Delimiters** | Injecting `<!-- PAGE X OF Y -->` into Markdown allows Agent 2 to extract the exact source PDF page without keeping bulky PDFs in memory. | Vector database chunks (rejected for core citations due to chunk-boundary drift and lack of deterministic page mapping). |
| **Git Binary Exclusion (`*.pdf`)** | Keeps repository clone weight under 2 MB while preserving full legal fidelity in Markdown (~5 MB text vs ~35 MB binary PDFs). | Git LFS (rejected to eliminate external storage quota dependencies). |

---

## 5. Repository Structure

```text
├── AGENTS.md                  # Two-agent pipeline specification & contract
├── README.md                  # System technical documentation (this file)
├── requirements.txt           # Python dependencies for Agent 1 and Agent 2
├── .gitignore                 # Excludes venv, pycache, and raw PDF binaries
├── run_agent.sh               # Execution script for Agent 1 (PDF to Markdown)
├── run_study_tool.sh          # Execution script for Agent 2 (Interactive Server)
│
├── pdf_to_md_agent.py         # Agent 1: Lossless PDF-to-Markdown extractor
├── adif_exam_agent.py         # Agent 2: Specialist study agent & mock exam generator
│
├── markdown_output/           # Lossless Markdown repository (21 processed laws)
│   ├── INDEX.md               # Master index of all processed legislation
│   ├── manifest.json          # Machine-readable metadata (word count, page count)
│   └── 01 ... 15 *.md         # Full legal texts with GFM tables & page markers
│
├── simulacros/                # Printable mock examinations
│   └── simulacro_oficial_adif_1.md # 25-question mock exam with answer rationale
│
└── web_app/                   # Self-contained PWA Active-Recall Client
    ├── index.html             # Single-page application structure & modals
    ├── styles.css             # Ultra-premium responsive design & 3D animations
    ├── app.js                 # Study engine (Fisher-Yates, timer, state, scoring)
    ├── questions_data.js      # Inlined 210-question offline dataset
    ├── adif_questions_db.json # Machine-readable 210-question database
    ├── sw.js                  # Service Worker v4 (Offline asset caching)
    ├── manifest.webmanifest   # PWA manifest metadata
    ├── icon.png               # High-resolution vector railway icon
    └── mobile_qr.png          # Dynamic QR code for Wi-Fi mobile connection
```

---

## 6. Quickstart & Installation

### Prerequisites
* **Python 3.10+**
* Modern web browser (Chrome, Safari, Firefox, Edge)

### Setup
```bash
# Clone the repository
git clone https://github.com/emilsyszanella/adif-oposiciones-ai-engine.git
cd adif-oposiciones-ai-engine

# Create and activate a clean virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install ingestion pipeline dependencies
pip install -r requirements.txt
```

---

## 7. Execution Guide

### 1. Launching the Interactive Study Platform (Agent 2)
```bash
# Using the convenience runner:
./run_study_tool.sh

# Or directly via Python:
./.venv/bin/python adif_exam_agent.py --serve 8080
```
* **Desktop**: Open [http://localhost:8080](http://localhost:8080)
* **Mobile (Same Wi-Fi)**: Scan the QR code displayed in the terminal with your phone camera.
* **Offline Mobile Installation (iOS Safari)**:
  1. Open `http://<your-local-ip>:8080` in Safari.
  2. Tap the **Share** button (`[ ↑ ]`).
  3. Select **"Add to Home Screen"**.
  4. Launch from your home screen icon. It functions 100% offline (even in Airplane Mode).

### 2. Generating Printable Mock Exams in Markdown
```bash
./.venv/bin/python adif_exam_agent.py
```
This generates a fresh 25-question mock exam with official correction template and legal citations in `simulacros/simulacro_oficial_adif_1.md`.

### 3. Running the PDF Ingestion Pipeline (Agent 1)
```bash
# Process all PDFs in the current directory:
./run_agent.sh

# Or process a specific PDF or directory:
./run_agent.sh --file "path/to/law.pdf" -o "markdown_output"
```

---

## 8. Deployment Options

Because `web_app/` has zero server-side runtime dependencies, it can be deployed to any static host in under 60 seconds:

* **GitHub Pages**: Set source branch to `main` and folder to `/web_app`.
* **Vercel / Netlify**: Deploy with root directory set to `web_app/`.
* **Zero-Config Local**: Simply double-click `web_app/index.html` on any computer.

---

## 9. License & Authorship

Developed by **Emilsys Zanella** ([@emilsyszanella](https://github.com/emilsyszanella)).  
Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
