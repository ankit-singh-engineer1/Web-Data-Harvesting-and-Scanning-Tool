import { ChangeDetectionStrategy, Component, computed, input, signal } from '@angular/core';

import { SiteIntel } from '../core/models';

type ReconKey = keyof Pick<SiteIntel, 'nmap' | 'whois' | 'robots'>;

const PENDING = /^(Analyzing|Scanning|Retrieving|Checking)\.\.\.$/;

/** The backend returns placeholder strings until each lookup finishes. */
export const isPending = (value: string): boolean => !value || PENDING.test(value);

@Component({
  selector: 'app-recon-panel',
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrl: './recon-panel.scss',
  template: `
    <p class="address">
      <span class="address__label">Resolved address</span>
      <span class="address__value">{{ ipPending() ? 'Resolving…' : intel().ip }}</span>
    </p>

    <div class="recon">
      <div class="recon__nav" role="group" aria-label="Lookup type">
        @for (item of items; track item.key) {
          <button type="button" class="pick" [attr.aria-pressed]="view() === item.key" (click)="view.set(item.key)">
            {{ item.label }}
          </button>
        }
      </div>

      <div class="out">
        <div class="out__head">
          <span class="out__title">{{ current().title }}</span>
          <button type="button" class="out__copy" [disabled]="pending()" (click)="copy()">
            {{ copied() ? 'Copied' : 'Copy' }}
          </button>
        </div>
        @if (pending()) {
          <p class="out__wait">Waiting for results. {{ current().wait }}</p>
        } @else {
          <pre class="out__body" tabindex="0">{{ output() }}</pre>
        }
      </div>
    </div>
  `,
})
export class ReconPanel {
  readonly intel = input.required<SiteIntel>();

  readonly items: { key: ReconKey; label: string; title: string; wait: string }[] = [
    { key: 'nmap', label: 'Port scan', title: 'nmap -F (fast scan, top 100 ports)', wait: 'Port scans can take a minute.' },
    { key: 'whois', label: 'WHOIS', title: 'WHOIS record', wait: 'This starts after the port scan.' },
    { key: 'robots', label: 'robots.txt', title: 'robots.txt', wait: 'This starts after the WHOIS lookup.' },
  ];

  readonly view = signal<ReconKey>('nmap');
  readonly copied = signal(false);

  readonly current = computed(() => this.items.find((i) => i.key === this.view())!);
  readonly output = computed(() => this.intel()[this.view()]);
  readonly pending = computed(() => isPending(this.output()));
  readonly ipPending = computed(() => isPending(this.intel().ip));

  async copy(): Promise<void> {
    try {
      await navigator.clipboard.writeText(this.output());
      this.copied.set(true);
      setTimeout(() => this.copied.set(false), 1500);
    } catch {
      // Clipboard access can be denied; the text stays selectable in the pane.
    }
  }
}
