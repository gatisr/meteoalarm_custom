export interface MeteoAlarmCardConfig {
  type: string;
  entity?: string;
  title?: string;
  show_description?: boolean;
  show_instruction?: boolean;
  compact?: boolean;
}

export interface AlertData {
  identifier: string;
  event: string | null;
  headline: string | null;
  description: string | null;
  instruction: string | null;
  severity: string;
  awareness_level: string | null;
  awareness_type: string | null;
  onset: string | null;
  expires: string | null;
  sender_name: string | null;
  language: string | null;
  area: string | null;
}

export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown> & {
    friendly_name?: string;
    alerts?: AlertData[];
    area?: string | null;
  };
}

export interface HomeAssistant {
  states: Record<string, HassEntity>;
  locale?: { language: string };
  language?: string;
  formatEntityState?: (stateObj: HassEntity) => string;
}
