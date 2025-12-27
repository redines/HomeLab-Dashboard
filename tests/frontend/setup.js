/**
 * Jest setup file for frontend tests
 */

// Setup DOM globals
global.document = window.document;
global.window = window;
global.navigator = window.navigator;

// Mock fetch API
global.fetch = jest.fn();

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  error: jest.fn(),
  warn: jest.fn(),
  log: jest.fn(),
};

// Reset mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
  fetch.mockClear();
});

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock cookies for CSRF token
Object.defineProperty(document, 'cookie', {
  writable: true,
  value: 'csrftoken=test_csrf_token',
});
