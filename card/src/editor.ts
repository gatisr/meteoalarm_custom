import { LitElement, html, css, nothing } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';

import { EDITOR_TYPE } from './const';
import type { HomeAssistant, MeteoAlarmCardConfig } from './types';

const SCHEMA = [
  {
    name: 'entity',
    required: true,
    selector: {
      entity: { filter: [{ integration: 'meteoalarm_custom', domain: 'sensor' }] },
    },
  },
  { name: 'title', selector: { text: {} } },
  {
    name: 'show_description',
    default: true,
    selector: { boolean: {} },
  },
  { name: 'show_instruction', selector: { boolean: {} } },
  { name: 'compact', selector: { boolean: {} } },
];

const LABELS: Record<string, Record<string, string>> = {
  en: {
    entity: 'Entity (warning level sensor)',
    title: 'Title',
    show_description: 'Show warning description',
    show_instruction: 'Show instructions',
    compact: 'Compact mode',
  },
  lv: {
    entity: 'Vienība (brīdinājuma līmeņa sensors)',
    title: 'Virsraksts',
    show_description: 'Rādīt brīdinājuma aprakstu',
    show_instruction: 'Rādīt norādījumus',
    compact: 'Kompaktais režīms',
  },
};

@customElement(EDITOR_TYPE)
export class MeteoAlarmCardEditor extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;

  @state() private _config?: MeteoAlarmCardConfig;

  public setConfig(config: MeteoAlarmCardConfig): void {
    this._config = config;
  }

  private _computeLabel = (schema: { name: string }): string => {
    const lang = (this.hass?.locale?.language ?? 'en').split('-')[0];
    return LABELS[lang]?.[schema.name] ?? LABELS.en[schema.name] ?? schema.name;
  };

  private _valueChanged(ev: CustomEvent): void {
    ev.stopPropagation();
    const config = ev.detail.value as MeteoAlarmCardConfig;
    this.dispatchEvent(
      new CustomEvent('config-changed', {
        detail: { config },
        bubbles: true,
        composed: true,
      })
    );
  }

  protected render() {
    if (!this.hass || !this._config) {
      return nothing;
    }
    return html`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${SCHEMA}
        .computeLabel=${this._computeLabel}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `;
  }

  static styles = css`
    ha-form {
      display: block;
    }
  `;
}

declare global {
  interface HTMLElementTagNameMap {
    'meteoalarm-card-editor': MeteoAlarmCardEditor;
  }
}
