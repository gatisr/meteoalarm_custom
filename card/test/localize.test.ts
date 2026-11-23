import { describe, expect, it } from 'vitest';

import { languageOf, localize } from '../src/localize';
import { makeHass } from './helpers';

describe('localize', () => {
  it('translates into the user language', () => {
    expect(localize(makeHass([], { locale: { language: 'lv' } }), 'no_warnings')).toBe(
      'Nav aktīvu brīdinājumu'
    );
  });


  it('falls back to hass.language when locale is missing', () => {
    expect(localize({ states: {}, language: 'lv' }, 'until')).toBe('līdz');
  });

  it('falls back to English for unknown languages and to the key for unknown keys', () => {
    const hass = makeHass([], { locale: { language: 'xx' } });
    expect(localize(hass, 'until')).toBe('until');
    expect(localize(hass, 'does_not_exist')).toBe('does_not_exist');
  });

});
