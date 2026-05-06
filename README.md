# PlannAI

A personal AI-powered daily planner that connects to your Google apps to automatically surface tasks, build an optimized schedule, and push it back to your calendar.

## Features

- **AI Schedule Generation** — Claude analyzes your pending tasks and personal preferences to generate an optimized daily plan
- **Gmail Integration** — Scans your inbox for actionable items and converts them into tasks
- **Google Calendar** — View upcoming events and export your AI-generated schedule directly to your calendar
- **Google Drive** — Detects recently modified documents that likely need attention
- **Task Management** — Add tasks manually with priority, deadline, and duration; mark them complete
- **Preferences** — Configure your work hours, break duration, energy peak, and work style to personalize the schedule

## Integrations

| Service | Status |
|---|---|
| Gmail | Connected |
| Google Calendar | Connected |
| Google Drive | Connected |
| Outlook | Coming soon |
| Notion | Coming soon |
| Slack | Coming soon |
| Todoist | Coming soon |

## Tech Stack

- React (via Babel CDN — no build step required)
- Claude API (`claude-sonnet-4-20250514`) for AI scheduling and integration parsing
- Google MCP servers for Gmail, Calendar, and Drive access
- Firebase Auth (Google sign-in) + Firestore for cloud task storage

## Setup

### 1. Firebase

See [AI-planner/FIREBASE_SETUP.md](AI-planner/FIREBASE_SETUP.md) for full instructions on configuring Firebase authentication and Firestore.

### 2. Run locally

Open `AI-planner/main.html` in a browser, or serve it with any static file server:

```bash
npx serve AI-planner
```

### 3. Deploy

The app is deployed via GitHub Pages at:  
`https://roemer94.github.io/AI-planner/`

## Project Structure

```
AI-planner/
  main.html          # Entry point + full React app (inline)
  FIREBASE_SETUP.md  # Firebase integration guide
README.md
```
