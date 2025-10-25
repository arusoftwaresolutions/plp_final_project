# 🌍 SDG 1: No Poverty – AI-Powered Budgeting & Microloan Platform

A **full-stack, AI-driven web application** designed to support **low-income families** through **financial literacy**, **personalized budgeting advice**, and **community microloans**.  
This project aligns with the **United Nations Sustainable Development Goal 1 (No Poverty)** — empowering users to improve financial stability with the help of AI.

---

### 🔗 Live Demo  
[👉 Visit the Live App](https://poverty-alleviation.onrender.com)

### 💻 GitHub Repository  
[🔗 https://github.com/arusoftwaresolutions/plp_final_project](https://github.com/arusoftwaresolutions/plp_final_project)

---

## ✨ Key Features

### 💬 AI-Powered Financial Coaching
- Personalized budgeting recommendations using **AI (OpenAI API)**.  
- Friendly, easy-to-understand financial tips — no complex jargon.  
- Offline support with fallback rules if AI is unreachable.  

### 💸 Crowdfunding & Microloans
- Community crowdfunding campaigns for families in need.  
- Microloan request and approval system for small businesses.  
- Transparent, secure donation and funding process.  

### 🗺️ Geospatial Poverty Analysis
- Integrated **PostGIS** for visualizing poverty-affected areas.  
- Data-driven mapping to prioritize regions for aid programs.  

### 📱 Progressive Web App (PWA)
- Mobile-first design built with **React + TailwindCSS + TypeScript**.  
- Installable as a native-like app on mobile and desktop.  
- Optimized for low-bandwidth and offline use.  

### 🔒 Privacy & Security
- No hard-coded secrets; all config handled via environment variables.  
- Data encryption and privacy-first design.  
- Compliant with GDPR and data deletion policies.  

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | React, TypeScript, Vite, TailwindCSS |
| **Backend** | Node.js, Express.js |
| **Database** | PostgreSQL + PostGIS |
| **Cache/Queue** | Redis |
| **AI Engine** | OpenAI GPT (via API) |
| **Deployment** | Render (Static Site + Web Service) |
| **Testing** | Jest (backend) |
| **CI/CD** | GitHub Actions |

---

## ⚙️ Environment Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/arusoftwaresolutions/plp_final_project.git
cd plp_final_project
```

### 2️⃣ Configure Environment Variables
Copy the example environment file and update all fields:

```bash
cp .env.example .env
```

| Variable | Description |
|-----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `MODEL_NAME` | AI model name (e.g. `gpt-4o-mini`) |
| `JWT_SECRET` | Secret for JWT authentication |
| `FRONTEND_URL` | Allowed frontend origins (comma-separated) |
| `NODE_ENV` | Environment (`development` or `production`) |
| `REDIS_URL` | Redis connection string |
| `VITE_API_BASE_URL` | Backend API base URL for frontend |

---

## 🧑‍💻 Running Locally

### Backend
```bash
cd apps/backend
npm install
npm run dev
```

### Frontend
```bash
cd apps/frontend
npm install
npm run dev
```

### Database Setup
Make sure PostGIS is enabled in your PostgreSQL database:

```sql
CREATE EXTENSION postgis;
```

Run migrations:

```bash
psql < db/migrations/001_init.sql
psql < db/migrations/002_seed.sql
```

---

## 🚀 Deployment on Render

### Backend (Web Service)
**Build Command:**
```bash
npm install && npm run build
```

**Start Command:**
```bash
npm run start
```

**Health Check Path:**  
`/api/health`

---

### Frontend (Static Site)
**Build Command:**
```bash
npm run build
```

**Publish Directory:**  
`dist`

---

### Database
Use **Render PostgreSQL Add-On**, then run:
```sql
CREATE EXTENSION postgis;
```

---

### Environment Variables
Set all `.env` values in the Render Environment Settings.

---

## 🧠 AI Prompt System

The AI assistant behavior is defined in:

```
ai/system_prompt.txt
```

This file ensures the AI produces **human-readable budgeting advice** (no JSON or code shown to users).

---

### 🧩 Example Input to AI Service
```
Family of 4, income = 3000 ETB.
Rent = 1000, food = 1200, transport = 200, phone = 150, school = 150.
Goal: save 300 ETB monthly.
```

### 💬 Example AI Output (shown to user)
```
You make about 3 000 ETB each month.
Rent and food take most of it — that’s okay.
Try buying grains and oil in bulk to save 150 ETB.
Cut down on phone use slightly to add another 50 ETB.
That gives you 200 ETB to start saving for school needs.
Keep going — small steps make a big difference!
```

---

## 🧪 Testing

### Run Tests
```bash
npm run test
```

### ✅ Sample Test Assertions
- AI advice must be plain text, not JSON.  
- `/api/health` returns HTTP 200 and `{status:"ok"}`.  
- Budget allocations should not exceed income.

Example (Jest):
```js
expect(typeof aiResponse).toBe("string");
expect(aiResponse.includes("{")).toBe(false);
```

---

### 📊 Sample Integration Tests
```bash
# 1️⃣ Register User
curl -X POST https://your-backend.onrender.com/api/users -d '{"name":"TestUser","email":"test@example.com"}'

# 2️⃣ Add Expenses
curl -X POST https://your-backend.onrender.com/api/transactions -d '{"category":"food","amount":1000}'

# 3️⃣ Get AI Advice
curl -X GET https://your-backend.onrender.com/api/ai/budget/1
```

**Expected Output:**
```
Based on your income of 3 000 ETB, you can save about 200 ETB this month.
Start by reducing phone and snack expenses slightly.
You’re doing great — every small effort counts!
```

---

## 👥 Contributing

We welcome contributions from developers, researchers, and open-source enthusiasts.

### Steps to Contribute
1. **Fork** this repository  
2. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Commit your changes**
   ```bash
   git commit -m "Add: your feature or fix"
   ```
4. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request** on GitHub  

Before submitting:
- Ensure code follows **ESLint + Prettier** standards  
- Add or update tests  
- Verify successful build and test run before PR submission  

---

## 🧭 Project Overview

This project demonstrates how **AI** can empower communities to:

- Learn and practice budgeting  
- Access microloans and community funding  
- Analyze poverty patterns for data-driven impact  

It is optimized for scalability, low bandwidth, and accessibility in developing regions.

---

## 🙌 Acknowledgments

- **OpenAI API** – powering intelligent financial insights  
- **Render** – enabling easy, reliable cloud deployment  
- **Power Learn Project Africa** – for educational support  

---

**Made with ❤️ by Araya Haftu and Arusoftware Solutions**  
🔗 [https://poverty-alleviation.onrender.com](https://poverty-alleviation.onrender.com)
