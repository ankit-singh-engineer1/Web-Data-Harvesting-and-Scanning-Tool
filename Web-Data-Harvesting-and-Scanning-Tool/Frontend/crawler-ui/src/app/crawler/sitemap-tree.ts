import { NgTemplateOutlet } from '@angular/common';
import { ChangeDetectionStrategy, Component, input } from '@angular/core';

import { SitemapNode } from '../core/sitemap';

@Component({
  selector: 'app-sitemap-tree',
  imports: [NgTemplateOutlet],
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrl: './sitemap-tree.scss',
  template: `
    <ng-template #branch let-node let-depth="depth">
      @if (node.children.length) {
        <details [open]="depth === 0">
          <summary>
            <span class="chev" aria-hidden="true"></span>
            @if (node.url) {
              <a class="name" [href]="node.url" target="_blank" rel="noopener noreferrer">{{ node.name }}</a>
            } @else {
              <span class="name">{{ node.name }}</span>
            }
            <span class="count" [attr.aria-label]="node.count + ' pages'">{{ node.count }}</span>
          </summary>
          <ul>
            @for (child of node.children; track child.path) {
              <li>
                <ng-container [ngTemplateOutlet]="branch" [ngTemplateOutletContext]="{ $implicit: child, depth: depth + 1 }" />
              </li>
            }
          </ul>
        </details>
      } @else {
        <a class="leaf name" [href]="node.url" target="_blank" rel="noopener noreferrer">{{ node.name }}</a>
      }
    </ng-template>

    <ul class="tree">
      @for (host of root().children; track host.path) {
        <li>
          <ng-container [ngTemplateOutlet]="branch" [ngTemplateOutletContext]="{ $implicit: host, depth: 0 }" />
        </li>
      }
    </ul>
  `,
})
export class SitemapTree {
  readonly root = input.required<SitemapNode>();
}
