const { useState, useEffect } = React;
const { createRoot } = ReactDOM;

// Firebase Initialization
firebase.initializeApp(window.firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();

// Firebase Auth Helpers
async function signInWithGoogle() {
  try {
    const provider = new firebase.auth.GoogleAuthProvider();
    await auth.signInWithPopup(provider);
  } catch (error) {
    console.error('Sign-in failed:', error);
    alert('Sign-in failed: ' + error.message);
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

const DEFAULT_PREFS = { workStart: '09:00', workEnd: '18:00', breakDuration: 15, focusBlocks: true, workStyle: 'balanced', bufferTime: 10, energyPeak: 'morning', timezone: 'Europe/Amsterdam' };

const INIT_TASKS = [
  { id: 1, name: 'Write project proposal', deadline: '2025-05-05', duration: 90, priority: 'high', done: false, source: 'manual' },
  { id: 2, name: 'Review team pull requests', deadline: '2025-05-03', duration: 45, priority: 'med', done: false, source: 'manual' },
  { id: 3, name: 'Prepare slides for presentation', deadline: '2025-05-06', duration: 120, priority: 'high', done: false, source: 'manual' },
  { id: 4, name: 'Reply to client emails', deadline: '2025-05-02', duration: 30, priority: 'med', done: false, source: 'manual' },
];

function formatDuration(minutes) {
  return `${minutes}m`;
}

function buildSampleSchedule(tasks, prefs) {
  const pending = tasks.filter((task) => !task.done);
  let currentMinutes = 9 * 60;
  return pending.slice(0, 8).map((task) => {
    const start = `${String(Math.floor(currentMinutes / 60)).padStart(2, '0')}:${String(currentMinutes % 60).padStart(2, '0')}`;
    currentMinutes += task.duration;
    const end = `${String(Math.floor(currentMinutes / 60)).padStart(2, '0')}:${String(currentMinutes % 60).padStart(2, '0')}`;
    currentMinutes += prefs.bufferTime;
    return { time: start, end, name: task.name, note: 'Planned with your preferences', type: 'task' };
  });
}

function App() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [tab, setTab] = useState('planner');
  const [tasks, setTasks] = useState(INIT_TASKS);
  const [prefs, setPrefs] = useState(DEFAULT_PREFS);
  const [schedule, setSchedule] = useState(null);
  const [aiNote, setAiNote] = useState('');
  const [nextId, setNextId] = useState(10);
  const [form, setForm] = useState({ name: '', deadline: '', duration: 30, priority: 'med' });
  const [gmailItems, setGmailItems] = useState(null);
  const [calendarEvents, setCalendarEvents] = useState(null);
  const [driveItems, setDriveItems] = useState(null);
  const [loading, setLoading] = useState({ plan: false, gmail: false, calendar: false, drive: false });

  // Auth listener
  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (currentUser) => {
      setUser(currentUser);
      if (currentUser) {
        const savedTasks = await loadTasks(currentUser.uid);
        if (savedTasks.length > 0) {
          setTasks(savedTasks);
        }
      }
      setAuthLoading(false);
    });
    return () => unsubscribe();
  }, []);

  // Save tasks to Firestore when they change
  useEffect(() => {
    if (user && tasks.length > 0) {
      saveTasks(user.uid, tasks);
    }
  }, [tasks, user]);

  const addTask = () => {
    if (!form.name.trim()) return;
    setTasks((current) => [...current, { id: nextId, ...form, done: false, source: 'manual' }]);
    setNextId((n) => n + 1);
    setForm({ name: '', deadline: '', duration: 30, priority: 'med' });
  };

  const toggleDone = (id) => setTasks((current) => current.map((task) => (task.id === id ? { ...task, done: !task.done } : task)));
  const deleteTask = (id) => setTasks((current) => current.filter((task) => task.id !== id));

  const generatePlan = () => {
    setLoading((current) => ({ ...current, plan: true }));
    setTimeout(() => {
      setSchedule(buildSampleSchedule(tasks, prefs));
      setAiNote('This is a demo plan based on your tasks and preferences.');
      setLoading((current) => ({ ...current, plan: false }));
    }, 400);
  };

  const scanGmail = () => {
    setLoading((current) => ({ ...current, gmail: true }));
    setTimeout(() => {
      setGmailItems([
        { name: 'Follow up on proposal', duration: 30, priority: 'high', deadline: '2025-05-05', from: 'Alice', subject: 'Proposal review' },
        { name: 'Prepare demo notes', duration: 45, priority: 'med', deadline: '', from: 'Product Team', subject: 'Demo prep' },
      ]);
      setLoading((current) => ({ ...current, gmail: false }));
    }, 500);
  };

  const fetchCalendar = () => {
    setLoading((current) => ({ ...current, calendar: true }));
    setTimeout(() => {
      setCalendarEvents([
        { name: 'Team standup', start: '10:00', end: '10:30', date: '2025-05-02', calendar: 'Work' },
        { name: 'Client call', start: '14:00', end: '14:45', date: '2025-05-02', calendar: 'Sales' },
      ]);
      setLoading((current) => ({ ...current, calendar: false }));
    }, 500);
  };

  const scanDrive = () => {
    setLoading((current) => ({ ...current, drive: true }));
    setTimeout(() => {
      setDriveItems([
        { name: 'Review product brief', duration: 30, priority: 'med', filename: 'product-brief.docx' },
        { name: 'Update roadmap', duration: 45, priority: 'high', filename: 'roadmap.xlsx' },
      ]);
      setLoading((current) => ({ ...current, drive: false }));
    }, 500);
  };

  const doneCount = tasks.filter((task) => task.done).length;
  const pendingMinutes = tasks.filter((task) => !task.done).reduce((sum, task) => sum + task.duration, 0);

  return (
    <div className="app">
      <div className="header">
        <div className="logo">Plann<span>AI</span></div>
        <div className="tabs">
          {['planner', 'schedule', 'integrations', 'preferences'].map((value) => (
            <button key={value} className={`tab ${tab === value ? 'active' : ''}`} type="button" onClick={() => setTab(value)}>{value[0].toUpperCase() + value.slice(1)}</button>
          ))}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginLeft: 'auto' }}>
          {authLoading ? (
            <span style={{ fontSize: '13px', color: '#6b6b60' }}>Loading...</span>
          ) : user ? (
            <>
              <span style={{ fontSize: '13px', color: '#8a8a7a' }}>
                {user.email}
              </span>
              <button
                onClick={() => signOut()}
                style={{
                  padding: '0.4rem 0.8rem',
                  background: '#7a3a3a',
                  color: '#e8e4da',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  fontSize: '12px',
                  fontWeight: '600'
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
                color: '#e8e4da',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: '600'
              }}
            >
              Sign In with Google
            </button>
          )}
        </div>
      </div>

      {(tab === 'planner' || tab === 'schedule') && (
        <div className="main">
          {!user && (
            <div style={{ gridColumn: '1/-1', background: '#2e1a1a', border: '1px solid #7a3a3a', borderRadius: '8px', padding: '1.5rem', margin: '1.5rem', textAlign: 'center' }}>
              <div style={{ fontSize: '16px', color: '#e8e4da', marginBottom: '1rem' }}>📝 Sign in to save your tasks</div>
              <button onClick={() => signInWithGoogle()} style={{ padding: '0.6rem 1.2rem', background: '#6b8c5a', color: '#e8e4da', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px', fontWeight: '600' }}>
                Sign In with Google
              </button>
            </div>
          )}
          <div className="sidebar">
            <div className="panel">
              <div className="panel-title">Add Task</div>
              <div className="form-group">
                <label className="form-label">Task name</label>
                <input className="form-input" value={form.name} placeholder="What needs to get done?" onChange={(e) => setForm((cur) => ({ ...cur, name: e.target.value }))} onKeyDown={(e) => e.key === 'Enter' && addTask()} />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Deadline</label>
                  <input type="date" className="form-input" value={form.deadline} onChange={(e) => setForm((cur) => ({ ...cur, deadline: e.target.value }))} />
                </div>
                <div className="form-group">
                  <label className="form-label">Duration</label>
                  <select className="form-input" value={form.duration} onChange={(e) => setForm((cur) => ({ ...cur, duration: +e.target.value }))}>
                    {[15, 30, 45, 60, 90, 120, 180].map((value) => <option key={value} value={value}>{value} min</option>)}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Priority</label>
                <div className="priority-grid">
                  {['low', 'med', 'high'].map((value) => (
                    <button key={value} type="button" className={`priority-btn ${value} ${form.priority === value ? 'active' : ''}`} onClick={() => setForm((cur) => ({ ...cur, priority: value }))}>{value === 'low' ? 'Low' : value === 'med' ? 'Med' : 'High'}</button>
                  ))}
                </div>
              </div>
              <button className="add-btn" type="button" onClick={addTask} disabled={!user} style={{ opacity: user ? 1 : 0.5, cursor: user ? 'pointer' : 'not-allowed' }}>+ Add Task</button>
            </div>

            <div className="panel">
              <div className="panel-title">AI Schedule</div>
              {[['Work window', `${prefs.workStart}–${prefs.workEnd}`], ['Energy peak', prefs.energyPeak], ['Style', prefs.workStyle], ['Pending', `${tasks.filter((task) => !task.done).length} tasks`]].map(([label, value]) => (
                <div key={label} className="pref-row"><span className="pref-label">{label}</span><span className="pref-value">{value}</span></div>
              ))}
              <button className="ai-btn" type="button" onClick={generatePlan} disabled={loading.plan}>{loading.plan ? <><div className="spinner sm"></div>Planning…</> : <><div className="ai-dot"></div>Generate My Plan</>}</button>
            </div>
          </div>

          <div className="content">
            {tab === 'planner' && (
              <>
                <div className="stats-row">
                  <div className="stat-card"><div className="stat-num">{tasks.length}</div><div className="stat-label">Total</div></div>
                  <div className="stat-card"><div className="stat-num">{doneCount}</div><div className="stat-label">Done</div></div>
                  <div className="stat-card"><div className="stat-num">{Math.round(pendingMinutes / 60)}h</div><div className="stat-label">Pending</div></div>
                </div>
                <div className="section-label">All Tasks</div>
                <div className="task-list">
                  {tasks.length === 0 && <div className="task-empty">No tasks yet — add one above or import from integrations</div>}
                  {tasks.map((task) => (
                    <div key={task.id} className={`task-card ${task.priority}`}>
                      <button className={`task-check ${task.done ? 'done' : ''}`} type="button" onClick={() => toggleDone(task.id)} />
                      <div className="task-info">
                        <div className={`task-name ${task.done ? 'done' : ''}`}>{task.name}</div>
                        <div className="task-meta">
                          {task.deadline && <span className="task-tag">📅 {task.deadline}</span>}
                          <span className="task-tag">⏱ {formatDuration(task.duration)}</span>
                          <span className={`chip ${task.priority}`}>{task.priority === 'med' ? 'medium' : task.priority}</span>
                          {task.source !== 'manual' && <span className={`src-badge ${task.source}`}>{task.source}</span>}
                        </div>
                      </div>
                      <button className="task-delete" type="button" onClick={() => deleteTask(task.id)}>×</button>
                    </div>
                  ))}
                </div>
              </>
            )}

            {tab === 'schedule' && (
              <>
                {!schedule && !loading.plan && <div className="task-empty" style={{ paddingTop: '4rem' }}>Hit "Generate My Plan" to create your schedule.</div>}
                {aiNote && <div style={{ background: '#171812', border: '1px solid #3a5a3a', borderRadius: 9, padding: '1rem 1.25rem', marginBottom: '1.5rem', borderLeft: '3px solid #6b8c5a' }}><div style={{ fontSize: 11, color: '#6b8c5a', marginBottom: 4, letterSpacing: '0.08em', textTransform: 'uppercase', fontWeight: 600 }}>AI Planner</div><div style={{ fontSize: 14, color: '#c8d4b8', fontStyle: 'italic' }}>{aiNote}</div></div>}
                {schedule && (
                  <div className="timeline">
                    {schedule.map((block, index) => (
                      <div key={index} className="tl-item">
                        <div className={`tl-dot ${block.type === 'break' ? 'break' : ''}`}></div>
                        <div className="tl-time">{block.time} — {block.end}</div>
                        <div className="tl-name" style={{ color: block.type === 'break' ? '#6b7a9a' : '#e8e4da' }}>{block.name}</div>
                        {block.note && <div className="tl-note">{block.note}</div>}
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {tab === 'integrations' && (
        <div className="integ-page">
          <div className="page-title">Integrations</div>
          <div className="page-sub">Connect your apps to automatically import tasks, sync calendars, and keep your planner up to date.</div>

          <div className="integ-section-label">Connected</div>
          <div className="integ-grid">
            <div className="i-card on">
              <div className="i-head"><div className="i-icon gmail">✉️</div><div><div className="i-name">Gmail</div><div className="i-sub">Google Mail</div></div><span className="badge on">● Connected</span></div>
              <div className="i-desc">Scan your inbox for action items and import them as tasks.</div>
              <div className="i-actions"><button className={`i-btn${loading.gmail ? ' loading' : ''}`} type="button" onClick={scanGmail} disabled={loading.gmail}>{loading.gmail ? <><div className="spinner sm"></div>Scanning inbox…</> : '✉️ Scan inbox for tasks'}</button></div>
              {gmailItems && <div className="result-box">{gmailItems.length === 0 ? <div className="empty-box">No actionable emails found.</div> : gmailItems.map((item, index) => <div key={index} className="r-item"><div className="r-info"><div className="r-name">{item.name}</div><div className="r-sub">{item.from} · {item.duration}m · {item.priority}{item.deadline && ` · due ${item.deadline}`}</div></div><button className="r-add" type="button">+ Add</button></div>)}</div>}
            </div>

            <div className="i-card on">
              <div className="i-head"><div className="i-icon gcal">📅</div><div><div className="i-name">Google Calendar</div><div className="i-sub">Events & scheduling</div></div><span className="badge on">● Connected</span></div>
              <div className="i-desc">View upcoming events and keep your planner aligned with your calendar.</div>
              <div className="i-actions"><button className={`i-btn${loading.calendar ? ' loading' : ''}`} type="button" onClick={fetchCalendar} disabled={loading.calendar}>{loading.calendar ? <><div className="spinner sm"></div>Loading calendar…</> : '📅 View upcoming events'}</button></div>
              {calendarEvents && <div className="result-box">{calendarEvents.length === 0 ? <div className="empty-box">No upcoming events found.</div> : calendarEvents.map((event, index) => <div key={index} className="e-item"><div className="e-name">{event.name}</div><div className="e-time">{event.date} · {event.start}–{event.end}{event.calendar ? ` · ${event.calendar}` : ''}</div></div>)}</div>}
            </div>

            <div className="i-card on">
              <div className="i-head"><div className="i-icon gdrive">📁</div><div><div className="i-name">Google Drive</div><div className="i-sub">Documents & files</div></div><span className="badge on">● Connected</span></div>
              <div className="i-desc">Detect recent files that may contain pending work.</div>
              <div className="i-actions"><button className={`i-btn${loading.drive ? ' loading' : ''}`} type="button" onClick={scanDrive} disabled={loading.drive}>{loading.drive ? <><div className="spinner sm"></div>Scanning Drive…</> : '📁 Scan Drive for pending docs'}</button></div>
              {driveItems && <div className="result-box">{driveItems.length === 0 ? <div className="empty-box">No pending documents found.</div> : driveItems.map((item, index) => <div key={index} className="r-item"><div className="r-info"><div className="r-name">{item.name}</div><div className="r-sub">{item.filename} · {item.duration}m · {item.priority}</div></div><button className="r-add" type="button">+ Add</button></div>)}</div>}
            </div>
          </div>

          <div className="integ-section-label">Available to Connect</div>
          <div className="integ-grid">
            {[
              { key: 'outlook', icon: '📬', name: 'Outlook', sub: 'Microsoft Mail & Calendar', desc: 'Sync Outlook tasks and calendar items.' },
              { key: 'notion', icon: '📓', name: 'Notion', sub: 'Workspace & notes', desc: 'Import tasks and notes from Notion.' },
              { key: 'slack', icon: '💬', name: 'Slack', sub: 'Team messaging', desc: 'Turn Slack reminders into planner tasks.' },
              { key: 'todoist', icon: '✅', name: 'Todoist', sub: 'Task management', desc: 'Two-way sync with Todoist projects.' },
            ].map((item) => (
              <div key={item.key} className="i-card"><div className="i-head"><div className={`i-icon ${item.key}`}>{item.icon}</div><div><div className="i-name">{item.name}</div><div className="i-sub">{item.sub}</div></div><span className="badge soon">Coming soon</span></div><div className="i-desc" style={{ opacity: 0.45 }}>{item.desc}</div><button className="i-connect" type="button" disabled>Connect {item.name}</button></div>
            ))}
          </div>
        </div>
      )}

      {tab === 'preferences' && (
        <div className="page-prefs">
          <div className="pref-section">
            <div className="pref-section-title">Work Hours</div>
            <div className="form-row">
              <div className="form-group"><label className="form-label">Start time</label><input type="time" className="form-input" value={prefs.workStart} onChange={(e) => setPrefs((cur) => ({ ...cur, workStart: e.target.value }))} /></div>
              <div className="form-group"><label className="form-label">End time</label><input type="time" className="form-input" value={prefs.workEnd} onChange={(e) => setPrefs((cur) => ({ ...cur, workEnd: e.target.value }))} /></div>
            </div>
            <div className="form-group"><label className="form-label">Break duration (minutes)</label><select className="form-input" value={prefs.breakDuration} onChange={(e) => setPrefs((cur) => ({ ...cur, breakDuration: +e.target.value }))}>{[5, 10, 15, 20, 30].map((value) => <option key={value} value={value}>{value} min</option>)}</select></div>
            <div className="form-group"><label className="form-label">Buffer between tasks</label><select className="form-input" value={prefs.bufferTime} onChange={(e) => setPrefs((cur) => ({ ...cur, bufferTime: +e.target.value }))}>{[0, 5, 10, 15, 20].map((value) => <option key={value} value={value}>{value} min</option>)}</select></div>
          </div>
          <div className="pref-section"><div className="pref-section-title">Personal Rhythm</div><div className="form-group"><label className="form-label">Energy peak</label><select className="form-input" value={prefs.energyPeak} onChange={(e) => setPrefs((cur) => ({ ...cur, energyPeak: e.target.value }))}><option value="morning">Morning (9–12)</option><option value="midday">Midday (12–15)</option><option value="afternoon">Afternoon (15–18)</option></select></div><div className="form-group"><label className="form-label">Work style</label><select className="form-input" value={prefs.workStyle} onChange={(e) => setPrefs((cur) => ({ ...cur, workStyle: e.target.value }))}><option value="balanced">Balanced</option><option value="deep-work">Deep work — long focus blocks</option><option value="sprints">Sprints — short intense bursts</option><option value="flexible">Flexible</option></select></div><div className="form-group" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}><label className="form-label" style={{ marginBottom: 0 }}>Enable focus blocks (Pomodoro-style)</label><label className="toggle"><input type="checkbox" checked={prefs.focusBlocks} onChange={(e) => setPrefs((cur) => ({ ...cur, focusBlocks: e.target.checked }))} /><span className="toggle-slider"></span></label></div></div>
          <div className="pref-section"><div className="pref-section-title">Location & Time</div><div className="form-group"><label className="form-label">Timezone</label><select className="form-input" value={prefs.timezone} onChange={(e) => setPrefs((cur) => ({ ...cur, timezone: e.target.value }))}>{['Europe/Amsterdam', 'Europe/London', 'America/New_York', 'America/Los_Angeles', 'Asia/Tokyo', 'Asia/Dubai'].map((value) => <option key={value} value={value}>{value}</option>)}</select></div></div>
          <button className="add-btn" type="button" onClick={() => setTab('planner')} style={{ maxWidth: 200 }}>Save Preferences</button>
        </div>
      )}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
