import type { HomeAssistant } from './types';

function resolveTimeZone(hass: HomeAssistant | undefined): string | undefined {
  // "local" (default) uses the browser's zone; "server" follows Home Assistant's.
  return hass?.locale?.time_zone === 'server' ? hass.config?.time_zone : undefined;
}

/**
 * Format an ISO timestamp for the card, honouring the Home Assistant user's
 * language, time zone and 12/24-hour preference. Today's times show only the
 * clock, other days also show the date.
 */
export function formatTime(
  iso: string | null,
  hass: HomeAssistant | undefined,
  now: Date = new Date()
): string {
  if (!iso) {
    return '';
  }
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return '';
  }

  const language = hass?.locale?.language ?? hass?.language ?? 'en';
  const timeZone = resolveTimeZone(hass);
  const timeFormat = hass?.locale?.time_format;

  const dayKey = (d: Date) =>
    new Intl.DateTimeFormat('en-CA', {
      timeZone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    }).format(d);
  const sameDay = dayKey(now) === dayKey(date);

  return new Intl.DateTimeFormat(language, {
    timeZone,
    hour12: timeFormat === '12' ? true : undefined,
    hourCycle: timeFormat === '24' ? 'h23' : undefined,
    ...(sameDay ? {} : { day: 'numeric', month: 'short' }),
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}
