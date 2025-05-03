import { createRouter, createWebHashHistory } from 'vue-router';
import PaperList from './components/PaperList.vue';
import AdvancedSearch from './components/AdvancedSearch.vue';
import ConferenceStats from './components/ConferenceStats.vue';

const routes = [
  {
    path: '/',
    redirect: '/papers'
  },
  {
    path: '/papers',
    name: 'papers',
    component: PaperList
  },
  {
    path: '/advanced-search',
    name: 'advanced-search',
    component: AdvancedSearch
  },
  {
    path: '/stats',
    name: 'stats',
    component: ConferenceStats
  }
];

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes
});

export default router;
