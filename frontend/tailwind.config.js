/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Syne"', 'sans-serif'],
        body:    ['"DM Sans"', 'sans-serif'],
        mono:    ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        bg:      '#080C14',
        surface: '#0D1320',
        border:  '#1A2332',
        muted:   '#2A3A52',
        dim:     '#4A6080',
        text:    '#C8D8EC',
        bright:  '#E8F0FA',
        accent:  '#3B82F6',
        green:   '#10B981',
        red:     '#EF4444',
        amber:   '#F59E0B',
        purple:  '#8B5CF6',
      },
    },
  },
  plugins: [],
}
