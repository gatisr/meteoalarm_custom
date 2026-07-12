import type { HomeAssistant } from './types';

const TRANSLATIONS: Record<string, Record<string, string>> = {
  en: {
    no_warnings: 'No active warnings',
    all_clear: 'All clear in',
    until: 'until',
    entity_missing: 'Entity not found:',
    entity_required: 'Please set an entity of the MeteoAlarm integration',
    show_more: 'Show details',
  },
  lv: {
    no_warnings: 'Nav aktīvu brīdinājumu',
    all_clear: 'Viss mierīgi:',
    until: 'līdz',
    entity_missing: 'Vienība nav atrasta:',
    entity_required: 'Norādi MeteoAlarm integrācijas vienību',
    show_more: 'Rādīt detaļas',
  },
};

export function localize(hass: HomeAssistant | undefined, key: string): string {
  const lang = (hass?.locale?.language ?? hass?.language ?? 'en').split('-')[0];
  return TRANSLATIONS[lang]?.[key] ?? TRANSLATIONS.en[key] ?? key;
}
