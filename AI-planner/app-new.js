const { useState } = React;
const { createRoot } = ReactDOM;

const DEFAULT_PREFS = { workStart: '09:00', workEnd: '18:00', breakDuration: 15, focusBlocks: true, workStyle: 'balanced', bufferTime: 10, energyPeak: 'morning', timezone: 'Europe/Amsterdam' };

const INIT_TASKS = [
  { id: 1, name: 'Write project proposal', deadline: '2025-05-05', duration: 90, priority: 'high', done: false, source: 'manual' },
  { id: 2, name: 'Review team pull requests', deadline: '2025-05-03', duration: 45, priority: 'med', done: false, source: 'manual' },
  { id: 3, name: 'Prepare slides for presentation', deadline: '2025-05-06', duration: 120, priority: 'high', done: false, source: 'manual' },
  { id: 4, name: 'Reply to client emails', deadline: '2025-05-02', duration: 30, priority: 'med', done: false, source: 'manual' },
];

function parseJSON(raw, fallback = []) {
  try {
    const m = raw.match(/```json([\s\S]*?)```/);
    if (m) return JSON.parse(m[1].trim());
    const m2 = raw.match(/(\[[\s\S]*?\])/);
    if (m2) return JSON.parse(m2[1]);
  } catch (error) {
    console.warn('Failed to parse JSON:', error);
  }
  return fallback;
}

async function ai(prompt, mcps = [], system = '') {
  const apiKey = window.ANTHROPIC_API_KEY || null;
  if (!apiKey) {
    if (prompt.includes('Create an optimized daily schedule')) {
      return `Your planner generated a sample schedule to get started.` +
        '\n```json\n[{"time":"09:00","end":"10:30","name":"Review tasks","note":"Start with your highest priority work","type":"task"}]```';
    }

    if (prompt.includes('Use Gmail')) {
      return '```json\n[]```';
    }

    if (prompt.includes('Use Google Calendar to list my upcoming events')) {
      return '```json\n[]```';
    }

    if (prompt.includes('Use Google Calendar to create these events')) {
      return 'OK';
    }

    if (prompt.includes('Use Google Drive')) {
      return '```json\n[]```';
    }

    return '```json\n[]```';
  }

  const body = { model: 'claude-sonnet-4-20250514', max_tokens: 1000, messages: [{ role: 'user', content: prompt }] };
  if (system) body.system = system;
  if (mcps.length) body.mcp_servers = mcps;

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`AI request failed: ${response.status} ${errorText}`);
  }

  const data = await response.json();
  return (data.content || []).filter((b) => b.type === 'text').map((b) => b.text).join('');
}

const GMAIL = [{ type: 'url', url: 'https://gmailmcp.googleapis.com/mcp/v1', name: 'gmail' }];
const GCAL = [{ type: 'url', url: 'https://calendarmcp.googleapis.com/mcp/v1', name: 'gcal' }];
const GDRIVE = [{ type: 'url', url: 'https://drivemcp.googleapis.com/mcp/v1', name: 'gdrive' }];

function App() {
  const [tab, setTab] = useState('planner');
  const [tasks, setTasks] = useState(INIT_TASKS);
  const [prefs, setPrefs] = useState(DEFAULT_PREFS);
  const [schedule, setSchedule] = useState(null);
  const [schedLoading, setSchedLoading] = useState(false);
  const [aiNote, setAiNote] = useState('');
  const [nextId, setNextId] = useState(10);
  const [form, setForm] = useState({ name: '', deadline: '', duration: 30, priority: 'med' });

  const [gmail, setGmail] = useState({ loading: false, items: null, imported: [] });
  const [gcal, setGcal] = useState({ loading: false, events: null, exportLoading: false, exported: false });
  const [drive, setDrive] = useState({ loading: false, items: null, imported: [] });

  const addTask = () => {
    if (!form.name.trim()) return;
    setTasks((t) => [...t, { id: nextId, ...form, done: false, source: 'manual' }]);
    setNextId((n) => n + 1);
    setForm({ name: '', deadline: '', duration: 30, priority: 'med' });
  };

  const importTask = (task, src) => {
    setTasks((t) => [...t, { ...task, id: nextId, done: false, source: src }]);
    setNextId((n) => n + 1);
  };

  const generatePlan = async () => {
    setSchedLoading(true);
    setSchedule(null);
    setAiNote('');

    const today = new Date().toISOString().split('T')[0];
    const pending = tasks.filter((t) => !t.done);
    const prompt = `You are a personal AI productivity planner. Create an optimized daily schedule for today (${today}).\nTASKS: ${JSON.stringify(pending)}\nPREFS: work ${prefs.workStart}–${prefs.workEnd}, break ${prefs.breakDuration}min, buffer ${prefs.bufferTime}min, peak ${prefs.energyPeak}, style ${prefs.workStyle}\nWrite one friendly sentence, then return JSON:\n\`\`\`json\n[{"time":"09:00","end":"10:30","name":"Task","note":"tip","type":"task"}]\n\`\`\``;

    try {
      const text = await ai(prompt);
      setSchedule(parseJSON(text));
      setAiNote(text.replace(/```json[\s\S]*?```/, '').trim().split('\n')[0]);
    } catch (error) {
      setAiNote('Could not connect to AI.');
      console.warn(error);
    }
    setSchedLoading(false);
  };

  const scanGmail = async () => {
    setGmail((g) => ({ ...g, loading: true, items: null }));
    try {
      const text = await ai(`Use Gmail to get my 10 most recent unread emails. Identify actionable tasks, deadlines, or to-dos. For each, extract: task name (under 60 chars), duration in minutes, priority (low/med/high), deadline (YYYY-MM-DD or empty string), from (sender name), subject.\nReturn ONLY:\n\`\`\`json\n[{"name":"...","duration":30,"priority":"med","deadline":"","from":"sender","subject":"subject"}]\n\`\`\`\nIf no actionable emails, return [].`, GMAIL);
      setGmail((g) => ({ ...g, loading: false, items: parseJSON(text) }));
    } catch (error) {
      setGmail((g) => ({ ...g, loading: false, items: [] }));
      console.warn(error);
    }
  };

  const fetchCalendar = async () => {
    setGcal((g) => ({ ...g, loading: true, events: null }));
    try {
      const text = await ai(`Use Google Calendar to list my upcoming events for the next 3 days. Return ONLY:\n\`\`\`json\n[{"name":"Event","start":"09:00","end":"10:00","date":"YYYY-MM-DD","calendar":"name"}]\n\`\`\`\nLimit to 10. If none, return [].`, GCAL);
      setGcal((g) => ({ ...g, loading: false, events: parseJSON(text) }));
    } catch (error) {
      setGcal((g) => ({ ...g, loading: false, events: [] }));
      console.warn(error);
    }
  };

  const exportToCalendar = async () => {
    if (!schedule) return;
    setGcal((g) => ({ ...g, exportLoading: true }));
    try {
      const today = new Date().toISOString().split('T')[0];
      await ai(`Use Google Calendar to create these events for today (${today}) on my primary calendar. For each, title=name, start=time, end=end: ${JSON.stringify(schedule.filter((b) => b.type === 'task').slice(0, 5))}`, GCAL);
      setGcal((g) => ({ ...g, exportLoading: false, exported: true }));
    } catch (error) {
      setGcal((g) => ({ ...g, exportLoading: false }));
      console.warn(error);
    }
  };

  const scanDrive = async () => {
    setDrive((d) => ({ ...d, loading: true, items: null }));
    try {
      const text = await ai(`Use Google Drive to search for recently modified files (last 7 days) with names suggesting pending work (draft, review, todo, report, proposal, pending). Convert each to a planner task. Return ONLY:\n\`\`\`json\n[{"name":"suggested task name","duration":30,"priority":"med","filename":"actual filename"}]\n\`\`\`\nLimit to 6. If nothing relevant, return [].`, GDRIVE);
      setDrive((d) => ({ ...d, loading: false, items: parseJSON(text) }));
    } catch (error) {
      setDrive((d) => ({ ...d, loading: false, items: [] }));
      console.warn(error);
    }
  };

  const done = tasks.filter((t) => t.done).length;
  const total = tasks.length;
  const totalMins = tasks.filter((t) => !t.done).reduce((a, b) => a + b.duration, 0);

  return (
    <div className="app">
      <div className="header">
        <div className="logo">Plann<span>AI</span></div>
        <div className="tabs">
          {['planner', 'schedule', 'integrations', 'preferences'].map((name) => (
            <button key={name} className={`tab ${tab === name ? 'active' : ''}`} type="button" onClick={() => setTab(name)}>
              {name[0].toUpperCase() + name.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {(tab === 'planner' || tab === 'schedule') && (
        <div className="main">
          <div className="sidebar">
            <div className="panel">
              <div className="panel-title">Add Task</div>
              <div className="form-group">
                <label className="form-label">Task name</label>
                <input className="form-input" placeholder="What needs to get done?" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} onKeyDown={(e) => e.key === 'Enter' && addTask()} />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Deadline</label>
                  <input type="date" className="form-input" value={form.deadline} onChange={(e) => setForm((f) => ({ ...f, deadline: e.target.value }))} />
                </div>
                <div className="form-group">
                  <label className="form-label">Duration</label>
                  <select className="form-input" value={form.duration} onChange={(e) => setForm((f) => ({ ...f, duration: +e.target.value }))}>
                    {[15, 30, 45, 60, 90, 120, 180].map((m) => (
                      <option key={m} value={m}>{m} min</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Priority</label>
                <div className="priority-grid">
                  {['low', 'med', 'high'].map((priority) => (
                    <button key={priority} className={`priority-btn ${priority} ${form.priority === priority ? 'active' : ''}`} type="button" onClick={() => setForm((f) => ({ ...f, priority }))}>
                      {priority === 'low' ? 'Low' : priority === 'med' ? 'Med' : 'High'}
                    </button>
                  ))}
                </div>
              </div>
              <button className="add-btn" type="button" onClick={addTask}>+ Add Task</button>
            </div>

            <div className="panel">
              <div className="panel-title">AI Schedule</div>
              {[['Work window', `${prefs.workStart}–${prefs.workEnd}`], ['Energy peak', prefs.energyPeak], ['Style', prefs.workStyle], ['Pending', `${tasks.filter((t) => !t.done).length} tasks`]].map(([label, value]) => (
                <div key={label} className="pref-row"><span className="pref-label">{label}</span><span className="pref-value">{value}</span></div>
              ))}
              <button className="ai-btn" type="button" style={{ marginTop: '1rem' }} onClick={generatePlan} disabled={schedLoading}>
                {schedLoading ? <><div className="spinner sm"></div>Planning…</> : <><div className="ai-dot"></div>Generate My Plan</>}
              </button>
              {schedule && !schedLoading && (
                <button className={`ai-btn ${gcal.exported ? 'cal-done' : 'cal'}`} type="button" style={{ marginTop: '6px' }} onClick={exportToCalendar} disabled={gcal.exportLoading || gcal.exported}>
                  {gcal.exportLoading ? <><div className="spinner sm"></div>Exporting…</> : gcal.exported ? '✓ Added to Calendar' : '📅 Export to Google Calendar'}
                </button>
              )}
            </div>
          </div>

          <div className="content">
            {tab === 'planner' && (
              <>
                <div className="stats-row">
                  <div className="stat-card"><div className="stat-num">{total}</div><div className="stat-label">Total</div></div>
                  <div className="stat-card"><div className="stat-num">{done}</div><div className="stat-label">Done</div></div>
                  <div className="stat-card"><div className="stat-num">{Math.round(totalMins / 60)}h</div><div className="stat-label">Pending</div></div>
                </div>
                <div className="section-label">All Tasks</div>
                <div className="task-list">
                  {tasks.length === 0 && <div className="task-empty">No tasks yet — add one above or import from integrations</div>}
                  {tasks.map((task) => (
                    <div key={task.id} className={`task-card ${task.priority}`}>
                      <button className={`task-check ${task.done ? 'done' : ''}`} type="button" onClick={() => setTasks((t) => t.map((x) => x.id === task.id ? { ...x, done: !x.done } : x))} />
                      <div className="task-info">
                        <div className={`task-name ${task.done ? 'done' : ''}`}>{task.name}</div>
                        <div className="task-meta">
                          {task.deadline && <span className="task-tag">📅 {task.deadline}</span>}
                          <span className="task-tag">⏱ {task.duration}m</span>
                          <span className={`chip ${task.priority}`}>{task.priority === 'med' ? 'medium' : task.priority}</span>
                          {task.source && task.source !== 'manual' && <span className={`src-badge ${task.source}`}>{task.source}</span>}
                        </div>
                      </div>
                      <button className="task-delete" type="button" onClick={() => setTasks((t) => t.filter((x) => x.id !== task.id))}>×</button>
                    </div>
                  ))}
                </div>
              </>
            )}

            {tab === 'schedule' && (
              <>
                {schedLoading && <div className="ai-thinking"><div className="spinner"></div><div className="ai-thinking-text">Crafting your personalized schedule…</div></div>}
                {!schedLoading && !schedule && !aiNote && <div className="task-empty" style={{ paddingTop: '4rem' }}>Hit "Generate My Plan" to create your AI-optimized schedule</div>}
                {aiNote && !schedLoading && (
                  <div style={{ background: '#171812', border: '1px solid #3a5a3a', borderRadius: 9, padding: '1rem 1.25rem', marginBottom: '1.5rem', borderLeft: '3px solid #6b8c5a' }}>
                    <div style={{ fontSize: 11, color: '#6b8c5a', marginBottom: 4, letterSpacing: '0.08em', textTransform: 'uppercase', fontWeight: 600 }}>AI Planner</div>
                    <div style={{ fontSize: 14, color: '#c8d4b8', fontStyle: 'italic' }}>{aiNote}</div>
                  </div>
                )}
                {schedule && !schedLoading && (
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
              <div className="i-head">
                <div className="i-icon gmail">✉️</div>
                <div><div className="i-name">Gmail</div><div className="i-sub">Google Mail</div></div>
                <span className="badge on">● Connected</span>
              </div>
              <div className="i-desc">Scan your inbox for emails that contain action items, deadlines, or follow-ups — and pull them in as tasks.</div>
              <div className="i-actions">
                <button className={`i-btn${gmail.loading ? ' loading' : ''}`} type="button" onClick={scanGmail} disabled={gmail.loading}>
                  {gmail.loading ? <><div className="spinner sm"></div>Scanning inbox…</> : '✉️ Scan inbox for tasks'}
                </button>
              </div>
              {gmail.loading && <div style={{ padding: '1rem', textAlign: 'center', color: '#6b6b60', fontSize: 12, fontStyle: 'italic' }}>Reading your recent emails…</div>}
              {gmail.items && !gmail.loading && (
                <div className="result-box">
                  {gmail.items.length === 0 ? <div className="empty-box">No actionable emails found in your inbox.</div> : gmail.items.map((item, index) => {
                    const imported = gmail.imported.includes(index);
                    return (
                      <div key={index} className="r-item">
                        <div className="r-info">
                          <div className="r-name">{item.name}</div>
                          <div className="r-sub">{item.from && `${item.from} · `}{item.duration}m · {item.priority}{item.deadline && ` · due ${item.deadline}`}</div>
                        </div>
                        <button className={`r-add${imported ? ' done' : ''}`} type="button" disabled={imported} onClick={() => {
                          importTask({ name: item.name, duration: item.duration || 30, priority: item.priority || 'med', deadline: item.deadline || '' }, 'gmail');
                          setGmail((g) => ({ ...g, imported: [...g.imported, index] }));
                        }}>
                          {imported ? '✓ Added' : '+ Add'}
                        </button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="i-card on">
              <div className="i-head">
                <div className="i-icon gcal">📅</div>
                <div><div className="i-name">Google Calendar</div><div className="i-sub">Events & scheduling</div></div>
                <span className="badge on">● Connected</span>
              </div>
              <div className="i-desc">View upcoming events to plan around existing commitments, and push your AI schedule directly into your calendar.</div>
              <div className="i-actions">
                <button className={`i-btn${gcal.loading ? ' loading' : ''}`} type="button" onClick={fetchCalendar} disabled={gcal.loading}>
                  {gcal.loading ? <><div className="spinner sm"></div>Loading calendar…</> : '📅 View upcoming events'}
                </button>
                <button className="i-btn" type="button" style={{ color: '#c8b87a', borderColor: '#3a3a2a' }} onClick={() => setTab('schedule')}>
                  ↗ Export schedule to calendar
                </button>
              </div>
              {gcal.loading && <div style={{ padding: '1rem', textAlign: 'center', color: '#6b6b60', fontSize: 12, fontStyle: 'italic' }}>Fetching your calendar…</div>}
              {gcal.events && !gcal.loading && (
                <div className="result-box">
                  {gcal.events.length === 0 ? <div className="empty-box">No upcoming events in the next 3 days.</div> : gcal.events.map((event, index) => (
                    <div key={index} className="e-item">
                      <div className="e-name">{event.name}</div>
                      <div className="e-time">{event.date} · {event.start}–{event.end}{event.calendar ? ` · ${event.calendar}` : ''}</div>
                    </div>
                  ))}
                </div>
              )}
              {gcal.exported && <div className="success-bar">✓ Schedule has been exported to Google Calendar</div>}
            </div>

            <div className="i-card on">
              <div className="i-head">
                <div className="i-icon gdrive">📁</div>
                <div><div className="i-name">Google Drive</div><div className="i-sub">Documents & files</div></div>
                <span className="badge on">● Connected</span>
              </div>
              <div className="i-desc">Detect recently modified documents and drafts that need your attention, and turn them into planner tasks.</div>
              <div className="i-actions">
                <button className={`i-btn${drive.loading ? ' loading' : ''}`} type="button" onClick={scanDrive} disabled={drive.loading}>
                  {drive.loading ? <><div className="spinner sm"></div>Scanning Drive…</> : '📁 Scan Drive for pending docs'}
                </button>
              </div>
              {drive.loading && <div style={{ padding: '1rem', textAlign: 'center', color: '#6b6b60', fontSize: 12, fontStyle: 'italic' }}>Searching your Google Drive…</div>}
              {drive.items && !drive.loading && (
                <div className="result-box">
                  {drive.items.length === 0 ? <div className="empty-box">No pending documents found in your Drive.</div> : drive.items.map((item, index) => {
                    const imported = drive.imported.includes(index);
                    return (
                      <div key={index} className="r-item">
                        <div className="r-info">
                          <div className="r-name">{item.name}</div>
                          <div className="r-sub">{item.filename} · {item.duration}m · {item.priority}</div>
                        </div>
                        <button className={`r-add${imported ? ' done' : ''}`} type="button" disabled={imported} onClick={() => {
                          importTask({ name: item.name, duration: item.duration || 30, priority: item.priority || 'med', deadline: '' }, 'drive');
                          setDrive((d) => ({ ...d, imported: [...d.imported, index] }));
                        }}>
                          {imported ? '✓ Added' : '+ Add'}
                        </button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          <div className="integ-section-label">Available to Connect</div>
          <div className="integ-grid">
            {[
              { key: 'outlook', icon: '📬', name: 'Outlook', sub: 'Microsoft Mail & Calendar', desc: 'Sync your Outlook inbox and calendar. Import emails as tasks and export your schedule to Outlook Calendar.' },
              { key: 'notion', icon: '📓', name: 'Notion', sub: 'Workspace & notes', desc: 'Import tasks from Notion databases, pages, and to-do lists. Keep Notion and your planner in sync.' },
              { key: 'slack', icon: '💬', name: 'Slack', sub: 'Team messaging', desc: 'Turn flagged Slack messages and reminders into planner tasks automatically.' },
              { key: 'todoist', icon: '✅', name: 'Todoist', sub: 'Task management', desc: 'Two-way sync with Todoist. Import existing tasks and export your AI schedule back to Todoist projects.' },
            ].map((service) => (
              <div key={service.key} className="i-card">
                <div className="i-head">
                  <div className={`i-icon ${service.key}`}>{service.icon}</div>
                  <div><div className="i-name">{service.name}</div><div className="i-sub">{service.sub}</div></div>
                  <span className="badge soon">Coming soon</span>
                </div>
                <div className="i-desc" style={{ opacity: 0.45 }}>{service.desc}</div>
                <button className="i-connect" type="button" disabled>Connect {service.name}</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === 'preferences' && (
        <div className="page-prefs">
          <div className="pref-section">
            <div className="pref-section-title">Work Hours</div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Start time</label>
                <input type="time" className="form-input" value={prefs.workStart} onChange={(e) => setPrefs((p) => ({ ...p, workStart: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">End time</label>
                <input type="time" className="form-input" value={prefs.workEnd} onChange={(e) => setPrefs((p) => ({ ...p, workEnd: e.target.value }))} />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Break duration (minutes)</label>
              <select className="form-input" value={prefs.breakDuration} onChange={(e) => setPrefs((p) => ({ ...p, breakDuration: +e.target.value }))}>
                {[5, 10, 15, 20, 30].map((value) => (
                  <option key={value} value={value}>{value} min</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Buffer between tasks</label>
              <select className="form-input" value={prefs.bufferTime} onChange={(e) => setPrefs((p) => ({ ...p, bufferTime: +e.target.value }))}>
                {[0, 5, 10, 15, 20].map((value) => (
                  <option key={value} value={value}>{value} min</option>
                ))}
              </select>
            </div>
          </div>

          <div className="pref-section">
            <div className="pref-section-title">Personal Rhythm</div>
            <div className="form-group">
              <label className="form-label">Energy peak</label>
              <select className="form-input" value={prefs.energyPeak} onChange={(e) => setPrefs((p) => ({ ...p, energyPeak: e.target.value }))}>
                <option value="morning">Morning (9–12)</option>
                <option value="midday">Midday (12–15)</option>
                <option value="afternoon">Afternoon (15–18)</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Work style</label>
              <select className="form-input" value={prefs.workStyle} onChange={(e) => setPrefs((p) => ({ ...p, workStyle: e.target.value }))}>
                <option value="balanced">Balanced</option>
                <option value="deep-work">Deep work — long focus blocks</option>
                <option value="sprints">Sprints — short intense bursts</option>
                <option value="flexible">Flexible</option>
              </select>
            </div>
            <div className="form-group" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <label className="form-label" style={{ marginBottom: 0 }}>Enable focus blocks (Pomodoro-style)</label>
              <label className="toggle">
                <input type="checkbox" checked={prefs.focusBlocks} onChange={(e) => setPrefs((p) => ({ ...p, focusBlocks: e.target.checked }))} />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div className="pref-section">
            <div className="pref-section-title">Location & Time</div>
            <div className="form-group">
              <label className="form-label">Timezone</label>
              <select className="form-input" value={prefs.timezone} onChange={(e) => setPrefs((p) => ({ ...p, timezone: e.target.value }))}>
                {['Europe/Amsterdam', 'Europe/London', 'America/New_York', 'America/Los_Angeles', 'Asia/Tokyo', 'Asia/Dubai'].map((tz) => (
                  <option key={tz} value={tz}>{tz}</option>
                ))}
              </select>
            </div>
          </div>

          <button className="add-btn" type="button" style={{ maxWidth: 200 }} onClick={() => setTab('planner')}>Save Preferences</button>
        </div>
      )}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
