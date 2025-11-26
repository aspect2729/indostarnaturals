/**
 * Service Worker Registration
 * Registers the service worker for offline caching and performance optimization
 */

export function register() {
  if ('serviceWorker' in navigator && import.meta.env.PROD) {
    window.addEventListener('load', () => {
      const swUrl = `/sw.js`

      navigator.serviceWorker
        .register(swUrl)
        .then((registration) => {
          if (import.meta.env.DEV) {
            console.log('Service Worker registered:', registration)
          }

          // Check for updates periodically
          setInterval(() => {
            registration.update()
          }, 60 * 60 * 1000) // Check every hour
        })
        .catch((error) => {
          console.error('Service Worker registration failed:', error)
        })
    })
  }
}

export function unregister() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready
      .then((registration) => {
        registration.unregister()
      })
      .catch((error) => {
        console.error('Service Worker unregistration failed:', error)
      })
  }
}
