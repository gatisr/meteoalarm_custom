import { beforeAll, describe, expect, it, vi } from 'vitest';

import type { MeteoAlarmCard } from '../src/meteoalarm-card';
import type { HomeAssistant, MeteoAlarmCardConfig } from '../src/types';
import { makeAlert, makeEntity, makeHass } from './helpers';

const ENTITY = 'sensor.meteoalarm_riga_warning_level';

let CardClass: typeof MeteoAlarmCard;

beforeAll(async () => {
  vi.spyOn(console, 'info').mockImplementation(() => undefined);
  ({ MeteoAlarmCard: CardClass } = await import('../src/meteoalarm-card'));
});

async function mount(
  config: Partial<MeteoAlarmCardConfig>,
  hass: HomeAssistant
): Promise<MeteoAlarmCard> {
  const card = document.createElement('meteoalarm-card') as MeteoAlarmCard;
  card.setConfig({ type: 'custom:meteoalarm-card', ...config });
  card.hass = hass;
  document.body.appendChild(card);
  await card.updateComplete;
  return card;
}

const text = (card: MeteoAlarmCard) => card.shadowRoot?.textContent?.replace(/\s+/g, ' ') ?? '';

describe('meteoalarm-card rendering', () => {
  it('asks for an entity when none is configured', async () => {
    const card = await mount({}, makeHass());
    expect(text(card)).toContain('Please set an entity');
  });

  it('reports a missing entity', async () => {
    const card = await mount({ entity: ENTITY }, makeHass());
    expect(text(card)).toContain(`Entity not found: ${ENTITY}`);
  });

  it('shows the calm state without alerts', async () => {
    const hass = makeHass([makeEntity(ENTITY, 'none', { alerts: [], area: 'Riga' })]);
    const card = await mount({ entity: ENTITY }, hass);

    expect(text(card)).toContain('No active warnings');
    expect(text(card)).toContain('Riga');
  });

  it('does not claim "no warnings" for a sensor without alerts data', async () => {
    // Non-alert sensors (count, onset, ...) have no `alerts` attribute.
    const hass = makeHass([makeEntity('sensor.other', '3', {})]);
    const card = await mount({ entity: 'sensor.other' }, hass);

    expect(text(card)).toContain('Select the warning level sensor');
    expect(text(card)).not.toContain('No active warnings');
  });

  it('shows an unavailable notice instead of an all-clear', async () => {
    for (const state of ['unavailable', 'unknown']) {
      const hass = makeHass([makeEntity(ENTITY, state, {})]);
      const card = await mount({ entity: ENTITY }, hass);

      expect(text(card)).toContain('Warnings are currently unavailable');
      expect(text(card)).not.toContain('No active warnings');
    }
  });

  it('renders every alert with description and optional instruction', async () => {
    const hass = makeHass([
      makeEntity(ENTITY, 'extreme', {
        area: 'Riga',
        alerts: [
          makeAlert({ event: 'Red Rain Warning', severity: 'extreme' }),
          makeAlert({ identifier: 'b', event: 'Yellow Fog Warning' }),
        ],
      }),
    ]);
    const card = await mount({ entity: ENTITY, show_instruction: true }, hass);

    expect(card.shadowRoot?.querySelectorAll('.alert')).toHaveLength(2);
    expect(text(card)).toContain('Red Rain Warning');
    expect(text(card)).toContain('Fog in places.');
    expect(text(card)).toContain('Drive carefully.');
  });

  it('collapses long texts behind a details toggle', async () => {
    const long = 'x'.repeat(250);
    const hass = makeHass([
      makeEntity(ENTITY, 'moderate', { alerts: [makeAlert({ description: long })] }),
    ]);
    const card = await mount({ entity: ENTITY }, hass);

    expect(card.shadowRoot?.querySelector('details summary')?.textContent).toContain(
      'Show details'
    );
  });

  it('keeps short texts inline', async () => {
    const hass = makeHass([makeEntity(ENTITY, 'moderate', { alerts: [makeAlert()] })]);
    const card = await mount({ entity: ENTITY }, hass);
    expect(card.shadowRoot?.querySelector('details')).toBeNull();
  });

  it('hides texts in compact mode', async () => {
    const hass = makeHass([makeEntity(ENTITY, 'moderate', { alerts: [makeAlert()] })]);
    const card = await mount({ entity: ENTITY, compact: true }, hass);

    expect(text(card)).toContain('Yellow Fog Warning');
    expect(text(card)).not.toContain('Fog in places.');
  });

  it('uses the configured title', async () => {
    const hass = makeHass([makeEntity(ENTITY, 'none', { alerts: [], area: 'Riga' })]);
    const card = await mount({ entity: ENTITY, title: 'Home weather' }, hass);
    expect(text(card)).toContain('Home weather');
  });

  it('falls back to the "none" style for unknown or prototype state names', async () => {
    const hass = makeHass([makeEntity(ENTITY, 'toString', { alerts: [] })]);
    const card = await mount({ entity: ENTITY }, hass);
    expect(card.shadowRoot?.querySelector('.badge')?.getAttribute('style')).toContain(
      '--success-color'
    );
  });
});

describe('meteoalarm-card badge', () => {
  it('marks the badge with the severity so the yellow one gets dark text', async () => {
    const hass = makeHass([makeEntity(ENTITY, 'moderate', { alerts: [] })]);
    const card = await mount({ entity: ENTITY }, hass);
    expect(card.shadowRoot?.querySelector('.badge')?.classList.contains('moderate')).toBe(true);
  });
});

describe('meteoalarm-card static API', () => {
  it('suggests only the warning level (enum) sensor', () => {
    const hass = makeHass([
      makeEntity('sensor.meteoalarm_riga_active_alerts', '2', { alerts: [makeAlert()] }),
      makeEntity('sensor.unrelated', 'x', {}),
      makeEntity(ENTITY, 'moderate', { device_class: 'enum', alerts: [makeAlert()] }),
    ]);
    expect(CardClass.getStubConfig(hass)).toEqual({ entity: ENTITY });
  });



  it('registers itself in the card picker exactly once, even if loaded twice', async () => {
    vi.resetModules();
    // A second load defines the element again, which the browser would reject
    // for the custom element only; the picker entry must not be duplicated.
    const original = customElements.define.bind(customElements);
    vi.spyOn(customElements, 'define').mockImplementation((name, ctor, options) => {
      if (!customElements.get(name)) original(name, ctor, options);
    });
    await import('../src/meteoalarm-card');

    const entries = (window.customCards ?? []).filter((c) => c.type === 'meteoalarm-card');
    expect(entries).toHaveLength(1);
  });
});
