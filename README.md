# Neeraj Kumar - AI/ML Engineering & Data Science Portfolio

A premium, interactive single-page portfolio designed for AI/ML engineering and analytics careers. It highlights verified academic achievements (IIT Madras Data Science & REC Bijnor B.Tech IT), GATE CSE qualification, professional experiences, and features interactive dashboard modules mimicking developer tools.

## 🚀 Live Features

### 1. Cybernetic Obsidian UI
- Modern dark obsidian aesthetic with glassmorphism cards and vibrant glowing cyber-hues.
- Smooth responsive layout with customized scrollbar styling and hover micro-animations.

### 2. Animated SVG Neural Network
- An interactive vector network representation of key skills (Deep Learning, Machine Learning, NLP, LangChain/RAG, DSA, and Data Analytics).
- Symmetrical layout featuring a vertical center spine and synchronized clockwise-flowing data packet pulses.

### 3. Interactive AI Training Playground
- A live simulated training console where users can trigger a model convergence loop.
- Updates training epoch parameters (Loss, Accuracy, Learning Rate, Batch Size) in real-time, plotting dynamic SVG validation curves.

### 4. Interactive Typewriter Terminal Console
- Boots up sequentially after successful model training completion.
- Evaluates query prompts line-by-line:
  - `/profile` - Prints academic details and professional summary.
  - `/skills` - Maps core competencies in ML, DS, Programming, and Web.
  - `/projects` - Lists technical repositories and Kaggle work.
  - `/gate` - Summarizes GATE 2026 CSE certification details.
  - `/why-hire` - Summarizes key value propositions.
  - `clear` - Resets console buffer.

### 5. Chronological Experience & Verified Links
- Timeline mapping academic roles (Class Representative, IIT Madras Group Leader) and select internships (Lenovo LeAP Gen, IIT Ropar Selection, Career Analytics Selection).
- Hyperlinked credential checks directly connected to verification PDFs on Google Drive.

---

## 🛠️ Stack & Technologies
- **Core**: HTML5, Vanilla CSS3, Modern ES6 Javascript.
- **Visuals**: Vector SVG Graphs, CSS Keyframe Animations.
- **Build System**: [Vite](https://vitejs.dev/) (Production compilation & asset optimization).

---

## 💻 Local Development Setup

### Prerequisites
Make sure you have [Node.js](https://nodejs.org/) installed on your machine.

### Installation
1. Clone this repository to your local directory.
2. Open terminal in the directory and run:
   ```bash
   npm install
   ```

### Running Local Dev Server
Launch Vite's hot-reloading development server:
```bash
npm run dev
```
Open **`http://localhost:3000`** in your browser.

### Building for Production
To build optimized, minified static assets to the `/dist` directory for production deployment (e.g., to Vercel, Netlify, or Render):
```bash
npm run build
```
The compiled files can be previewed locally using:
```bash
npm run preview
```
