import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './contexts/AuthContext'
import { CartProvider } from './contexts/CartContext'
import { ToastProvider } from './components/ToastContainer'
import ErrorBoundary from './components/ErrorBoundary'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import RoleBasedRoute from './components/RoleBasedRoute'
import LoadingSpinner from './components/LoadingSpinner'
import { UserRole } from './types/auth'



// Lazy load pages for code splitting
const HomePage = lazy(() => import('./pages/HomePage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const UserProfilePage = lazy(() => import('./pages/UserProfilePage'))
const ProductCatalogPage = lazy(() => import('./pages/ProductCatalogPage'))
const ProductDetailPage = lazy(() => import('./pages/ProductDetailPage'))
const CartPage = lazy(() => import('./pages/CartPage'))
const CheckoutPage = lazy(() => import('./pages/CheckoutPage'))
const SubscriptionManagementPage = lazy(() => import('./pages/SubscriptionManagementPage'))
const ConsumerDashboardPage = lazy(() => import('./pages/ConsumerDashboardPage'))
const DistributorDashboardPage = lazy(() => import('./pages/DistributorDashboardPage'))
const OwnerDashboardPage = lazy(() => import('./pages/OwnerDashboardPage'))
const ProductManagementPage = lazy(() => import('./pages/ProductManagementPage'))
const CategoryManagementPage = lazy(() => import('./pages/CategoryManagementPage'))
const OrderManagementPage = lazy(() => import('./pages/OrderManagementPage'))
const UserManagementPage = lazy(() => import('./pages/UserManagementPage'))
const InventoryPage = lazy(() => import('./pages/InventoryPage'))
const AuditLogPage = lazy(() => import('./pages/AuditLogPage'))
const TestPage = lazy(() => import('./pages/TestPage'))

// Loading fallback component
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center">
    <LoadingSpinner size="lg" />
  </div>
)

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <CartProvider>
            <ToastProvider>
              <BrowserRouter>
                <Layout>
                  <Suspense fallback={<PageLoader />}>
                    <Routes>
                    {/* Public routes */}
                    <Route path="/" element={<HomePage />} />
                    <Route path="/home" element={<HomePage />} />
                    <Route path="/test" element={<TestPage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/products" element={<ProductCatalogPage />} />
                    <Route path="/products/:id" element={<ProductDetailPage />} />

                    {/* Protected routes - require authentication */}
                    <Route
                      path="/cart"
                      element={
                        <ProtectedRoute>
                          <CartPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/checkout"
                      element={
                        <ProtectedRoute>
                          <CheckoutPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/profile"
                      element={
                        <ProtectedRoute>
                          <UserProfilePage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/subscriptions"
                      element={
                        <ProtectedRoute>
                          <SubscriptionManagementPage />
                        </ProtectedRoute>
                      }
                    />

                    {/* Consumer dashboard */}
                    <Route
                      path="/dashboard/consumer"
                      element={
                        <RoleBasedRoute allowedRoles={[UserRole.CONSUMER]}>
                          <ConsumerDashboardPage />
                        </RoleBasedRoute>
                      }
                    />

                    {/* Distributor dashboard */}
                    <Route
                      path="/dashboard/distributor"
                      element={
                        <RoleBasedRoute allowedRoles={[UserRole.DISTRIBUTOR, UserRole.OWNER]}>
                          <DistributorDashboardPage />
                        </RoleBasedRoute>
                      }
                    />

                    {/* Owner dashboard and management pages */}
                    <Route
                      path="/dashboard/owner"
                      element={
                        <RoleBasedRoute allowedRoles={[UserRole.OWNER]}>
                          <OwnerDashboardPage />
                        </RoleBasedRoute>
                      }
                    />
                    <Route
                      path="/owner/products"
                      element={
                        <RoleBasedRoute allowedRoles={[UserRole.OWNER]}>
                          <ProductManagementPage />
                        </RoleBasedRoute>
                      }
                    />
                    <Route
                      path="/owner/categories"
                      element={
                        <RoleBasedRoute allowedRoles={[UserRole.OWNER]}>
                          <CategoryManagementPage />
                        </RoleBasedRoute>
                      }
                    />
                    <Route
                      path="/owner/orders"
                      element={
                        <RoleBasedRoute allowedRoles={[UserRole.OWNER]}>
                          <OrderManagementPage />
                        </RoleBasedRoute>
                      }
                    />
                    <Route
                      path="/owner/users"
                      element={
                        <RoleBasedRoute allowedRoles={[UserRole.OWNER]}>
                          <UserManagementPage />
                        </RoleBasedRoute>
                      }
                    />
                    <Route
                      path="/owner/inventory"
                      element={
                        <RoleBasedRoute allowedRoles={[UserRole.OWNER]}>
                          <InventoryPage />
                        </RoleBasedRoute>
                      }
                    />
                    <Route
                      path="/owner/audit-logs"
                      element={
                        <RoleBasedRoute allowedRoles={[UserRole.OWNER]}>
                          <AuditLogPage />
                        </RoleBasedRoute>
                      }
                    />

                    {/* 404 Not Found */}
                    <Route
                      path="*"
                      element={
                        <div className="min-h-screen flex items-center justify-center">
                          <div className="text-center">
                            <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
                            <p className="text-xl text-gray-600 mb-8">Page not found</p>
                            <a
                              href="/"
                              className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 transition-colors"
                            >
                              Go Home
                            </a>
                          </div>
                        </div>
                      }
                    />
                    </Routes>
                  </Suspense>
                </Layout>
              </BrowserRouter>
            </ToastProvider>
          </CartProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
