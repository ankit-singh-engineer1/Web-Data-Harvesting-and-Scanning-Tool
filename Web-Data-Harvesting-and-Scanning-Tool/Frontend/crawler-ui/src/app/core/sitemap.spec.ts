import { baseDomain, buildSitemap, normalizeUrl } from './sitemap';
import { formatDuration, toCsv } from './utils';

describe('buildSitemap', () => {
  it('groups pages by host and path segment with counts', () => {
    const root = buildSitemap([
      'https://example.com/',
      'https://example.com/blog/a',
      'https://example.com/blog/b',
      'https://example.com/about',
    ]);

    expect(root.count).toBe(4);
    const host = root.children[0];
    expect(host.name).toBe('example.com');
    expect(host.count).toBe(4);
    expect(host.url).toBe('https://example.com/');
    expect(host.children.map((c) => c.name)).toEqual(['about', 'blog']);
    expect(host.children[1].count).toBe(2);
  });

  it('keeps query strings as separate pages', () => {
    const host = buildSitemap(['https://e.com/p?x=1', 'https://e.com/p?x=2']).children[0];
    expect(host.children.map((c) => c.name)).toEqual(['p?x=1', 'p?x=2']);
  });

  it('counts a trailing-slash duplicate once and skips invalid URLs', () => {
    const root = buildSitemap(['https://e.com/a', 'https://e.com/a/', 'not a url']);
    expect(root.count).toBe(1);
  });
});

describe('normalizeUrl', () => {
  it('adds https and trims whitespace', () => {
    expect(normalizeUrl(' example.com ')).toBe('https://example.com/');
    expect(normalizeUrl('http://a.io/x')).toBe('http://a.io/x');
  });

  it('rejects empty and unusable input', () => {
    expect(normalizeUrl('')).toBeNull();
    expect(normalizeUrl('localhost')).toBeNull();
    expect(normalizeUrl('not a url')).toBeNull();
  });
});

describe('helpers', () => {
  it('reduces hostnames to the base domain', () => {
    expect(baseDomain('https://www.blog.example.com/x')).toBe('example.com');
  });

  it('formats durations as m:ss', () => {
    expect(formatDuration(65)).toBe('1:05');
  });

  it('escapes quotes in CSV output', () => {
    expect(toCsv(['https://a.com/?q="x"'])).toBe('url\r\n"https://a.com/?q=""x"""');
  });
});
