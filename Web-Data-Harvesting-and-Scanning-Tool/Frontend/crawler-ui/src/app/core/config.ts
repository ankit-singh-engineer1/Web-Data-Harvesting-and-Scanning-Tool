import { InjectionToken } from '@angular/core';

/** Base URL of the FastAPI backend. Override in tests or per environment via providers. */
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL', {
  providedIn: 'root',
  factory: () => 'http://localhost:8000',
});
