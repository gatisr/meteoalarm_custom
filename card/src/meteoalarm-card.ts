import { LitElement, html, css, nothing, type PropertyValues } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';

import './editor';
import { CARD_TYPE, CARD_VERSION, EDITOR_TYPE, SEVERITY_COLORS, iconForAlert } from './const';
import { localize } from './localize';
import type { AlertData, HassEntity, HomeAssistant, MeteoAlarmCardConfig } from './types';

/* eslint-disable no-console */
console.info(
  `%c METEOALARM-CARD %c ${CARD_VERSION} `,
  'color: white; background: #e65100; font-weight: 700;',
  'color: #e65100; background: white; font-weight: 700;'
);

declare global {
  interface Window {
    customCards?: Array<Record<string, unknown>>;
  }
}

window.customCards = window.customCards ?? [];
window.customCards.push({
  type: CARD_TYPE,
  name: 'MeteoAlarm Card',
  description: 'Shows active MeteoAlarm weather warnings for a region.',
  preview: true,
  documentationURL: 'https://github.com/gatisr/meteoalarm_custom',
});

@customElement(CARD_TYPE)
export class MeteoAlarmCard extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;

  @state() private _config?: MeteoAlarmCardConfig;

  public static async getConfigElement(): Promise<HTMLElement> {
    return document.createElement(EDITOR_TYPE);
  }

  public static getStubConfig(hass: HomeAssistant): Partial<MeteoAlarmCardConfig> {
    const entity = Object.values(hass.states).find(
      (s) => s.entity_id.startsWith('sensor.') && Array.isArray(s.attributes.alerts)
    );
    return { entity: entity?.entity_id };
  }

  public setConfig(config: MeteoAlarmCardConfig): void {
    this._config = { show_description: true, ...config };
  }

  public getCardSize(): number {
    return 1 + (this._entity()?.attributes.alerts?.length ?? 0) * 2;
  }

  protected shouldUpdate(changedProps: PropertyValues): boolean {
    if (changedProps.has('_config')) {
      return true;
    }
    const oldHass = changedProps.get('hass') as HomeAssistant | undefined;
    if (!oldHass || !this._config?.entity) {
      return true;
    }
    return oldHass.states[this._config.entity] !== this.hass?.states[this._config.entity];
  }

  private _entity(): HassEntity | undefined {
    if (!this.hass || !this._config?.entity) {
      return undefined;
    }
    return this.hass.states[this._config.entity];
  }

  private _title(entity: HassEntity | undefined): string {
    if (this._config?.title) {
      return this._config.title;
    }
    const area = entity?.attributes.area;
    if (area) {
      return area;
    }
    return entity?.attributes.friendly_name ?? 'MeteoAlarm';
  }

  private _formatTime(iso: string | null): string {
    if (!iso) {
      return '';
    }
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) {
      return '';
    }
    const lang = this.hass?.locale?.language ?? 'en';
    const sameDay = new Date().toDateString() === date.toDateString();
    return new Intl.DateTimeFormat(lang, {
      ...(sameDay ? {} : { day: 'numeric', month: 'short' }),
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  }

  private _timeRange(alert: AlertData): string {
    const from = this._formatTime(alert.onset);
    const to = this._formatTime(alert.expires);
    if (from && to) {
      return `${from} – ${to}`;
    }
    if (to) {
      return `${localize(this.hass, 'until')} ${to}`;
    }
    return from;
  }

  protected render() {
    if (!this._config) {
      return nothing;
    }
    if (!this._config.entity) {
      return this._warning(localize(this.hass, 'entity_required'));
    }
    const entity = this._entity();
    if (!entity) {
      return this._warning(`${localize(this.hass, 'entity_missing')} ${this._config.entity}`);
    }

    const alerts = entity.attributes.alerts ?? [];
    const severity = entity.state in SEVERITY_COLORS ? entity.state : 'none';
    const color = SEVERITY_COLORS[severity];
    const stateLabel = this.hass?.formatEntityState?.(entity) ?? entity.state;

    return html`
      <ha-card>
        <div class="header">
          <ha-icon class="header-icon" style="color: ${color}"
            icon=${alerts.length ? 'mdi:alert-decagram' : 'mdi:shield-check'}
          ></ha-icon>
          <div class="name">${this._title(entity)}</div>
          <div class="badge" style="background: ${color}">${stateLabel}</div>
        </div>
        ${alerts.length === 0
          ? html`<div class="calm">${localize(this.hass, 'no_warnings')}</div>`
          : alerts.map((alert) => this._renderAlert(alert))}
      </ha-card>
    `;
  }

  private _renderAlert(alert: AlertData) {
    const color = SEVERITY_COLORS[alert.severity] ?? SEVERITY_COLORS.none;
    const compact = this._config?.compact ?? false;
    return html`
      <div class="alert" style="border-color: ${color}">
        <ha-icon icon=${iconForAlert(alert.awareness_type, alert.event)} style="color: ${color}"></ha-icon>
        <div class="alert-body">
          <div class="event">${alert.event ?? alert.headline ?? ''}</div>
          <div class="time">${this._timeRange(alert)}</div>
          ${!compact && this._config?.show_description && alert.description
            ? html`<div class="description">${alert.description}</div>`
            : nothing}
          ${!compact && this._config?.show_instruction && alert.instruction
            ? html`<div class="instruction">${alert.instruction}</div>`
            : nothing}
        </div>
      </div>
    `;
  }

  private _warning(message: string) {
    return html`<ha-card><div class="calm">${message}</div></ha-card>`;
  }

  static styles = css`
    ha-card {
      padding: 12px 16px 16px;
    }
    .header {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 4px 0 8px;
    }
    .header-icon {
      --mdc-icon-size: 26px;
    }
    .name {
      flex: 1;
      font-size: 1.15rem;
      font-weight: 500;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .badge {
      color: #fff;
      border-radius: 12px;
      padding: 3px 10px;
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    .calm {
      color: var(--secondary-text-color);
      padding: 4px 0;
    }
    .alert {
      display: flex;
      gap: 12px;
      align-items: flex-start;
      border-left: 4px solid;
      border-radius: 4px;
      background: var(--secondary-background-color, rgba(0, 0, 0, 0.04));
      padding: 10px 12px;
      margin-top: 8px;
    }
    .alert ha-icon {
      --mdc-icon-size: 24px;
      margin-top: 2px;
    }
    .alert-body {
      flex: 1;
      min-width: 0;
    }
    .event {
      font-weight: 500;
    }
    .time {
      color: var(--secondary-text-color);
      font-size: 0.85rem;
      margin-top: 2px;
    }
    .description,
    .instruction {
      font-size: 0.9rem;
      margin-top: 6px;
      white-space: pre-line;
    }
    .instruction {
      color: var(--secondary-text-color);
      font-style: italic;
    }
  `;
}

declare global {
  interface HTMLElementTagNameMap {
    'meteoalarm-card': MeteoAlarmCard;
  }
}
