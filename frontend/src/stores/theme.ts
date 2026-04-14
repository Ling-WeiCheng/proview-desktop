import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(
    localStorage.theme === 'dark' ||
    (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)
  )

  function apply() {
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  /** View Transitions API 圆形扩散切换 */
  async function toggle(btnEl?: HTMLElement | null) {
    const nextDark = !isDark.value

    // 简单降级：无按钮元素 / 不支持 API / 用户偏好减少动画
    const prefersReduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    const canTransition = !prefersReduce
      && typeof (document as any).startViewTransition === 'function'
      && btnEl instanceof HTMLElement

    if (!canTransition) {
      isDark.value = nextDark
      localStorage.theme = nextDark ? 'dark' : 'light'
      apply()
      return
    }

    // 计算圆心和半径
    const rect = btnEl!.getBoundingClientRect()
    const x = rect.left + rect.width / 2
    const y = rect.top + rect.height / 2
    const endRadius = Math.hypot(
      Math.max(x, window.innerWidth - x),
      Math.max(y, window.innerHeight - y)
    )

    // 启动 View Transition
    const transition = (document as any).startViewTransition(() => {
      isDark.value = nextDark
      localStorage.theme = nextDark ? 'dark' : 'light'
      apply()
    })

    try {
      await transition.ready

      // 切到暗色：新视图从按钮位置圆形展开
      // 切到亮色：旧视图从全屏圆形收缩到按钮位置
      const clipPathFrames = nextDark
        ? [`circle(0px at ${x}px ${y}px)`, `circle(${endRadius}px at ${x}px ${y}px)`]
        : [`circle(${endRadius}px at ${x}px ${y}px)`, `circle(0px at ${x}px ${y}px)`]

      const pseudo = nextDark
        ? '::view-transition-new(root)'
        : '::view-transition-old(root)'

      document.documentElement.animate(
        { clipPath: clipPathFrames },
        {
          duration: 800,
          easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
          pseudoElement: pseudo,
        }
      )

      await transition.finished
    } catch {
      // transition 被中断或不支持，状态已在回调中更新
    }
  }

  apply()

  return { isDark, toggle, apply }
})
