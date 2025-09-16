<template>
  <v-app>
    <v-navigation-drawer
      v-model="drawer"
      app
      clipped
      permanent
      width="280"
    >
      <v-list>
        <v-list-item
          prepend-icon="mdi-solar-panel"
          title="Solar Configurator"
          subtitle="Professional PV & HP Tool"
        />
      </v-list>
      
      <v-divider />
      
      <v-list density="compact" nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.route"
          :prepend-icon="item.icon"
          :title="item.title"
          :subtitle="item.subtitle"
          :value="item.route"
          :to="item.route"
          color="primary"
        />
      </v-list>
    </v-navigation-drawer>

    <v-app-bar
      app
      clipped-left
      color="primary"
      dark
    >
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      
      <v-toolbar-title>
        {{ currentPageTitle }}
      </v-toolbar-title>
      
      <v-spacer />
      
      <!-- Backend Status -->
      <v-chip
        :color="backendStatus.connected ? 'success' : 'error'"
        variant="flat"
        size="small"
        class="mr-2"
      >
        <v-icon
          :icon="backendStatus.connected ? 'mdi-check-circle' : 'mdi-alert-circle'"
          start
        />
        {{ backendStatus.connected ? 'Backend OK' : 'Backend Offline' }}
      </v-chip>
      
      <!-- Theme Toggle -->
      <v-btn
        icon
        @click="toggleTheme"
      >
        <v-icon>
          {{ theme.global.name.value === 'light' ? 'mdi-weather-night' : 'mdi-weather-sunny' }}
        </v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid class="pa-0">
        <router-view />
      </v-container>
    </v-main>

    <!-- Global Loading Overlay -->
    <v-overlay
      v-model="isLoading"
      class="align-center justify-center"
    >
      <v-progress-circular
        color="primary"
        indeterminate
        size="64"
      />
      <div class="text-h6 mt-4">{{ loadingMessage }}</div>
    </v-overlay>

    <!-- Global Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      location="top right"
    >
      {{ snackbar.message }}
      <template #actions>
        <v-btn
          color="white"
          variant="text"
          @click="snackbar.show = false"
        >
          Schließen
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTheme } from 'vuetify'
import { useAppStore } from '@/store/app'
import { listen } from '@tauri-apps/api/event'

const theme = useTheme()
const route = useRoute()
const appStore = useAppStore()

const drawer = ref(true)

// Menu items matching original Streamlit structure
const menuItems = [
  {
    title: 'Eingabe',
    subtitle: 'Projektdaten',
    icon: 'mdi-form-select',
    route: '/input'
  },
  {
    title: 'Analyse',
    subtitle: 'Berechnung & KPIs',
    icon: 'mdi-chart-line',
    route: '/analysis'
  },
  {
    title: 'PDF-Erstellung',
    subtitle: 'Angebots-PDF',
    icon: 'mdi-file-pdf-box',
    route: '/pdf'
  },
  {
    title: 'Schnellkalkulation',
    subtitle: 'Quick Calc',
    icon: 'mdi-calculator',
    route: '/quick-calc'
  },
  {
    title: 'Wärmepumpe',
    subtitle: 'HP-Angebote',
    icon: 'mdi-heat-pump',
    route: '/heatpump'
  },
  {
    title: 'CRM',
    subtitle: 'Kundenverwaltung',
    icon: 'mdi-account-group',
    route: '/crm'
  },
  {
    title: 'Administration',
    subtitle: 'Einstellungen',
    icon: 'mdi-cog',
    route: '/admin'
  }
]

const currentPageTitle = computed(() => {
  const currentItem = menuItems.find(item => item.route === route.path)
  return currentItem ? currentItem.title : 'Solar Configurator'
})

const backendStatus = computed(() => appStore.backendStatus)
const isLoading = computed(() => appStore.isLoading)
const loadingMessage = computed(() => appStore.loadingMessage)
const snackbar = computed(() => appStore.snackbar)

const toggleTheme = () => {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
}

// Listen to Tauri menu events
onMounted(async () => {
  // Check backend status
  await appStore.checkBackendStatus()
  
  // Setup periodic backend health check
  setInterval(() => {
    appStore.checkBackendStatus()
  }, 30000) // Check every 30 seconds
  
  // Listen to Tauri menu events
  await listen('menu_action', (event) => {
    const action = event.payload as string
    switch (action) {
      case 'new_project':
        appStore.showSnackbar('Neues Projekt', 'info')
        break
      case 'about':
        appStore.showSnackbar('Solar Configurator v1.0.0', 'info')
        break
    }
  })
  
  await listen('navigate', (event) => {
    const route = event.payload as string
    // Handle navigation from menu
    if (route) {
      window.location.hash = '#' + route
    }
  })
})
</script>

<style scoped>
.v-navigation-drawer {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}

.v-app-bar {
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}
</style>