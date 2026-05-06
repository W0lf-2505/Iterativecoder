import { useState, useRef, useEffect, useCallback } from 'react'
import { runRunPost } from './lib/api'
import './App.css'

type EntryType = 'goal' | 'id' | 'conn' | 'disc' | 'plan' | 'step' | 'result' | 'status' | 'info' | 'new plan'

interface PlanStep { step: number; description: string }
interface ResultObj { status: string; tool?: string; error?: { message?: string } | string; output?: { stdout?: string; stderr?: string } }
interface SummaryItem { title: string; summary: string; source: string }

type Entry =
  | { type: 'goal' | 'id' | 'conn' | 'disc' | 'step' | 'info'; text: string }
  | { type: 'plan'; steps: PlanStep[] }
  | { type: 'new plan'; steps: PlanStep[] }
  | { type: 'result'; ok: boolean; obj: ResultObj }
  | { type: 'status'; ok: boolean; text: string }
  | { type: 'summary'; items: SummaryItem[] } 

function parseMessage(raw: string): Entry[] {
  const text = raw.trim()
  if (text.startsWith('PLAN:')) {
    try {
      const obj = JSON.parse(text.slice(5).trim())
      const steps: PlanStep[] = obj.plan ?? obj
      if (Array.isArray(steps)) return [{ type: 'plan', steps }]
    } catch {}
    return [{ type: 'info', text }]
  }
  if (text.startsWith('Summary:')) {
    try {
      const items: SummaryItem[] = JSON.parse(text.slice(8).trim())
      if (Array.isArray(items)) return [{ type: 'summary', items }]
    } catch {}
    return [{ type: 'info', text }]
  }
  if (text.startsWith('NEW PLAN:')) {
    try {
      const obj = JSON.parse(text.slice(9).trim())
      const steps: PlanStep[] = obj.plan ?? obj
      if (Array.isArray(steps)) return [{ type: 'new plan', steps }]
    } catch {}
    return [{ type: 'info', text }]
  }
  if (text.startsWith('STEP:')) return [{ type: 'step', text: text.slice(5).trim() }]
  if (text.startsWith('RESULT:')) {
    try {
      const obj: ResultObj = JSON.parse(text.slice(7).trim())
      return [{ type: 'result', ok: obj.status === 'success', obj }]
    } catch {}
    return [{ type: 'info', text }]
  }
  if (text.startsWith('STATUS:')) {
    const s = text.slice(7).trim()
    const ok = ['success', 'done', 'complete'].includes(s)
    return [{ type: 'status', ok, text: s }]
  }
  return [{ type: 'info', text }]
}

const TAG: Record<string, { label: string; style: React.CSSProperties }> = {
  goal:   { label: 'goal',   style: { background: '#1e293b', color: '#64748b' } },
  id:     { label: 'id',     style: { background: '#1e293b', color: '#94a3b8' } },
  conn:   { label: 'ws',     style: { background: '#14291f', color: '#22c55e' } },
  disc:   { label: 'ws',     style: { background: '#2d1111', color: '#ef4444' } },
  step:   { label: 'step',   style: { background: '#0c2033', color: '#38bdf8' } },
  info:   { label: 'info',   style: { background: '#1a1a1a', color: '#555' } },
}

function Row({ tag, tagStyle, text, textColor }: { tag: string; tagStyle: React.CSSProperties; text: string; textColor: string }) {
  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', fontSize: 11.5, lineHeight: 1.65, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
      <span style={{ fontSize: 9, padding: '1px 5px', borderRadius: 3, fontWeight: 500, letterSpacing: '.05em', flexShrink: 0, alignSelf: 'flex-start', marginTop: 2, ...tagStyle }}>{tag}</span>
      <span style={{ color: textColor }}>{text}</span>
    </div>
  )
}

function PlanCard({ steps }: { steps: PlanStep[] }) {
  return (
    <div style={{ border: '0.5px solid #1e1b4b', borderRadius: 6, padding: '8px 10px', background: '#0f0e1a', display: 'flex', flexDirection: 'column', gap: 3 }}>
      <div style={{ fontSize: 10, color: '#6366f1', letterSpacing: '.08em', marginBottom: 4 }}>plan</div>
      {steps.map(s => (
        <div key={s.step} style={{ display: 'flex', gap: 8, alignItems: 'baseline' }}>
          <span style={{ fontSize: 10, color: '#4338ca', minWidth: 16 }}>{s.step}.</span>
          <span style={{ fontSize: 11.5, color: '#a5b4fc' }}>{s.description}</span>
        </div>
      ))}
    </div>
  )
}

function SummaryCard({ items }: { items: SummaryItem[] }) {
  return (
    <div style={{ border: '0.5px solid #1a2e1a', borderRadius: 6, padding: '8px 10px', background: '#0a160a', display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ fontSize: 10, color: '#4ade80', letterSpacing: '.08em' }}>summary</div>
      {items.map((item, i) => (
        <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 2, paddingLeft: 2 }}>
          <span style={{ fontSize: 11.5, color: '#86efac', fontWeight: 500 }}>{item.title}</span>
          <span style={{ fontSize: 11, color: '#94a3b8', lineHeight: 1.6 }}>{item.summary}</span>
          {item.source && <span style={{ fontSize: 10, color: '#374151' }}>source: {item.source}</span>}
        </div>
      ))}
    </div>
  )
}

function ResultCard({ ok, obj }: { ok: boolean; obj: ResultObj }) {
  const errMsg = obj.error ? (typeof obj.error === 'string' ? obj.error : obj.error.message) : null
  return (
    <div style={{ borderRadius: 6, padding: '8px 10px', display: 'flex', flexDirection: 'column', gap: 3, background: ok ? '#0a1f12' : '#1c0a0a', border: `0.5px solid ${ok ? '#14532d' : '#450a0a'}` }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 11, color: ok ? '#4ade80' : '#f87171' }}>{ok ? '✓' : '✗'}</span>
        <span style={{ fontSize: 9, padding: '1px 6px', borderRadius: 3, fontWeight: 500, background: ok ? '#14532d' : '#450a0a', color: ok ? '#4ade80' : '#f87171' }}>{obj.tool ?? '?'}</span>
        <span style={{ fontSize: 11, color: ok ? '#4ade80' : '#f87171' }}>{obj.status}</span>
      </div>
      {errMsg && <div style={{ fontSize: 11, color: '#fca5a5', paddingLeft: 2 }}>{errMsg}</div>}
      {obj.output?.stdout && <div style={{ fontSize: 11, color: '#94a3b8', paddingLeft: 2 }}>stdout: {obj.output.stdout}</div>}
      {obj.output?.stderr && <div style={{ fontSize: 11, color: '#fca5a5', paddingLeft: 2 }}>stderr: {obj.output.stderr}</div>}
    </div>
  )
}

function EntryView({ entry }: { entry: Entry }) {
  if (entry.type === 'plan') return <PlanCard steps={entry.steps} />
  if (entry.type === 'new plan') return <PlanCard steps={entry.steps} />
  if (entry.type === 'result') return <ResultCard ok={entry.ok} obj={entry.obj} />
  if (entry.type === 'status') {
    return <Row tag="status" tagStyle={entry.ok ? { background: '#14291f', color: '#4ade80' } : { background: '#2d1111', color: '#f87171' }} text={entry.text} textColor={entry.ok ? '#86efac' : '#fca5a5'} />
  }
  if (entry.type === 'summary') return <SummaryCard items={entry.items} />
  const t = TAG[entry.type] ?? TAG.info
  const textColors: Record<string, string> = { goal: '#64748b', id: '#94a3b8', conn: '#86efac', disc: '#fca5a5', step: '#7dd3fc', info: '#94a3b8' }
  return <Row tag={t.label} tagStyle={t.style} text={entry.text} textColor={textColors[entry.type] ?? '#cbd5e1'} />
}

export default function App() {
  const [goal, setGoal] = useState('')
  const [entries, setEntries] = useState<Entry[]>([])
  const [connected, setConnected] = useState(false)
  const [running, setRunning] = useState(false)
  const [taskId, setTaskId] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const termRef = useRef<HTMLDivElement>(null)

  useEffect(() => { termRef.current?.scrollTo(0, termRef.current.scrollHeight) }, [entries])

  function push(...e: Entry[]) { setEntries(prev => [...prev, ...e]) }

  function connectWS(id: string) {
    wsRef.current?.close()
    const base = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'
    const ws = new WebSocket(`${base}/ws/${id}`)
    wsRef.current = ws
    ws.onopen = () => { setConnected(true); push({ type: 'conn', text: 'websocket connected' }) }
    ws.onmessage = (e) => push(...parseMessage(e.data))
    ws.onclose = (e) => {
      setConnected(false); setRunning(false)
      push({ type: 'disc', text: `disconnected (code: ${e.code}${e.reason ? `, reason: "${e.reason}"` : ''})` })
    }
    ws.onerror = () => push({ type: 'disc', text: 'websocket error' })
  }

  async function runAgent() {
  if (!goal.trim()) return
  setRunning(true); setEntries([]); setTaskId(null)
  push({ type: 'goal', text: goal })

  // get or create session id
  let sessionId = localStorage.getItem('session_id')
  if (!sessionId) {
    sessionId = crypto.randomUUID()
    localStorage.setItem('session_id', sessionId)
  }

  try {
    const { data, error } = await runRunPost({ query: { goal, session_id: sessionId } })
    if (error) throw new Error(JSON.stringify(error))
    const id = (data as any)?.task_id ?? (data as any)?.id
    if (!id) throw new Error('no task_id in response')
    setTaskId(id)
    push({ type: 'id', text: id })
    connectWS(id)
  } catch (err: any) {
    push({ type: 'disc', text: 'error: ' + err.message })
    setRunning(false)
  }
}

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', fontFamily: 'var(--font-mono, monospace)', background: '#0d0d0d' }}>

      {/* Goal bar */}
      <div style={{ padding: '12px 16px', borderBottom: '0.5px solid #1e1e1e', display: 'flex', flexDirection: 'column', gap: 8, background: '#111' }}>
        <div style={{ fontSize: 10, letterSpacing: '.1em', color: '#444', textTransform: 'uppercase' }}>agent goal</div>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            value={goal}
            onChange={e => setGoal(e.target.value)}
            onKeyDown={e => (e.metaKey || e.ctrlKey) && e.key === 'Enter' && runAgent()}
            placeholder="e.g. Create a hello world Python project with README"
            style={{ flex: 1, fontFamily: 'inherit', fontSize: 13, padding: '7px 10px', border: '0.5px solid #2a2a2a', borderRadius: 6, background: '#0d0d0d', color: '#cbd5e1' }}
          />
          <button
            onClick={runAgent}
            disabled={running || !goal.trim()}
            style={{ padding: '0 14px', height: 34, fontFamily: 'inherit', fontSize: 12, fontWeight: 500, border: '0.5px solid #2a2a2a', borderRadius: 6, background: '#111', color: '#94a3b8', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, opacity: (running || !goal.trim()) ? .4 : 1 }}
          >
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: connected ? '#22c55e' : '#ef4444', flexShrink: 0 }} />
            {running ? 'running…' : 'run'}
          </button>
        </div>
      </div>

      {/* Status bar */}
      <div style={{ padding: '4px 14px', background: '#0a0a0a', display: 'flex', alignItems: 'center', gap: 8, borderBottom: '0.5px solid #181818' }}>
        <span style={{ width: 6, height: 6, borderRadius: '50%', background: connected ? '#22c55e' : '#333', flexShrink: 0, transition: 'background .3s' }} />
        <span style={{ fontSize: 10, color: '#444' }}>{connected ? 'connected' : 'disconnected'}</span>
        {taskId && <span style={{ fontSize: 10, color: '#333', marginLeft: 'auto', background: '#141414', padding: '2px 8px', borderRadius: 20, border: '0.5px solid #222' }}>task {taskId.slice(0, 8)}…</span>}
      </div>

      {/* Terminal */}
      <div ref={termRef} style={{ flex: 1, background: '#0d0d0d', overflowY: 'auto', padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 5 }}>
        {entries.length === 0 && <span style={{ fontSize: 11, color: '#2a2a2a' }}>$ ready — enter a goal above</span>}
        {entries.map((e, i) => <EntryView key={i} entry={e} />)}
      </div>

    </div>
  )
}