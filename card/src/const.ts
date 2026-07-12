export const CARD_VERSION = '1.0.0';
export const CARD_TYPE = 'meteoalarm-card';
export const EDITOR_TYPE = 'meteoalarm-card-editor';

export const SEVERITY_COLORS: Record<string, string> = {
  none: 'var(--success-color, #4caf50)',
  minor: 'var(--info-color, #43a047)',
  moderate: 'var(--warning-color, #ffb300)',
  severe: 'var(--meteoalarm-severe-color, #ff7043)',
  extreme: 'var(--error-color, #f44336)',
};

// Matched case-insensitively against the name part of awareness_type
// (e.g. "1; Wind" or "10; rain").
const TYPE_ICONS: [string, string][] = [
  ['wind', 'mdi:weather-windy'],
  ['snow', 'mdi:snowflake-alert'],
  ['ice', 'mdi:snowflake-alert'],
  ['thunder', 'mdi:weather-lightning-rainy'],
  ['fog', 'mdi:weather-fog'],
  ['high-temp', 'mdi:thermometer-plus'],
  ['high temp', 'mdi:thermometer-plus'],
  ['heat', 'mdi:thermometer-plus'],
  ['low-temp', 'mdi:thermometer-minus'],
  ['low temp', 'mdi:thermometer-minus'],
  ['cold', 'mdi:thermometer-minus'],
  ['coastal', 'mdi:waves-arrow-up'],
  ['fire', 'mdi:pine-tree-fire'],
  ['avalanche', 'mdi:landslide'],
  ['rain-flood', 'mdi:home-flood'],
  ['flood', 'mdi:home-flood'],
  ['rain', 'mdi:weather-pouring'],
];

export function iconForAlert(awarenessType: string | null, event: string | null): string {
  const haystack = `${awarenessType ?? ''} ${event ?? ''}`.toLowerCase();
  for (const [needle, icon] of TYPE_ICONS) {
    if (haystack.includes(needle)) {
      return icon;
    }
  }
  return 'mdi:alert-outline';
}
