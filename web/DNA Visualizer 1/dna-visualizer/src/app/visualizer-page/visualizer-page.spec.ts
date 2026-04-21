import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VisualizerPage } from './visualizer-page';

describe('VisualizerPage', () => {
  let component: VisualizerPage;
  let fixture: ComponentFixture<VisualizerPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VisualizerPage]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VisualizerPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
