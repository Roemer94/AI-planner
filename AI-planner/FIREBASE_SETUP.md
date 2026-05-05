# Firebase Integration Setup Guide for PlannAI

## Overview
This guide walks you through integrating Firebase with your PlannAI app to enable:
- ✅ **Authentication**: Google sign-in for secure access
- ✅ **Database**: Firestore to store tasks in the cloud
- ✅ **Authorization**: Public read access + private write access (only you can edit)
- ✅ **Free tier**: Completely free for personal use

---

## Part 1: Get Your Firebase Credentials

### Step 1.1 - Copy Your Firebase Config
1. Go to: https://console.firebase.google.com/project/planai-bd1fb/overview
2. Click on your **"PlannAI Web"** app (in the left sidebar or settings)
3. Scroll down to **"Firebase SDK snippet"**
4. Select **"CDN"** tab (not npm)
5. Copy the entire config object that looks like:

```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "planai-bd1fb.firebaseapp.com",
  projectId: "planai-bd1fb",
  storageBucket: "planai-bd1fb.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_ID",
  appId: "YOUR_APP_ID"
};
```

**Save this somewhere safe** - you'll need it in Step 2.

---

## Part 2: Set Up Firestore Database

### Step 2.1 - Create Firestore Database
1. In Firebase Console, go to **Build** → **Firestore Database** (left sidebar)
2. Click **"Create Database"**
3. Choose **"Start in test mode"** (we'll secure it in Step 2.3)
4. Select region: **Europe (nearest to Netherlands)**
5. Click **"Create"**

### Step 2.2 - Create Collection
1. In Firestore, click **"+ Start collection"**
2. Name it: `tasks`
3. For the first document, click **"Auto ID"**
4. Add this sample field:
   - Field: `name`
   - Type: `string`
   - Value: `Sample Task`
5. Click **"Save"**

### Step 2.3 - Set Security Rules (Important!)
1. Go to **Firestore Database** → **Rules** tab
2. Replace the default rules with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Public can read all tasks
    match /tasks/{document=**} {
      allow read: if true;
      allow write: if request.auth.uid == resource.data.userId;
    }
    
    // Users can only read/write their own user doc
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
    }
  }
}
```

3. Click **"Publish"**

---

## Part 3: Set Up Authentication

### Step 3.1 - Enable Google Sign-In
1. Go to **Build** → **Authentication** (left sidebar)
2. Click **"Get Started"**
3. Click **"Google"** provider
4. Toggle it **ON**
5. Add your email as a test user
6. Click **"Save"**

### Step 3.2 - Configure OAuth Consent Screen
1. You might see a warning to configure OAuth consent
2. Click the link or go to **Google Cloud Console** → **APIs & Services** → **OAuth consent screen**
3. Select **"External"** and click **"Create"**
4. Fill in the form:
   - App name: `PlannAI`
   - User support email: your email
   - Developer contact: your email
5. Click **"Save and Continue"** through all steps
6. Add your email as a test user

---

## Part 4: Update Your App Code

### Step 4.1 - Update index.html
Replace the scripts section in your `index.html` with:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PlannAI</title>
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <div id="root"></div>

    <!-- Firebase Scripts -->
    <script src="https://www.gstatic.com/firebasejs/10.7.2/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/10.7.2/firebase-auth.js"></script>
    <script src="https://www.gstatic.com/firebasejs/10.7.2/firebase-firestore.js"></script>

    <!-- React & Babel -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

    <!-- Firebase Config & App -->
    <script>
      window.firebaseConfig = {
        apiKey: "PASTE_YOUR_API_KEY_HERE",
        authDomain: "planai-bd1fb.firebaseapp.com",
        projectId: "planai-bd1fb",
        storageBucket: "planai-bd1fb.appspot.com",
        messagingSenderId: "PASTE_YOUR_MESSAGING_ID_HERE",
        appId: "PASTE_YOUR_APP_ID_HERE"
      };
    </script>

    <script type="text/babel" src="app.js"></script>
  </body>
</html>
```

**Important:** Replace the 3 placeholder values with your actual Firebase config from Part 1.

### Step 4.2 - Update app.js
Add this code at the TOP of `app.js` (before the existing code):

```javascript
// Firebase Initialization
firebase.initializeApp(window.firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();

// Firebase Auth Helper
async function signInWithGoogle() {
  try {
    const provider = new firebase.auth.GoogleAuthProvider();
    await auth.signInWithPopup(provider);
  } catch (error) {
    console.error('Sign-in failed:', error);
  }
}

async function signOut() {
  try {
    await auth.signOut();
  } catch (error) {
    console.error('Sign-out failed:', error);
  }
}

// Firestore Helpers
async function saveTasks(userId, tasks) {
  try {
    await db.collection('tasks').doc(userId).set(
      { tasks, lastUpdated: new Date() },
      { merge: true }
    );
  } catch (error) {
    console.error('Error saving tasks:', error);
  }
}

async function loadTasks(userId) {
  try {
    const doc = await db.collection('tasks').doc(userId).get();
    if (doc.exists && doc.data().tasks) {
      return doc.data().tasks;
    }
  } catch (error) {
    console.error('Error loading tasks:', error);
  }
  return [];
}
```

### Step 4.3 - Modify App Component
In your `App()` component, add this at the top:

```javascript
function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Existing state...
  const [tab, setTab] = useState('planner');
  const [tasks, setTasks] = useState(INIT_TASKS);
  // ... rest of existing state

  // Auth listener
  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (currentUser) => {
      setUser(currentUser);
      if (currentUser) {
        // Load tasks from Firestore
        const savedTasks = await loadTasks(currentUser.uid);
        if (savedTasks.length > 0) {
          setTasks(savedTasks);
        }
      }
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  // Save tasks to Firestore when they change
  useEffect(() => {
    if (user && tasks.length > 0) {
      saveTasks(user.uid, tasks);
    }
  }, [tasks, user]);
```

**Note:** You'll need to add `import { useEffect } = React;` at the top if not already there.

### Step 4.4 - Add Login/Logout UI
Add this to your JSX (add to the header section):

```jsx
<div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
  {user ? (
    <>
      <span style={{ fontSize: '14px', color: '#8a8a7a' }}>
        Signed in as {user.email}
      </span>
      <button
        onClick={() => signOut()}
        style={{
          padding: '0.4rem 0.8rem',
          background: '#c86a6a',
          color: '#fff',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          fontSize: '12px'
        }}
      >
        Sign Out
      </button>
    </>
  ) : (
    <button
      onClick={() => signInWithGoogle()}
      style={{
        padding: '0.4rem 0.8rem',
        background: '#6b8c5a',
        color: '#fff',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer',
        fontSize: '12px'
      }}
    >
      Sign In with Google
    </button>
  )}
</div>
```

---

## Part 5: Test Your Setup

### Step 5.1 - Local Testing
1. Commit & push your changes to GitHub
2. Navigate to: http://localhost:8000/index.html
3. Click **"Sign In with Google"**
4. Complete the login
5. Add a task
6. Refresh the page - your task should still be there ✅

### Step 5.2 - Deploy to GitHub Pages
1. In terminal:
```bash
cd "c:\Users\roeme\OneDrive\Documenten\VS code"
git add AI-planner/
git commit -m "Integrate Firebase with authentication and Firestore"
git push origin main
```

2. Your app will be live at: https://roemer94.github.io/AI-planner/index.html

---

## Part 6: Understanding Security

### Public Read Access
- Anyone can view your tasks at the GitHub Pages URL
- They cannot modify tasks (no write access)

### Private Write Access
- Only you (when signed in) can create/edit/delete tasks
- Your tasks are stored under your unique Google user ID
- Other users' tasks won't interfere

### Security Rules Breakdown
```javascript
// Anyone can read all tasks
allow read: if true;

// Only the owner (userId matches auth.uid) can write
allow write: if request.auth.uid == resource.data.userId;
```

---

## Troubleshooting

### Issue: "auth is not defined"
**Solution:** Make sure Firebase scripts are loaded in correct order in `index.html`

### Issue: Tasks not saving
**Solution:** Check browser console (F12) for errors. Verify:
1. Firebase config is correct
2. You're signed in
3. Firestore security rules are published

### Issue: "Quota exceeded"
**Solution:** You're using free tier. That's fine! Just means high traffic. Upgrade when needed.

### Issue: "App not initialized"
**Solution:** Make sure `firebase.initializeApp()` is called before anything else

---

## Next Steps (Optional)

1. **Add more integrations** (Gmail, Calendar, Drive)
2. **Multi-user support** - allow sharing tasks with others
3. **Offline mode** - work offline and sync when online
4. **Mobile app** - use React Native
5. **Analytics** - track usage with Google Analytics

---

## Support Resources
- Firebase Docs: https://firebase.google.com/docs
- Firestore Guide: https://firebase.google.com/docs/firestore
- Auth Guide: https://firebase.google.com/docs/auth/web/manage-users

Good luck! 🚀
