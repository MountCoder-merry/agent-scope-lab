import type { MockResult, TraceDataSource, TraceRecord } from './types'

const span = (spanId: string, name: string, kind: TraceRecord['spans'][number]['kind'], status: TraceRecord['spans'][number]['status'], durationMs: number, detail: string, error?: string, parentSpanId?: string) => ({ spanId, name, kind, status, durationMs, detail, ...(parentSpanId ? { parentSpanId } : {}), ...(error ? { error } : {}) })

export const traces: TraceRecord[] = [
  {
    schemaVersion: '1.0', sourceFramework: 'synthetic', traceId: 'tr_7f21_timeout', scenario: 'tool-timeout', title: 'Tool timeout / weather lookup',
    summary: 'The planner waits on a weather tool until the recorded timeout boundary.', status: 'failed', startedAt: '10:42:18.120', durationMs: 4800,
    spans: [
      span('sp_root', 'Travel planner', 'agent', 'error', 4800, 'Plans a two-day itinerary from user constraints.'),
      span('sp_weather', 'weather.lookup', 'tool', 'error', 4500, 'Recorded tool call exceeded its 4.5s budget.', 'TOOL_TIMEOUT', 'sp_root'),
      span('sp_answer', 'compose.answer', 'agent', 'pending', 0, 'Skipped because the required weather evidence is missing.', undefined, 'sp_root')
    ],
    events: [
      { eventId: 'ev_001', sequence: 0, spanId: 'sp_root', type: 'span.started', label: 'Planner started', atMs: 0, payload: 'constraints: {city: Hangzhou, days: 2}' },
      { eventId: 'ev_002', sequence: 1, spanId: 'sp_weather', type: 'tool.called', label: 'Weather tool called', atMs: 240, payload: 'location=Hangzhou; timeout_ms=4500' },
      { eventId: 'ev_003', sequence: 2, spanId: 'sp_weather', type: 'tool.failed', label: 'Tool timeout', atMs: 4740, payload: 'error_code=TOOL_TIMEOUT' },
      { eventId: 'ev_004', sequence: 3, spanId: 'sp_root', type: 'span.completed', label: 'Trace failed', atMs: 4800, payload: 'status=failed' }
    ]
  },
  {
    schemaVersion: '1.0', sourceFramework: 'synthetic', traceId: 'tr_91ab_conflict', scenario: 'evidence-conflict', title: 'Evidence conflict / citation check',
    summary: 'Two sources disagree on a launch date and the verifier requests a human review.', status: 'completed', startedAt: '09:18:05.004', durationMs: 1630,
    spans: [
      span('sp_root', 'Research agent', 'agent', 'ok', 1630, 'Compares source excerpts before drafting an answer.'),
      span('sp_source_a', 'source.fetch.primary', 'tool', 'ok', 390, 'Primary source returned a dated announcement.', undefined, 'sp_root'),
      span('sp_source_b', 'source.fetch.secondary', 'tool', 'ok', 420, 'Secondary source returned a conflicting date.', undefined, 'sp_root'),
      span('sp_verify', 'evidence.verify', 'parser', 'ok', 580, 'Marks the claim as conflicting and requests review.', undefined, 'sp_root')
    ],
    events: [
      { eventId: 'ev_101', sequence: 0, spanId: 'sp_root', type: 'span.started', label: 'Research started', atMs: 0, payload: 'question=launch date' },
      { eventId: 'ev_102', sequence: 1, spanId: 'sp_source_a', type: 'tool.called', label: 'Primary source fetched', atMs: 120, payload: 'confidence=0.91' },
      { eventId: 'ev_103', sequence: 2, spanId: 'sp_source_b', type: 'tool.called', label: 'Secondary source fetched', atMs: 510, payload: 'confidence=0.68' },
      { eventId: 'ev_104', sequence: 3, spanId: 'sp_verify', type: 'agent.thought', label: 'Conflict detected', atMs: 930, payload: 'dates differ by 3 days' },
      { eventId: 'ev_105', sequence: 4, spanId: 'sp_root', type: 'span.completed', label: 'Review requested', atMs: 1630, payload: 'status=completed_with_review' }
    ]
  },
  {
    schemaVersion: '1.0', sourceFramework: 'synthetic', traceId: 'tr_3cc2_json', scenario: 'invalid-json', title: 'Invalid JSON / structured output',
    summary: 'The parser receives a trailing comma and returns a schema error before tool use.', status: 'failed', startedAt: '08:04:41.772', durationMs: 220,
    spans: [
      span('sp_root', 'Invoice extractor', 'agent', 'error', 220, 'Extracts line items into a typed object.'),
      span('sp_parser', 'output.parse', 'parser', 'error', 14, 'Trailing comma makes the recorded JSON invalid.', 'INVALID_JSON', 'sp_root'),
      span('sp_retry', 'output.repair', 'agent', 'pending', 0, 'No repair policy was enabled in the baseline.', undefined, 'sp_root')
    ],
    events: [
      { eventId: 'ev_201', sequence: 0, spanId: 'sp_root', type: 'span.started', label: 'Extraction started', atMs: 0, payload: 'document=invoice_042' },
      { eventId: 'ev_202', sequence: 1, spanId: 'sp_parser', type: 'tool.called', label: 'Parser called', atMs: 206, payload: 'content_type=application/json' },
      { eventId: 'ev_203', sequence: 2, spanId: 'sp_parser', type: 'tool.failed', label: 'Invalid JSON', atMs: 220, payload: 'line=1; column=87' }
    ]
  }
]

export const mockStrategies = [
  { id: 'bounded-retry', name: 'Bounded retry', description: 'Retry once with a shorter timeout budget.' },
  { id: 'fallback-cache', name: 'Use recorded fallback', description: 'Use the last known weather snapshot and annotate uncertainty.' }
]

export const fixtureDataSource: TraceDataSource = {
  listTraces: () => traces,
  getTrace: (traceId) => traces.find((trace) => trace.traceId === traceId),
}

export function runMockStrategy(strategyId: string, trace: TraceRecord): MockResult {
  if (trace.scenario !== 'tool-timeout') return { strategyId, strategyName: 'Not applicable', status: 'failed', retries: 0, virtualDurationMs: trace.durationMs, assertion: 'Scenario is not tool-timeout', delta: 'No simulation available' }
  if (strategyId === 'fallback-cache') return { strategyId, strategyName: 'Use recorded fallback', status: 'recovered', retries: 0, virtualDurationMs: 1320, assertion: 'weather evidence is annotated as stale', delta: '-3,480ms · adds uncertainty flag' }
  return { strategyId, strategyName: 'Bounded retry', status: 'recovered', retries: 1, virtualDurationMs: 2980, assertion: 'second call returns within 2s budget', delta: '-1,820ms · +1 retry' }
}
