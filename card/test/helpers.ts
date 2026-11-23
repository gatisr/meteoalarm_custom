import type { AlertData, HassEntity, HomeAssistant } from '../src/types';

export function makeAlert(overrides: Partial<AlertData> = {}): AlertData {
  return {
    identifier: 'LV.RIGA.FOG.1',
    event: 'Yellow Fog Warning',
    headline: null,
    description: 'Fog in places.',
    instruction: 'Drive carefully.',
    severity: 'moderate',
    awareness_level: '2; yellow; Moderate',
    awareness_type: '7; Fog',
    onset: '2026-07-12T01:00:00+00:00',
    expires: '2126-07-12T10:00:00+00:00',
    sender_name: 'LVGMC',
    language: 'en-GB',
    area: 'Riga',
    ...overrides,
  };
}

export function makeEntity(
  entityId: string,
  state: string,
  attributes: HassEntity['attributes'] = {}
): HassEntity {
  return { entity_id: entityId, state, attributes };
}

export function makeHass(
  entities: HassEntity[] = [],
  overrides: Partial<HomeAssistant> = {}
): HomeAssistant {
  return {
    states: Object.fromEntries(entities.map((e) => [e.entity_id, e])),
    locale: { language: 'en' },
    ...overrides,
  };
}
