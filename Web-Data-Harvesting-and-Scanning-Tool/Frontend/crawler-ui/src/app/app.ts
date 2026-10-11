import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { ApiService } from './core/api.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  protected readonly api = inject(ApiService);

  protected readonly apiLabel = computed(() => {
    const online = this.api.online();
    return online === null ? 'Checking API' : online ? 'API connected' : 'API offline';
  });
}
