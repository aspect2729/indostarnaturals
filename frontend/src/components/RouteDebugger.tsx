import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

const RouteDebugger = () => {
  const location = useLocation()

  useEffect(() => {
    console.log('=== ROUTE DEBUG ===')
    console.log('Current pathname:', location.pathname)
    console.log('Current search:', location.search)
    console.log('Current hash:', location.hash)
    console.log('Location state:', location.state)
    console.log('==================')
  }, [location])

  return null
}

export default RouteDebugger
