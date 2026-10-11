export interface SitemapNode {
  name: string;
  /** Unique key: host followed by the raw path segments. */
  path: string;
  /** Set when a crawled page lives at exactly this node. */
  url?: string;
  /** Number of crawled pages at or below this node. */
  count: number;
  children: SitemapNode[];
}

/** Last two hostname labels, e.g. www.blog.example.com -> example.com (matches the backend's rule). */
export function baseDomain(url: string): string {
  try {
    return new URL(url).hostname.split('.').slice(-2).join('.');
  } catch {
    return '';
  }
}

/** Adds https:// when missing and returns a full URL, or null when the input is not a usable address. */
export function normalizeUrl(input: string): string | null {
  const value = input.trim();
  if (!value) return null;
  const candidate = /^https?:\/\//i.test(value) ? value : `https://${value}`;
  try {
    const parsed = new URL(candidate);
    return parsed.hostname.includes('.') ? parsed.href : null;
  } catch {
    return null;
  }
}

const decode = (segment: string): string => {
  try {
    return decodeURIComponent(segment);
  } catch {
    return segment;
  }
};

/** Groups flat URLs into a host > path-segment tree. Query strings stay on the last segment. */
export function buildSitemap(urls: readonly string[]): SitemapNode {
  const root: SitemapNode = { name: '', path: '', count: 0, children: [] };
  const seen = new Set<string>();

  for (const raw of urls) {
    let parsed: URL;
    try {
      parsed = new URL(raw);
    } catch {
      continue;
    }

    const segments = [parsed.host, ...parsed.pathname.split('/').filter(Boolean)];
    if (parsed.search) segments[segments.length - 1] += parsed.search;

    const key = segments.join('/');
    if (seen.has(key)) continue;
    seen.add(key);

    let node = root;
    for (const segment of segments) {
      const path = node.path ? `${node.path}/${segment}` : segment;
      let child = node.children.find((c) => c.path === path);
      if (!child) {
        child = { name: decode(segment), path, count: 0, children: [] };
        node.children.push(child);
      }
      child.count++;
      node = child;
    }
    node.url = raw;
    root.count++;
  }

  sortChildren(root);
  return root;
}

function sortChildren(node: SitemapNode): void {
  node.children.sort((a, b) => a.name.localeCompare(b.name));
  node.children.forEach(sortChildren);
}
