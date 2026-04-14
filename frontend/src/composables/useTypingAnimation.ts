import { ref, onUnmounted } from 'vue'

export function useTypingAnimation(speed = 25) {
  const displayedText = ref('')
  const isComplete = ref(true)
  let interval: ReturnType<typeof setInterval> | null = null

  function start(fullText: string): Promise<void> {
    return new Promise((resolve) => {
      stop()
      displayedText.value = ''
      isComplete.value = false
      let i = 0
      interval = setInterval(() => {
        displayedText.value += fullText.charAt(i)
        i++
        if (i >= fullText.length) {
          stop()
          isComplete.value = true
          resolve()
        }
      }, speed)
    })
  }

  function stop() {
    if (interval) {
      clearInterval(interval)
      interval = null
    }
  }

  onUnmounted(stop)

  return { displayedText, isComplete, start, stop }
}
