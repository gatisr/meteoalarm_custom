import { beforeAll, describe, expect, it } from 'vitest';

import type { MeteoAlarmCardEditor } from '../src/editor';
import { makeHass } from './helpers';

beforeAll(async () => {
  await import('../src/editor');
});

async function mountEditor(language = 'en') {
  const editor = document.createElement('meteoalarm-card-editor') as MeteoAlarmCardEditor;
  editor.hass = makeHass([], { locale: { language } });
  editor.setConfig({ type: 'custom:meteoalarm-card', entity: 'sensor.x' });
  document.body.appendChild(editor);
  await editor.updateComplete;
  return editor;
}

describe('meteoalarm-card-editor', () => {
  it('only offers warning level sensors of this integration', async () => {
    const editor = await mountEditor();
    const form = editor.shadowRoot!.querySelector('ha-form') as unknown as {
      schema: Array<{ name: string; selector: { entity?: { filter: unknown[] } } }>;
    };

    const entityField = form.schema.find((field) => field.name === 'entity')!;
    expect(entityField.selector.entity!.filter).toEqual([
      { integration: 'meteoalarm_custom', domain: 'sensor', device_class: 'enum' },
    ]);
  });


  it('emits config-changed when the form changes', async () => {
    const editor = await mountEditor();
    const received: unknown[] = [];
    editor.addEventListener('config-changed', (ev) =>
      received.push((ev as CustomEvent).detail.config)
    );

    const form = editor.shadowRoot!.querySelector('ha-form')!;
    form.dispatchEvent(
      new CustomEvent('value-changed', { detail: { value: { entity: 'sensor.y' } } })
    );

    expect(received).toEqual([{ entity: 'sensor.y' }]);
  });
});
