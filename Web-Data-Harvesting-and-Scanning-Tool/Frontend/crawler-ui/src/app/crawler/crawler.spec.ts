import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Crawler } from './crawler';

const API = 'http://localhost:8000';

describe('Crawler', () => {
  let fixture: ComponentFixture<Crawler>;
  let component: Crawler;
  let http: HttpTestingController;

  beforeEach(async () => {
    localStorage.clear();
    await TestBed.configureTestingModule({
      imports: [Crawler],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(Crawler);
    component = fixture.componentInstance;
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('rejects an unusable address without calling the API', () => {
    component.url.set('not a url');
    component.start();

    expect(component.urlError()).toContain('full address');
    expect(component.phase()).toBe('idle');
    http.expectNone(`${API}/crawl`);
  });

  it('posts the normalised address and enters the running phase', () => {
    component.url.set('example.com');
    component.start();

    const req = http.expectOne(`${API}/crawl`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ url: 'https://example.com/' });
    expect(component.phase()).toBe('running');
  });

  it('suggests recent scans first and does not repeat them', () => {
    expect(component.suggestions()[0].label).not.toBe('Recent scan');

    component.url.set('books.toscrape.com');
    component.start();

    const suggestions = component.suggestions();
    expect(suggestions[0]).toEqual({ value: 'https://books.toscrape.com/', label: 'Recent scan' });
    expect(suggestions.filter((s) => s.value === 'https://books.toscrape.com/').length).toBe(1);
  });

  it('explains how to start the API when it is unreachable', () => {
    component.url.set('example.com');
    component.start();

    http.expectOne(`${API}/crawl`).error(new ProgressEvent('error'), { status: 0 });

    expect(component.phase()).toBe('error');
    expect(component.error()).toContain('uvicorn api:app --reload');
  });
});
