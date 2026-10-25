import { InjectionToken } from '@angular/core';

/** Base URL of the FastAPI backend. Override in tests or per environment via providers. */
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL', {
  providedIn: 'root',
  factory: () => 'https://crawler-backend-i7nb.onrender.com',
});
