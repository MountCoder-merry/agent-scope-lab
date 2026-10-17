import { z } from 'zod'
import type { TraceRecord } from './types'

const eventSchema = z.object({
  eventId: z.string().min(1).max(128), sequence: z.number().int().nonnegative(), spanId: z.string().min(1).max(128),
  type: z.enum(['span.started', 'tool.called', 'tool.failed', 'span.completed', 'agent.thought']),
  label: z.string().min(1).max(256), atMs: z.number().int().nonnegative().max(86_400_000), payload: z.string().max(16_384)
}).strict()

const spanSchema = z.object({
  spanId: z.string().min(1).max(128), parentSpanId: z.string().min(1).max(128).optional(), name: z.string().min(1).max(256),
  kind: z.enum(['agent', 'tool', 'parser']), status: z.enum(['ok', 'error', 'pending']), durationMs: z.number().int().nonnegative().max(86_400_000),
  error: z.string().max(128).optional(), detail: z.string().max(16_384)
}).strict()

const traceSchema = z.object({
  schemaVersion: z.string().min(1).max(32).default('1.0'),
  sourceFramework: z.enum(['synthetic', 'langgraph', 'agentscope', 'unknown']).default('unknown'),
  traceId: z.string().min(1).max(128), scenario: z.enum(['evidence-conflict', 'tool-timeout', 'invalid-json']), title: z.string().min(1).max(256),
  summary: z.string().max(2000), status: z.enum(['failed', 'completed', 'running']), startedAt: z.string().max(64), durationMs: z.number().int().nonnegative().max(86_400_000),
  spans: z.array(spanSchema).min(1).max(500), events: z.array(eventSchema).min(1).max(5000)
}).strict()

function hasCycle(spans: TraceRecord['spans']): boolean {
  const parents = new Map(spans.map((span) => [span.spanId, span.parentSpanId]))
  for (const span of spans) {
    const seen = new Set<string>()
    let current: string | undefined = span.spanId
    while (current) {
      if (seen.has(current)) return true
      seen.add(current)
      current = parents.get(current)
    }
  }
  return false
}

function exceedsDepth(value: unknown, maxDepth: number, depth = 0): boolean {
  if (depth > maxDepth || value === null || typeof value !== 'object') return depth > maxDepth
  return Object.values(value as Record<string, unknown>).some((child) => exceedsDepth(child, maxDepth, depth + 1))
}

export function parseTraceImport(input: unknown): { success: true; data: TraceRecord } | { success: false; error: string } {
  if (exceedsDepth(input, 12)) return { success: false, error: 'Invalid trace: maximum nesting depth is 12' }
  const parsed = traceSchema.safeParse(input)
  if (!parsed.success) return { success: false, error: `Invalid trace: ${parsed.error.issues[0]?.path.join('.') || 'root'}` }
  const trace = parsed.data
  const spanIds = new Set(trace.spans.map((span) => span.spanId))
  if (spanIds.size !== trace.spans.length) return { success: false, error: 'Invalid trace: duplicate spanId' }
  if (trace.spans.some((span) => span.parentSpanId && !spanIds.has(span.parentSpanId))) return { success: false, error: 'Invalid trace: missing parent span' }
  if (hasCycle(trace.spans)) return { success: false, error: 'Invalid trace: cyclic span relation' }
  const eventIds = new Set(trace.events.map((event) => event.eventId))
  if (eventIds.size !== trace.events.length) return { success: false, error: 'Invalid trace: duplicate eventId' }
  if (trace.events.some((event, index) => event.sequence !== index)) return { success: false, error: 'Invalid trace: event sequence must be contiguous' }
  if (trace.events.some((event) => !spanIds.has(event.spanId))) return { success: false, error: 'Invalid trace: event references unknown span' }
  return { success: true, data: trace }
}
