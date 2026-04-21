import { Routes } from '@angular/router';
import { VisualizerPage } from './visualizer-page/visualizer-page';
import { ProfilePage } from './profile-page/profile-page';
import { App } from './app';
import { MainPage } from './main-page/main-page';

export const routes: Routes = [
    {
    path: '',
    component: MainPage,
  },
  {
    path: 'visualizer',
    component: VisualizerPage,
  },
  {
    path: 'profile',
    component: ProfilePage,
  },
];