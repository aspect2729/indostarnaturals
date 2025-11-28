import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useCart } from '../hooks/useCart'
import SearchBar from './SearchBar'
import { UserRole } from '../types/auth'

const Header = () => {
  const { user, logout } = useAuth()
  const { cart } = useCart()
  const navigate = useNavigate()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)

  const cartItemCount = cart?.items?.reduce((sum, item) => sum + item.quantity, 0) || 0

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const handleSearch = (query: string) => {
    // Only navigate if there's a search query
    if (query.trim()) {
      navigate(`/products?search=${encodeURIComponent(query)}`)
    }
    // Don't navigate if query is empty - let user stay on current page
  }

  const getDashboardLink = () => {
    if (!user) return '/login'
    switch (user.role) {
      case UserRole.OWNER:
        return '/dashboard/owner'
      case UserRole.DISTRIBUTOR:
        return '/dashboard/distributor'
      case UserRole.CONSUMER:
        return '/dashboard/consumer'
      default:
        return '/profile'
    }
  }

  return (
    <header 
      className={`sticky top-0 z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-white/95 backdrop-blur-lg shadow-soft' 
          : 'bg-white'
      }`}
      role="banner"
    >
      {/* Skip to main content link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 focus:z-50 focus:p-4 focus:bg-primary-600 focus:text-white focus:rounded-br-lg"
      >
        Skip to main content
      </a>
      
      <div className="container-custom">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link 
            to="/" 
            className="flex items-center gap-3 group" 
            aria-label="IndoStar Naturals Home"
          >
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-lg group-hover:shadow-xl transition-shadow">
              IN
            </div>
            <div className="hidden sm:block">
              <div className="text-xl font-display font-bold text-neutral-900 group-hover:text-primary-600 transition-colors">
                IndoStar Naturals
              </div>
              <div className="text-xs text-neutral-500 -mt-1">Pure & Organic</div>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-8" aria-label="Main navigation">
            <Link
              to="/products"
              className="text-neutral-700 hover:text-primary-600 font-medium transition-colors relative group"
            >
              Products
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary-600 group-hover:w-full transition-all duration-300"></span>
            </Link>
            {user?.role === UserRole.OWNER && (
              <>
                <Link
                  to="/owner/products"
                  className="text-neutral-700 hover:text-primary-600 font-medium transition-colors relative group"
                >
                  Manage Products
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary-600 group-hover:w-full transition-all duration-300"></span>
                </Link>
                <Link
                  to="/owner/orders"
                  className="text-neutral-700 hover:text-primary-600 font-medium transition-colors relative group"
                >
                  Orders
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary-600 group-hover:w-full transition-all duration-300"></span>
                </Link>
                <Link
                  to="/owner/users"
                  className="text-neutral-700 hover:text-primary-600 font-medium transition-colors relative group"
                >
                  Users
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary-600 group-hover:w-full transition-all duration-300"></span>
                </Link>
              </>
            )}
          </nav>

          {/* Search Bar - Desktop */}
          <div className="hidden md:block flex-1 max-w-md mx-6">
            <SearchBar onSearch={handleSearch} />
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center gap-4">
            {/* Cart Icon */}
            <Link
              to="/cart"
              className="relative p-2 text-neutral-700 hover:text-primary-600 transition-colors rounded-lg hover:bg-neutral-100"
              aria-label={`Shopping cart with ${cartItemCount} items`}
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
                />
              </svg>
              {cartItemCount > 0 && (
                <span 
                  className="absolute top-0 right-0 w-5 h-5 bg-gradient-to-br from-primary-500 to-primary-600 text-white text-xs rounded-full flex items-center justify-center font-semibold shadow-lg"
                  aria-hidden="true"
                >
                  {cartItemCount > 9 ? '9+' : cartItemCount}
                </span>
              )}
            </Link>

            {/* User Menu */}
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center gap-2 p-2 text-neutral-700 hover:text-primary-600 transition-colors rounded-lg hover:bg-neutral-100"
                  aria-expanded={isUserMenuOpen}
                  aria-haspopup="true"
                  aria-label="User menu"
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center text-white font-semibold text-sm">
                    {((user.name || user.email) ?? 'U').charAt(0).toUpperCase()}
                  </div>
                  <span className="hidden md:inline font-medium">{user.name || user.email}</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Dropdown Menu */}
                {isUserMenuOpen && (
                  <>
                    <div 
                      className="fixed inset-0 z-40"
                      onClick={() => setIsUserMenuOpen(false)}
                    ></div>
                    <div 
                      className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-soft-lg py-2 z-50 border border-neutral-100"
                      role="menu"
                      aria-orientation="vertical"
                    >
                      <div className="px-4 py-3 border-b border-neutral-100">
                        <p className="text-sm font-semibold text-neutral-900">{user.name || user.email}</p>
                        <p className="text-xs text-neutral-500 capitalize">{user.role}</p>
                      </div>
                      
                      <Link
                        to={getDashboardLink()}
                        className="flex items-center gap-3 px-4 py-2.5 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors"
                        onClick={() => setIsUserMenuOpen(false)}
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                        </svg>
                        Dashboard
                      </Link>
                      
                      <Link
                        to="/profile"
                        className="flex items-center gap-3 px-4 py-2.5 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors"
                        onClick={() => setIsUserMenuOpen(false)}
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        Profile
                      </Link>
                      
                      {user.role !== UserRole.OWNER && (
                        <Link
                          to="/subscriptions"
                          className="flex items-center gap-3 px-4 py-2.5 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors"
                          onClick={() => setIsUserMenuOpen(false)}
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                          Subscriptions
                        </Link>
                      )}
                      
                      <div className="border-t border-neutral-100 mt-2 pt-2">
                        <button
                          onClick={() => {
                            setIsUserMenuOpen(false)
                            handleLogout()
                          }}
                          className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                          </svg>
                          Logout
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <Link
                to="/login"
                className="btn btn-primary btn-sm"
              >
                Login
              </Link>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="lg:hidden p-2 text-neutral-700 hover:text-primary-600 transition-colors rounded-lg hover:bg-neutral-100"
              aria-expanded={isMobileMenuOpen}
              aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                {isMobileMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="lg:hidden py-6 border-t border-neutral-100 animate-slide-down" role="navigation" aria-label="Mobile navigation">
            {/* Mobile Search */}
            <div className="mb-6">
              <SearchBar onSearch={handleSearch} />
            </div>

            {/* Mobile Navigation Links */}
            <nav className="flex flex-col space-y-1">
              <Link
                to="/products"
                className="px-4 py-3 text-neutral-700 hover:text-primary-600 hover:bg-neutral-50 rounded-lg transition-colors font-medium"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Products
              </Link>
              {user?.role === UserRole.OWNER && (
                <>
                  <Link
                    to="/owner/products"
                    className="px-4 py-3 text-neutral-700 hover:text-primary-600 hover:bg-neutral-50 rounded-lg transition-colors font-medium"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Manage Products
                  </Link>
                  <Link
                    to="/owner/orders"
                    className="px-4 py-3 text-neutral-700 hover:text-primary-600 hover:bg-neutral-50 rounded-lg transition-colors font-medium"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Orders
                  </Link>
                  <Link
                    to="/owner/users"
                    className="px-4 py-3 text-neutral-700 hover:text-primary-600 hover:bg-neutral-50 rounded-lg transition-colors font-medium"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Users
                  </Link>
                </>
              )}
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header
