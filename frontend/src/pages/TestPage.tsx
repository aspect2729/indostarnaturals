import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { tokenStorage } from '../services/api'
import { useCart } from '../contexts/CartContext'

const TestPage = () => {
  const { user, isAuthenticated, isLoading } = useAuth()
  const { cart, addToCart } = useCart()
  const accessToken = tokenStorage.getAccessToken()

  const testQuickLogin = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/test/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: '+919876543210', role: 'consumer' })
      })
      const data = await response.json()
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      alert('Logged in successfully! Reloading...')
      location.reload()
    } catch (error: any) {
      alert(`Failed to login: ${error.message}`)
      console.error('Login error:', error)
    }
  }

  const testAddToCart = async () => {
    try {
      await addToCart({ product_id: 1, quantity: 1 })
      alert('Successfully added to cart!')
    } catch (error: any) {
      alert(`Failed to add to cart: ${error.message}`)
      console.error('Cart error:', error)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-2xl w-full bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Debug Test Page</h1>
        
        <div className="space-y-4">
          {/* Authentication Status */}
          <div>
            <h2 className="text-xl font-semibold mb-2">Authentication Status:</h2>
            <div className="bg-gray-100 p-4 rounded space-y-2">
              <p><strong>Is Authenticated:</strong> {isAuthenticated ? '✅ Yes' : '❌ No'}</p>
              <p><strong>Is Loading:</strong> {isLoading ? 'Yes' : 'No'}</p>
              <p><strong>User:</strong> {user ? `${user.email} (${user.role})` : 'Not logged in'}</p>
              <p><strong>Access Token:</strong> {accessToken ? `${accessToken.substring(0, 20)}...` : 'None'}</p>
            </div>
          </div>

          {/* Cart Status */}
          <div>
            <h2 className="text-xl font-semibold mb-2">Cart Status:</h2>
            <div className="bg-gray-100 p-4 rounded space-y-2">
              <p><strong>Cart Items:</strong> {cart?.items.length || 0}</p>
              <p><strong>Total:</strong> ₹{cart?.total_amount || 0}</p>
            </div>
          </div>

          {/* Test Actions */}
          <div>
            <h2 className="text-xl font-semibold mb-2">Test Actions:</h2>
            <div className="flex flex-col space-y-2">
              <button
                onClick={testQuickLogin}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                🚀 Quick Login (Consumer: +919876543210)
              </button>
              <button
                onClick={testAddToCart}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
              >
                Test Add to Cart (Product ID: 1)
              </button>
            </div>
          </div>

          {/* Navigation */}
          <div>
            <h2 className="text-xl font-semibold mb-2">Test Navigation:</h2>
            <div className="flex flex-col space-y-2">
              <Link to="/" className="text-blue-600 hover:underline">→ Go to Home (/)</Link>
              <Link to="/products" className="text-blue-600 hover:underline">→ Go to Products (/products)</Link>
              <Link to="/login" className="text-blue-600 hover:underline">→ Go to Login (/login)</Link>
              <Link to="/cart" className="text-blue-600 hover:underline">→ Go to Cart (/cart)</Link>
            </div>
          </div>

          <div className="mt-6">
            <h2 className="text-xl font-semibold mb-2">Current Location:</h2>
            <pre className="bg-gray-100 p-4 rounded text-xs">
              {window.location.href}
            </pre>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TestPage
