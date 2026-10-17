import { describe, expect, it } from 'vitest'
import { mockStrategies, runMockStrategy, traces } from './data'
import { parseTraceImport } from './validation'

describe('deterministic trace fixtures', () => {
  it('keeps event sequences contiguous', () => {
    for (const trace of traces) expect(trace.events.map((event) => event.sequence)).toEqual(trace.events.map((_, index) => index))
  })

  it('returns stable recovery results for the timeout scenario', () => {
    const first = runMockStrategy(mockStrategies[0].id, traces[0])
    const second = runMockStrategy(mockStrategies[0].id, traces[0])
    expect(first).toEqual(second)
    expect(first.status).toBe('recovered')
  })

  it('rejects an event that points to an unknown span', () => {
    const invalid = { ...traces[0], events: traces[0].events.map((event, index) => index === 1 ? { ...event, spanId: 'missing' } : event) }
    expect(parseTraceImport(invalid)).toEqual({ success: false, error: 'Invalid trace: event references unknown span' })
  })
})
