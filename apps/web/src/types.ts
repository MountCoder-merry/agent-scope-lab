export type TraceStatus = 'failed' | 'completed' | 'running'
export type SpanStatus = 'ok' | 'error' | 'pending'
export type TraceSourceFramework = 'synthetic' | 'langgraph' | 'agentscope' | 'unknown'

export interface TraceEvent {
  eventId: string
  sequence: number
  spanId: string
  type: 'span.started' | 'tool.called' | 'tool.failed' | 'span.completed' | 'agent.thought'
  label: string
  atMs: number
  payload: string
}

export interface TraceSpan {
  spanId: string
  parentSpanId?: string
  name: string
  kind: 'agent' | 'tool' | 'parser'
  status: SpanStatus
  durationMs: number
  error?: string
  detail: string
}

export interface TraceRecord {
  schemaVersion: string
  sourceFramework: TraceSourceFramework
  traceId: string
  scenario: 'evidence-conflict' | 'tool-timeout' | 'invalid-json'
  title: string
  summary: string
  status: TraceStatus
  startedAt: string
  durationMs: number
  spans: TraceSpan[]
  events: TraceEvent[]
}

export interface TraceDataSource {
  listTraces(): Promise<TraceRecord[]> | TraceRecord[]
  getTrace(traceId: string): Promise<TraceRecord | undefined> | TraceRecord | undefined
}

export interface MockResult {
  strategyId: string
  strategyName: string
  status: 'recovered' | 'failed'
  retries: number
  virtualDurationMs: number
  assertion: string
  delta: string
}
