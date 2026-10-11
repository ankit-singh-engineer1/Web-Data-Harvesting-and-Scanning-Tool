import { HttpErrorResponse } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { EMPTY, Subscription, catchError, switchMap, timer } from 'rxjs';

import { ApiService } from '../core/api.service';
import { CrawlStatus } from '../core/models';
import { baseDomain, buildSitemap, normalizeUrl } from '../core/sitemap';
import { downloadFile, formatDuration, toCsv } from '../core/utils';
import { ReconPanel, isPending } from './recon-panel';
import { SitemapTree } from './sitemap-tree';

type Phase = 'idle' | 'running' | 'completed' | 'stopped' | 'error';
type Tab = 'sitemap' | 'links' | 'recon';

const EMPTY_STATUS: CrawlStatus = {
  links: [],
  queue_count: 0,
  crawled_count: 0,
  success_rate: 0,
  intel: { ip: '', nmap: '', whois: '', robots: '' },
};

/** Sites that explicitly allow crawling or scanning, so there is always a safe place to start. */
const EXAMPLES = [
  { value: 'https://scanme.nmap.org/', label: 'Public test host for Nmap' },
  { value: 'https://books.toscrape.com/', label: 'Practice site for crawlers' },
  { value: 'https://quotes.toscrape.com/', label: 'Practice site for crawlers' },
];
const RECENT_KEY = 'sitescope.recent';
const RECENT_MAX = 6;

function loadRecent(): string[] {
  try {
    const parsed = JSON.parse(localStorage.getItem(RECENT_KEY) ?? '[]');
    return Array.isArray(parsed) ? parsed.filter((v) => typeof v === 'string').slice(0, RECENT_MAX) : [];
  } catch {
    return [];
  }
}

const POLL_MS = 2000;
const MAX_FAILED_POLLS = 3;
/** Give slow nmap/whois lookups up to ~200s after the crawl drains before declaring the scan done. */
const MAX_IDLE_POLLS = 100;
const LINK_LIMIT = 500;

@Component({
  selector: 'app-crawler',
  imports: [SitemapTree, ReconPanel],
  templateUrl: './crawler.html',
  styleUrl: './crawler.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Crawler {
  private readonly api = inject(ApiService);
  private run = new Subscription();
  private idlePolls = 0;
  private failedPolls = 0;
  private domain = '';

  readonly tabs: { id: Tab; label: string }[] = [
    { id: 'sitemap', label: 'Sitemap' },
    { id: 'links', label: 'Links' },
    { id: 'recon', label: 'Network data' },
  ];
  readonly linkLimit = LINK_LIMIT;

  readonly url = signal('');
  readonly urlError = signal<string | null>(null);
  readonly target = signal('');
  readonly phase = signal<Phase>('idle');
  readonly error = signal<string | null>(null);
  readonly status = signal<CrawlStatus>(EMPTY_STATUS);
  readonly elapsed = signal(0);
  readonly tab = signal<Tab>('sitemap');
  readonly filter = signal('');

  readonly recent = signal<string[]>(loadRecent());
  /** Recent scans first, then the examples that are not already in the list. */
  readonly suggestions = computed(() => [
    ...this.recent().map((value) => ({ value, label: 'Recent scan' })),
    ...EXAMPLES.filter((e) => !this.recent().includes(e.value)),
  ]);

  readonly running = computed(() => this.phase() === 'running');
  readonly links = computed(() => this.status().links);
  readonly sitemap = computed(() => buildSitemap(this.links()));
  readonly time = computed(() => formatDuration(this.elapsed()));
  readonly rate = computed(() =>
    this.elapsed() > 0 ? (this.status().crawled_count / this.elapsed()).toFixed(1) : '0.0',
  );

  readonly matchingLinks = computed(() => {
    const query = this.filter().trim().toLowerCase();
    const sorted = [...this.links()].sort();
    return query ? sorted.filter((l) => l.toLowerCase().includes(query)) : sorted;
  });
  readonly shownLinks = computed(() => this.matchingLinks().slice(0, LINK_LIMIT));

  readonly stageLabel = computed(() => {
    const { crawled_count, queue_count } = this.status();
    switch (this.phase()) {
      case 'running':
        if (crawled_count === 0) return 'Starting scan';
        return queue_count === 0 ? 'Collecting network data' : 'Crawling';
      case 'completed':
        return 'Completed';
      case 'stopped':
        return 'Stopped';
      case 'error':
        return 'Failed';
      default:
        return 'Ready';
    }
  });

  constructor() {
    inject(DestroyRef).onDestroy(() => this.run.unsubscribe());
    // Lets the header show whether the backend is reachable before the first scan.
    this.api.status().pipe(takeUntilDestroyed(), catchError(() => EMPTY)).subscribe();
  }

  start(): void {
    const target = normalizeUrl(this.url());
    if (!target) {
      this.urlError.set('Enter a full address, like https://example.com');
      return;
    }

    this.run.unsubscribe();
    this.remember(target);
    this.urlError.set(null);
    this.error.set(null);
    this.target.set(target);
    this.domain = baseDomain(target);
    this.status.set(EMPTY_STATUS);
    this.elapsed.set(0);
    this.filter.set('');
    this.tab.set('sitemap');
    this.idlePolls = 0;
    this.failedPolls = 0;
    this.phase.set('running');

    this.api.startCrawl(target).subscribe({
      next: () => this.watch(),
      error: (err) => this.fail(err),
    });
  }

  stop(): void {
    this.run.unsubscribe();
    this.api.stopCrawl().pipe(catchError(() => EMPTY)).subscribe();
    this.phase.set('stopped');
  }

  exportCsv(): void {
    downloadFile(`${this.domain}-pages.csv`, toCsv(this.links()), 'text/csv');
  }

  exportJson(): void {
    const report = { target: this.target(), scannedAt: new Date().toISOString(), ...this.status() };
    downloadFile(`${this.domain}-scan.json`, JSON.stringify(report, null, 2), 'application/json');
  }

  onTabKey(event: KeyboardEvent): void {
    const step = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0;
    if (!step) return;
    const index = this.tabs.findIndex((t) => t.id === this.tab());
    const next = this.tabs[(index + step + this.tabs.length) % this.tabs.length];
    this.tab.set(next.id);
    (event.currentTarget as HTMLElement).querySelector<HTMLElement>(`#tab-${next.id}`)?.focus();
    event.preventDefault();
  }

  private remember(target: string): void {
    const next = [target, ...this.recent().filter((v) => v !== target)].slice(0, RECENT_MAX);
    this.recent.set(next);
    try {
      localStorage.setItem(RECENT_KEY, JSON.stringify(next));
    } catch {
      // Storage can be blocked (private mode); suggestions still work for this session.
    }
  }

  private watch(): void {
    const startedAt = Date.now();
    this.run = new Subscription();
    this.run.add(
      timer(0, 1000).subscribe(() => this.elapsed.set(Math.floor((Date.now() - startedAt) / 1000))),
    );
    this.run.add(
      timer(0, POLL_MS)
        .pipe(
          switchMap(() =>
            this.api.status().pipe(
              catchError((err) => {
                this.pollFailed(err);
                return EMPTY;
              }),
            ),
          ),
        )
        .subscribe((res) => this.apply(res)),
    );
  }

  private apply(res: CrawlStatus): void {
    this.failedPolls = 0;
    // The backend keeps the previous scan's data until the new one boots; ignore it.
    if (!res.links.some((l) => baseDomain(l) === this.domain)) return;

    this.status.set(res);
    const drained = res.queue_count === 0 && res.crawled_count > 0;
    const intelSettled = Object.values(res.intel).every((v) => !isPending(v));
    this.idlePolls = drained ? this.idlePolls + 1 : 0;
    if (this.idlePolls >= 2 && (intelSettled || this.idlePolls >= MAX_IDLE_POLLS)) {
      this.run.unsubscribe();
      this.phase.set('completed');
    }
  }

  private pollFailed(err: unknown): void {
    if (++this.failedPolls >= MAX_FAILED_POLLS) this.fail(err);
  }

  private fail(err: unknown): void {
    this.run.unsubscribe();
    this.phase.set('error');
    this.error.set(this.describe(err));
  }

  private describe(err: unknown): string {
    if (err instanceof HttpErrorResponse) {
      if (err.status === 0) {
        return `Can't reach the API at ${this.api.baseUrl}. Start it with "uvicorn api:app --reload" in the Backend folder.`;
      }
      return `The API returned an error (${err.status}). Check the backend terminal for details.`;
    }
    return 'Something went wrong while scanning. Try again.';
  }
}
