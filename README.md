# TaskKeeper

A single-user personal task manager featuring a **FastAPI** REST backend, **SQLite** persistence, and a modern single-page **Kanban** board styled with high-fidelity glassmorphism.

## 🚀 Key Features
- **Kanban Board:** Organize tasks into **To Do**, **In Progress**, and **Done** columns.
- **Detailed Task Modal:** Add descriptions, select priorities (low, medium, high), set due dates, and update statuses.
- **Visual Indicators:** Color-coded priority badges and warning highlights for overdue tasks.
- **Soft-Delete & Trash Bin:** Delete tasks safely without losing them. View, restore, or permanently delete tasks from the Trash view.
- **API Documentation:** Interactive Swagger UI automatically generated at `/docs`.
- **Zero-Config Database:** Automatically initializes and self-migrates on startup.

---

## 🛠️ Prerequisites
- **Python 3.10+**
- **pip**

---

## 💻 Local Setup & Run

Follow these steps to get the application running locally on your machine:

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd TaskKeeper
   ```

2. **Create and activate a Python virtual environment:**
   - **Windows (PowerShell/CMD):**
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server:**
   ```bash
   uvicorn main:app --reload
   ```

5. **Open in browser:**
   - App: [http://localhost:8000](http://localhost:8000)
   - Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Running Tests

FastAPI routes, database migrations, validations, and CRUD operations are fully covered by unit tests.

To run the test suite locally:
```bash
pytest
```
