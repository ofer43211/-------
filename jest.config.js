/** @type {import('jest').Config} */
module.exports = {
  // Collect projects from all workspace categories
  projects: [
    '<rootDir>/packages/shared/*/jest.config.*',
    '<rootDir>/packages/rotem/*/jest.config.*',
    '<rootDir>/packages/gemini/*/jest.config.*',
    '<rootDir>/packages/ai-platforms/*/jest.config.*',
    '<rootDir>/packages/tools/*/jest.config.*',
    '<rootDir>/packages/infrastructure/*/jest.config.*',
  ],

  // Shared coverage settings
  collectCoverageFrom: [
    'src/**/*.{ts,tsx,js,jsx}',
    '!src/**/*.d.ts',
    '!src/**/index.{ts,tsx}',
  ],

  coverageDirectory: '<rootDir>/coverage',

  coverageThresholds: {
    global: {
      branches: 50,
      functions: 50,
      lines: 50,
      statements: 50,
    },
  },
};
