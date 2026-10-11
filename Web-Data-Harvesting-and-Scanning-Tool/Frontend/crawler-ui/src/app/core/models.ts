export interface SiteIntel {
  ip: string;
  nmap: string;
  whois: string;
  robots: string;
}

export interface CrawlStatus {
  links: string[];
  queue_count: number;
  crawled_count: number;
  success_rate: number;
  intel: SiteIntel;
}

export interface MessageResponse {
  message: string;
}
