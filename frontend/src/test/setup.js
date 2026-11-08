import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';
import { tokenStorage } from '../services/tokenStorage.js';

afterEach(() => {
  cleanup();
  tokenStorage.limpiar();
});
