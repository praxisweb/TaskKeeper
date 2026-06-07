# Gemini Project Context

## Skill Routing

If the user's request matches any of the following skills, always invoke the corresponding **Skill tool** as the first action.
These skills have dedicated workflows defined to provide highly accurate reasoning.

Key Routing Rules:
- Product ideas, feasibility studies, brainstorming → invoke office-hours
- Bugs, errors, root cause investigation → invoke investigate
- Shipping, deployment, pushing, PR creation → invoke ship
- QA, site testing, bug finding → invoke qa
- Code review, checking diffs → invoke review
- Document updates after release → invoke document-release
- Weekly retrospectives → invoke retro
- Design systems, brand consultation → invoke design-consultation
- Visual audits, design adjustments → invoke design-review
- Architecture reviews → invoke plan-eng-review
- Self-reflection, code of conduct check, conducting retrospectives → invoke antigravity-reflection

## AI Agent Guidance (GStack Workflow)

This project utilizes GStack's powerful "autonomous workflows."

### 1. Importance of Planning and CEO Reviews
Before starting implementation, always run `/autoplan` or individual reviews (such as `/plan-ceo-review`).
In particular, during the **CEO review**, the AI will act as a "Silicon Valley founder" rather than a "developer" to rigorously (but constructively) evaluate the plan's validity.

### 2. Interactive Decision Making (AskUserQuestion)
During a GStack workflow, the AI may ask questions in the following formats:
- **Re-ground:** Re-confirming the current situation.
- **Simplify:** Explaining the problem simply.
- **Recommend:** AI-recommended option (prioritizing completeness score of 10/10).
- **Options:** Presenting options like A, B, etc.
The user only needs to reply with something like **"A, please"** for the AI to autonomously continue its work.

### 3. Principle of Completeness (Boil the Lake)
Because the marginal cost of AI implementation is extremely low, we always recommend "flawless implementation considering edge cases" over "just getting code to work." By choosing the option with a "completeness score of 10/10" presented by the AI, you will get high-quality code with minimal technical debt.
