import { describe, expect, it } from 'vitest';

import { formatTime } from '../src/format';
import { makeHass } from './helpers';

const NOW = new Date('2026-07-12T11:00:00Z');

describe('formatTime', () => {
  it('returns an empty string for missing or invalid input', () => {
    expect(formatTime(null, makeHass())).toBe('');
    expect(formatTime('not a date', makeHass())).toBe('');
  });

  it('shows only the clock for today and the date for other days', () => {
    const hass = makeHass([], {
      locale: { language: 'en', time_zone: 'server', time_format: '24' },
      config: { time_zone: 'UTC' },
    });
    expect(formatTime('2026-07-12T15:30:00Z', hass, NOW)).toBe('15:30');
    expect(formatTime('2026-07-13T15:30:00Z', hass, NOW)).toMatch(/13 Jul|Jul 13/);
  });

  it("uses Home Assistant's server time zone when configured", () => {
    const hass = makeHass([], {
      locale: { language: 'en', time_zone: 'server', time_format: '24' },
      config: { time_zone: 'Pacific/Auckland' }, // UTC+12 in July
    });
    expect(formatTime('2026-07-12T10:00:00Z', hass, NOW)).toBe('22:00');
  });

  it('honours the 12-hour preference', () => {
    const hass = makeHass([], {
      locale: { language: 'en', time_zone: 'server', time_format: '12' },
      config: { time_zone: 'UTC' },
    });
    expect(formatTime('2026-07-12T15:30:00Z', hass, NOW)).toMatch(/^0?3:30\s?PM$/i);
  });

});
