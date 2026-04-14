import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { fetchMe } from '../services/auth'
import type { AuthUser } from '../services/auth'

const LEGACY_STORAGE_KEY = 'proview_jwt'

export const useAuthStore = defineStore('auth', () => {
  const jwt = ref('')
  const user = ref<AuthUser | null>(null)
  const isLoggedIn = computed(() => !!user.value)

  function clearLegacyJwt() {
    try {
      localStorage.removeItem(LEGACY_STORAGE_KEY)
    } catch {
      // Ignore storage failures.
    }
  }

  function clearUserReference() {
    jwt.value = ''
    user.value = null
    clearLegacyJwt()
  }

  async function tryRestore() {
    clearLegacyJwt()
    try {
      user.value = await fetchMe()
      jwt.value = ''
      return true
    } catch {
      clearUserReference()
      return false
    }
  }

  return { jwt, user, isLoggedIn, tryRestore }
})
