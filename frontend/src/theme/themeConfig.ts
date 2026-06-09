import type { ThemeConfig } from 'antd';
import { theme } from 'antd';
import type { ThemeMode } from './themeStorage';

export type ResolvedThemeMode = Exclude<ThemeMode, 'system'>;

type LegacyThemeVars = Record<string, string>;

const sharedToken: ThemeConfig['token'] = {
  colorPrimary: '#4D8088',
  borderRadius: 8,
  wireframe: false,
  fontFamily: '"PingFang SC", "Microsoft YaHei", "Heiti SC", Inter, system-ui, sans-serif',
};

const sharedComponents: ThemeConfig['components'] = {
  Button: {
    borderRadius: 8,
    controlHeight: 36,
  },
  Card: {
    borderRadiusLG: 12,
  },
  Tooltip: {
    colorBgSpotlight: sharedToken.colorPrimary,
  },
};

const lightThemeConfig: ThemeConfig = {
  algorithm: theme.defaultAlgorithm,
  token: {
    ...sharedToken,
    colorBgBase: '#F8F6F1',
    colorTextBase: '#2B2B2B',
    colorBgLayout: '#F8F6F1',
    colorBgContainer: '#FFFFFF',
  },
  components: {
    ...sharedComponents,
    Layout: {
      bodyBg: '#F8F6F1',
      headerBg: '#FFFFFF',
      siderBg: '#FFFFFF',
    },
  },
};

const darkThemeConfig: ThemeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    ...sharedToken,
    colorPrimary: '#78aeb6',
    colorBgBase: '#11161b',
    colorTextBase: '#f3f6f8',
    colorBgLayout: '#0b1014',
    colorBgContainer: '#171e24',
  },
  components: {
    ...sharedComponents,
    Layout: {
      bodyBg: '#0b1014',
      headerBg: '#11161b',
      siderBg: '#11161b',
    },
  },
};

export const getThemeConfig = (mode: ResolvedThemeMode): ThemeConfig => {
  return mode === 'dark' ? darkThemeConfig : lightThemeConfig;
};

export const LEGACY_THEME_VARS: Record<ResolvedThemeMode, LegacyThemeVars> = {
  light: {
    '--color-primary': '#4D8088',
    '--color-primary-hover': '#5F9EA8',
    '--color-primary-active': '#3A666C',
    '--color-success': '#52C41A',
    '--color-success-active': '#389E0D',
    '--color-warning': '#FAAD14',
    '--color-error': '#FF4D4F',
    '--color-info': '#1890FF',
    '--color-success-bg': '#F6FFED',
    '--color-success-border': '#B7EB8F',
    '--color-warning-bg': '#FFFBE6',
    '--color-warning-border': '#FFE58F',
    '--color-error-bg': '#FFF2F0',
    '--color-error-border': '#FFCCC7',
    '--color-info-bg': '#E6F7FF',
    '--color-info-border': '#91D5FF',
    '--color-bg-base': '#F8F6F1',
    '--color-bg-container': '#FFFFFF',
    '--color-bg-layout': '#F0F2F5',
    '--color-bg-spotlight': '#3A666C',
    '--color-border': '#D9D9D9',
    '--color-border-secondary': '#F0F0F0',
    '--color-text-base': '#2B2B2B',
    '--color-text-primary': '#2B2B2B',
    '--color-text-secondary': '#595959',
    '--color-text-tertiary': '#8C8C8C',
    '--color-text-quaternary': '#BFBFBF',
    '--shadow-card': '0 2px 8px rgba(0, 0, 0, 0.06)',
    '--shadow-elevated': '0 8px 24px rgba(77, 128, 136, 0.15)',
    '--shadow-primary': '0 4px 16px rgba(77, 128, 136, 0.25)',
    '--shadow-header': '0 2px 8px rgba(0, 0, 0, 0.05)',
  },
  dark: {
    '--color-primary': '#78aeb6',
    '--color-primary-hover': '#8ec3cb',
    '--color-primary-active': '#5d929a',
    '--color-success': '#73d13d',
    '--color-success-active': '#4caf50',
    '--color-warning': '#ffc53d',
    '--color-error': '#ff7875',
    '--color-info': '#69b1ff',
    '--color-success-bg': 'rgba(115, 209, 61, 0.14)',
    '--color-success-border': 'rgba(115, 209, 61, 0.32)',
    '--color-warning-bg': 'rgba(255, 197, 61, 0.14)',
    '--color-warning-border': 'rgba(255, 197, 61, 0.32)',
    '--color-error-bg': 'rgba(255, 120, 117, 0.14)',
    '--color-error-border': 'rgba(255, 120, 117, 0.32)',
    '--color-info-bg': 'rgba(105, 177, 255, 0.14)',
    '--color-info-border': 'rgba(105, 177, 255, 0.32)',
    '--color-bg-base': '#11161b',
    '--color-bg-container': '#171e24',
    '--color-bg-layout': '#0b1014',
    '--color-bg-spotlight': '#24444a',
    '--color-border': '#2b3640',
    '--color-border-secondary': '#202a33',
    '--color-text-base': '#f3f6f8',
    '--color-text-primary': '#f3f6f8',
    '--color-text-secondary': '#c9d3da',
    '--color-text-tertiary': '#97a5af',
    '--color-text-quaternary': '#6f7c86',
    '--shadow-card': '0 10px 28px rgba(0, 0, 0, 0.28)',
    '--shadow-elevated': '0 14px 36px rgba(0, 0, 0, 0.34)',
    '--shadow-primary': '0 10px 24px rgba(120, 174, 182, 0.22)',
    '--shadow-header': '0 10px 24px rgba(0, 0, 0, 0.25)',
  },
};
