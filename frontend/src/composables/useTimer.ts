import { ref, computed, onUnmounted } from 'vue'

export function useTimer() {
  const seconds = ref(0)
  let interval: ReturnType<typeof setInterval> | null = null

  const formatted = computed(() => {
    const m = Math.floor(seconds.value / 60).toString().padStart(2, '0')
    const s = (seconds.value % 60).toString().padStart(2, '0')
    return `${m}:${s}`
  })

  function start() {
    stop()
    seconds.value = 0
    interval = setInterval(() => seconds.value++, 1000)
  }

  function stop() {
    if (interval) {
      clearInterval(interval)
      interval = null
    }
  }

  function reset() {
    stop()
    seconds.value = 0
  }

  onUnmounted(stop)

  return { seconds, formatted, start, stop, reset }
}
