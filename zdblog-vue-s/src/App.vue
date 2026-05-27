<script setup>
import { useRoute } from 'vue-router'
import AdminLayout from '@/components/AdminLayout.vue'

const route = useRoute()
</script>

<template>
  <AdminLayout v-if="route.meta.layout === 'admin'">
    <router-view />
  </AdminLayout>
  <router-view v-else />
</template>

<style>
@import '@/assets/main.css';
</style>
