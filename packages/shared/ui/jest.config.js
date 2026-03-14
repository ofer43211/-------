const preset = require('../../../jest.preset');

/** @type {import('jest').Config} */
module.exports = {
  ...preset,
  testEnvironment: 'jsdom',
  displayName: '@unified/ui',
};
