import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useProducts, useCategories } from '../hooks/useProducts'
import ProductCard from '../components/ProductCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { Product } from '../types/product'

const HomePage = () => {
  const { user, isAuthenticated } = useAuth()
  const { data: productsData, isLoading: productsLoading } = useProducts({ page_size: 6 })
  const { data: categoriesData, isLoading: categoriesLoading } = useCategories()

  // Category icon mapping
  const getCategoryIcon = (name: string) => {
    const lowerName = name.toLowerCase()
    if (lowerName.includes('jaggery') || lowerName.includes('sugar')) return '🍯'
    if (lowerName.includes('milk')) return '🥛'
    if (lowerName.includes('dairy') || lowerName.includes('butter') || lowerName.includes('ghee')) return '🧈'
    if (lowerName.includes('yogurt') || lowerName.includes('curd')) return '🥛'
    return '🌿'
  }

  const getCategoryGradient = (index: number) => {
    const gradients = [
      'from-amber-400 to-orange-500',
      'from-blue-400 to-cyan-500',
      'from-yellow-400 to-amber-500',
      'from-green-400 to-emerald-500',
      'from-purple-400 to-pink-500',
      'from-red-400 to-rose-500',
    ]
    return gradients[index % gradients.length]
  }

  return (
    <div className="bg-gradient-to-b from-neutral-50 to-white">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}></div>
        </div>
        
        <div className="container-custom relative py-24 md:py-32 lg:py-40">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-white/90 text-sm font-medium mb-8 animate-fade-in">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              100% Certified Organic Products
            </div>
            
            {/* Main Heading */}
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-display font-bold text-white mb-6 animate-slide-up">
              Pure, Organic,
              <span className="block text-transparent bg-gradient-to-r from-green-200 to-emerald-300 bg-clip-text">
                Natural Goodness
              </span>
            </h1>
            
            {/* Subheading */}
            <p className="text-lg md:text-xl lg:text-2xl text-white/90 mb-10 max-w-2xl mx-auto leading-relaxed animate-slide-up" style={{ animationDelay: '0.1s' }}>
              Premium organic jaggery, fresh milk, and artisanal dairy products delivered straight from farm to your doorstep
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-slide-up" style={{ animationDelay: '0.2s' }}>
              {isAuthenticated ? (
                <>
                  <Link to="/products" className="btn btn-lg bg-white text-primary-700 hover:bg-white/90 shadow-2xl">
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                    </svg>
                    Browse Products
                  </Link>
                  <Link to="/profile" className="btn btn-lg glass text-white border-2 border-white/30 hover:bg-white/10">
                    My Profile
                    <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/login" className="btn btn-lg bg-white text-primary-700 hover:bg-white/90 shadow-2xl">
                    Get Started
                    <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </Link>
                  <Link to="/products" className="btn btn-lg glass text-white border-2 border-white/30 hover:bg-white/10">
                    Browse Products
                  </Link>
                </>
              )}
            </div>
            
            {/* Trust Indicators */}
            <div className="mt-16 grid grid-cols-3 gap-8 max-w-2xl mx-auto">
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white mb-1">5000+</div>
                <div className="text-sm text-white/70">Happy Customers</div>
              </div>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white mb-1">100%</div>
                <div className="text-sm text-white/70">Organic Certified</div>
              </div>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white mb-1">24/7</div>
                <div className="text-sm text-white/70">Fresh Delivery</div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Wave Divider */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto">
            <path d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" fill="white"/>
          </svg>
        </div>
      </div>

      {/* Features Section */}
      <div className="container-custom py-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              icon: (
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ),
              title: '100% Organic',
              description: 'All our products are certified organic and naturally produced without harmful chemicals',
              gradient: 'from-green-500 to-emerald-600',
            },
            {
              icon: (
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              ),
              title: 'Lightning Fast Delivery',
              description: 'Daily fresh milk delivery and same-day shipping for all orders placed before noon',
              gradient: 'from-blue-500 to-cyan-600',
            },
            {
              icon: (
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ),
              title: 'Best Value',
              description: 'Competitive pricing with special bulk rates for distributors and subscription discounts',
              gradient: 'from-amber-500 to-orange-600',
            },
          ].map((feature, index) => (
            <div key={index} className="card card-hover p-8 text-center group">
              <div className={`w-16 h-16 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center mx-auto mb-6 text-white shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-display font-semibold text-neutral-900 mb-3">{feature.title}</h3>
              <p className="text-neutral-600 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Categories Section */}
      <div className="bg-gradient-to-b from-white to-neutral-50 py-20">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-neutral-900 mb-4">
              Shop by Category
            </h2>
            <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
              Explore our carefully curated selection of premium organic products
            </p>
          </div>
          
          {categoriesLoading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : categoriesData && categoriesData.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {categoriesData.slice(0, 6).map((category, index) => (
                <Link
                  key={category.id}
                  to={`/products?category=${category.id}`}
                  className="group relative overflow-hidden card p-8 text-center hover:shadow-soft-lg transition-all duration-300"
                >
                  {/* Gradient Background */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${getCategoryGradient(index)} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
                  
                  {/* Icon */}
                  <div className="relative text-7xl mb-6 transform group-hover:scale-110 transition-transform duration-300">
                    {getCategoryIcon(category.name)}
                  </div>
                  
                  {/* Content */}
                  <div className="relative">
                    <h3 className="text-2xl font-display font-semibold text-neutral-900 mb-3 group-hover:text-primary-600 transition-colors">
                      {category.name}
                    </h3>
                    <p className="text-neutral-600 mb-4">{category.description || 'Discover our premium organic products'}</p>
                    
                    {/* Arrow */}
                    <div className="inline-flex items-center text-primary-600 font-medium opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0 transition-all duration-300">
                      Explore
                      <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-24 h-24 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-12 h-12 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-neutral-900 mb-2">No categories yet</h3>
              <p className="text-neutral-600">Categories will appear here once added</p>
            </div>
          )}
        </div>
      </div>

      {/* Featured Products Section */}
      <div className="container-custom py-20">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-4">
          <div>
            <h2 className="text-4xl md:text-5xl font-display font-bold text-neutral-900 mb-2">
              Featured Products
            </h2>
            <p className="text-lg text-neutral-600">
              Handpicked favorites from our organic collection
            </p>
          </div>
          <Link
            to="/products"
            className="btn btn-secondary group"
          >
            View All Products
            <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </Link>
        </div>
        
        {productsLoading ? (
          <div className="flex justify-center py-20">
            <div className="text-center">
              <LoadingSpinner size="lg" />
              <p className="mt-4 text-neutral-600">Loading amazing products...</p>
            </div>
          </div>
        ) : productsData?.items && productsData.items.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {productsData.items.slice(0, 6).filter(product => product && product.id).map((product: Product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="w-24 h-24 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-12 h-12 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-neutral-900 mb-2">No products yet</h3>
            <p className="text-neutral-600 mb-6">Be the first to add products to your store!</p>
            {user?.role === 'owner' && (
              <Link to="/owner/products" className="btn btn-primary">
                Add Products
              </Link>
            )}
          </div>
        )}
      </div>

      {/* Subscription CTA Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 py-20">
        {/* Decorative Elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2"></div>
        
        <div className="container-custom relative">
          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              {/* Left Content */}
              <div className="text-white">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-sm font-medium mb-6">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  Most Popular
                </div>
                
                <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
                  Never Run Out of Fresh Milk
                </h2>
                <p className="text-xl text-white/90 mb-8 leading-relaxed">
                  Subscribe to our daily milk delivery service and enjoy fresh, organic milk at your doorstep every morning. Save up to 20% with our subscription plans!
                </p>
                
                {/* Benefits */}
                <ul className="space-y-4 mb-8">
                  {['Daily fresh delivery', 'Flexible scheduling', 'Cancel anytime', 'Save up to 20%'].map((benefit, index) => (
                    <li key={index} className="flex items-center gap-3">
                      <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <span className="text-lg">{benefit}</span>
                    </li>
                  ))}
                </ul>
                
                <div className="flex flex-col sm:flex-row gap-4">
                  <Link to="/products?subscription=true" className="btn btn-lg bg-white text-primary-700 hover:bg-white/90 shadow-2xl">
                    View Plans
                    <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </Link>
                  {isAuthenticated && (
                    <Link to="/subscriptions" className="btn btn-lg glass text-white border-2 border-white/30 hover:bg-white/10">
                      Manage Subscriptions
                    </Link>
                  )}
                </div>
              </div>
              
              {/* Right Image/Illustration */}
              <div className="relative">
                <div className="aspect-square bg-white/10 backdrop-blur-sm rounded-3xl p-8 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-8xl mb-6">🥛</div>
                    <div className="text-white/90 text-lg font-medium">Fresh Daily Delivery</div>
                  </div>
                </div>
                
                {/* Floating Badge */}
                <div className="absolute -top-4 -right-4 bg-accent-500 text-white px-6 py-3 rounded-2xl shadow-2xl transform rotate-6">
                  <div className="text-2xl font-bold">20%</div>
                  <div className="text-xs">OFF</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* User Welcome (if authenticated) */}
      {isAuthenticated && user && (
        <div className="container-custom py-12">
          <div className="card p-8 bg-gradient-to-br from-primary-50 to-white border-2 border-primary-100">
            <div className="flex items-start justify-between gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center text-white text-xl font-bold">
                    {((user.name || user.email) ?? 'U').charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h2 className="text-2xl font-display font-semibold text-neutral-900">
                      Welcome back, {user.name || user.email}!
                    </h2>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="badge badge-primary capitalize">{user.role}</span>
                    </div>
                  </div>
                </div>
                <p className="text-neutral-600 mb-6">
                  Ready to explore our fresh organic products? Your dashboard is just a click away.
                </p>
                <Link
                  to={user.role === 'owner' ? '/dashboard/owner' : user.role === 'distributor' ? '/dashboard/distributor' : '/dashboard/consumer'}
                  className="btn btn-primary"
                >
                  Go to Dashboard
                  <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </Link>
              </div>
              
              {/* Decorative Element */}
              <div className="hidden lg:block">
                <div className="w-32 h-32 bg-gradient-to-br from-primary-100 to-primary-200 rounded-2xl flex items-center justify-center text-5xl">
                  👋
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Trust Section */}
      <div className="bg-neutral-50 py-20">
        <div className="container-custom">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-neutral-900 mb-4">
              Why Choose Us
            </h2>
            <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
              Committed to delivering the finest organic products with exceptional service
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: (
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                ),
                title: 'Quality Assured',
                description: 'Every product is carefully tested and certified organic',
              },
              {
                icon: (
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                ),
                title: 'On-Time Delivery',
                description: 'Fresh products delivered right to your doorstep',
              },
              {
                icon: (
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                ),
                title: 'Customer Support',
                description: 'Dedicated team ready to help you anytime',
              },
              {
                icon: (
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                ),
                title: 'Best Prices',
                description: 'Competitive pricing with special bulk discounts',
              },
            ].map((item, index) => (
              <div key={index} className="card p-6 text-center hover:shadow-soft-lg transition-all duration-300">
                <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4 text-white">
                  {item.icon}
                </div>
                <h3 className="text-lg font-display font-semibold text-neutral-900 mb-2">{item.title}</h3>
                <p className="text-sm text-neutral-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage
