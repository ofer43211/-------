/**
 * Shared Jest preset for all sub-projects.
 *
 * Usage in a sub-project's jest.config.js:
 *
 *   const preset = require('../../../jest.preset');
 *   module.exports = { ...preset, displayName: 'my-project' };
 */

/** @type {import('jest').Config} */
module.exports = {
  testEnvironment: 'node',

  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        tsconfig: 'tsconfig.json',
      },
    ],
  },

  testMatch: [
    '**/__tests__/**/*.{ts,tsx,js,jsx}',
    '**/*.{spec,test}.{ts,tsx,js,jsx}',
  ],

  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],

  collectCoverageFrom: [
    'src/**/*.{ts,tsx,js,jsx}',
    '!src/**/*.d.ts',
    '!src/**/index.{ts,tsx}',
  ],

  coverageDirectory: 'coverage',

  clearMocks: true,
  restoreMocks: true,
};
