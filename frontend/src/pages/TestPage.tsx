import { Link } from 'react-router-dom'

const TestPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-2xl w-full bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Routing Test Page</h1>
        
        <div className="space-y-4">
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
            <pre className="bg-gray-100 p-4 rounded">
              {window.location.href}
            </pre>
          </div>

          <div className="mt-6">
            <button
              onClick={() => {
                console.log('Button clicked!')
                alert('Button works!')
              }}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Test Button Click
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TestPage
