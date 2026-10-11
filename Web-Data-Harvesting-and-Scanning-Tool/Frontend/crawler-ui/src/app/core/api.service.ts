import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { tap } from 'rxjs';

import { API_BASE_URL } from './config';
import { CrawlStatus, MessageResponse } from './models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  readonly baseUrl = inject(API_BASE_URL);

  /** null = not checked yet, true = last call succeeded, false = last call failed to connect. */
  readonly online = signal<boolean | null>(null);

  startCrawl(url: string) {
    return this.http
      .post<MessageResponse>(`${this.baseUrl}/crawl`, { url })
      .pipe(this.trackHealth());
  }

  stopCrawl() {
    return this.http.post<MessageResponse>(`${this.baseUrl}/stop`, {}).pipe(this.trackHealth());
  }

  status() {
    return this.http.get<CrawlStatus>(`${this.baseUrl}/status`).pipe(this.trackHealth());
  }

  private trackHealth<T>() {
    return tap<T>({
      next: () => this.online.set(true),
      error: (err) => this.online.set(err?.status === 0 ? false : true),
    });
  }
}
