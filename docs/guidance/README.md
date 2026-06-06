# 📋 Engineering Guidance

This document outlines the coding standards, workflow, testing expectations, and conventions for TaskKeeper.

---

## 🛠️ Tech Stack & Tooling
-   **Core**: Vanilla HTML & Vanilla CSS with modern Javascript (ESNext).
-   **Styling**: Premium modern CSS (custom variables, HSL colors, grid/flexbox layouts, responsive design, glassmorphism, micro-interactions).
-   **Linter & Formatter**: ESLint + Prettier.

---

## 🌿 Git & Worktree Workflow

Since this repository is configured to utilize Git Worktrees, please adhere to the following development workflow:

### 1. The Main Repository
-   The base folder (`c:\Users\jason\Documents\Code\TaskKeeper`) contains the primary repository database. Avoid working directly on `main` in the primary folder if you want to keep your workspace clean.
-   Create an empty/initial commit before adding worktrees.

### 2. Creating a Feature Worktree
Instead of switching branches inside a single folder, create a new directory for your feature:
```powershell
# In the root repository folder:
git worktree add ../TaskKeeper-<feature-name> -b <feature-branch>
```

### 3. Working inside the Worktree
Navigate to your newly created worktree folder:
```powershell
cd ../TaskKeeper-<feature-name>
# Run npm install if dependencies have changed, then start developing.
```

### 4. Cleaning up Completed Worktrees
Once your feature is merged and the branch is deleted:
```powershell
# Remove the worktree folder and prune Git's references
git worktree remove ../TaskKeeper-<feature-name>
git worktree prune
```

---

## 🎨 Styling & UI Principles
To maintain a premium look and feel, follow these UI guidelines:
-   **Typography**: Use modern sans-serif typefaces (e.g. Inter, Outfit, or system-ui defaults). Avoid default serif fonts.
-   **Color Palettes**: Use Tailwind-like curated HSL palette variables (e.g., `--primary: 220 90% 56%; --bg-dark: 224 71% 4%;`). Avoid hardcoded basic web colors (`red`, `blue`, `green`).
-   **Micro-interactions**: Every clickable element must have a clear `:hover` and `:active` state. Use transition animations (e.g., `transition: all 0.2s ease;`).
-   **Responsiveness**: Build mobile-first using CSS Grid or Flexbox, incorporating CSS Media Queries for larger screens.

---

## 🧪 Testing Expectations
-   **Unit Tests**: Write unit tests for business logic in the stores and utility functions.
-   **E2E Tests**: Use Playwright or Cypress for core task-handling user flows.
-   **Verification**: Always run `npm run test` and verify code builds cleanly before staging changes.
