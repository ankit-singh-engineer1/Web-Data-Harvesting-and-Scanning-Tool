export function formatDuration(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

export function toCsv(urls: readonly string[]): string {
  const rows = urls.map((u) => `"${u.replaceAll('"', '""')}"`);
  return ['url', ...rows].join('\r\n');
}

export function downloadFile(name: string, content: string, type: string): void {
  const href = URL.createObjectURL(new Blob([content], { type: `${type};charset=utf-8` }));
  const anchor = document.createElement('a');
  anchor.href = href;
  anchor.download = name;
  anchor.click();
  URL.revokeObjectURL(href);
}
