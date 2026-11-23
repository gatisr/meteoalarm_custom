import type { HomeAssistant } from './types';

const TRANSLATIONS: Record<string, Record<string, string>> = {
  en: {
    no_warnings: 'No active warnings',
    until: 'until',
    show_details: 'Show details',
    entity_missing: 'Entity not found:',
    entity_required: 'Please set an entity of the MeteoAlarm integration',
    entity_unavailable: 'Warnings are currently unavailable',
    entity_wrong: 'This entity has no warnings. Select the warning level sensor.',
  },
  lv: {
    no_warnings: 'Nav aktīvu brīdinājumu',
    until: 'līdz',
    show_details: 'Rādīt detaļas',
    entity_missing: 'Vienība nav atrasta:',
    entity_required: 'Norādi MeteoAlarm integrācijas vienību',
    entity_unavailable: 'Brīdinājumi pašlaik nav pieejami',
    entity_wrong: 'Šai vienībai nav brīdinājumu. Izvēlies brīdinājuma līmeņa sensoru.',
  },
};

export function languageOf(hass: HomeAssistant | undefined): string {
  return (hass?.locale?.language ?? hass?.language ?? 'en').split('-')[0];
}

export function localize(hass: HomeAssistant | undefined, key: string): string {
  const lang = languageOf(hass);
  return TRANSLATIONS[lang]?.[key] ?? TRANSLATIONS.en[key] ?? key;
}
