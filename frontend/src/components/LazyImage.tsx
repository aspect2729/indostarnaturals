import { useState, useEffect, useRef, ImgHTMLAttributes } from 'react'

interface LazyImageProps extends ImgHTMLAttributes<HTMLImageElement> {
  src: string
  alt: string
  placeholder?: string
  className?: string
}

/**
 * LazyImage component with intersection observer for lazy loading
 * Implements responsive images with srcset for performance optimization
 */
const LazyImage = ({
  src,
  alt,
  placeholder = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect fill="%23f3f4f6" width="400" height="300"/%3E%3C/svg%3E',
  className = '',
  ...props
}: LazyImageProps) => {
  const [imageSrc, setImageSrc] = useState(placeholder)
  const [isLoaded, setIsLoaded] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    // Check if IntersectionObserver is supported
    if (!('IntersectionObserver' in window)) {
      // Fallback: load image immediately
      setImageSrc(src)
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setImageSrc(src)
            if (imgRef.current) {
              observer.unobserve(imgRef.current)
            }
          }
        })
      },
      {
        rootMargin: '50px', // Start loading 50px before image enters viewport
        threshold: 0.01,
      }
    )

    if (imgRef.current) {
      observer.observe(imgRef.current)
    }

    return () => {
      if (imgRef.current) {
        observer.unobserve(imgRef.current)
      }
    }
  }, [src])

  const handleLoad = () => {
    setIsLoaded(true)
  }

  // Generate responsive image URLs (assuming CDN supports size parameters)
  const generateSrcSet = (baseUrl: string): string => {
    // If the URL contains query parameters, append size params
    // Otherwise, this is a simple implementation that could be enhanced
    // based on your CDN's capabilities
    if (baseUrl.includes('?')) {
      return `${baseUrl}&w=400 400w, ${baseUrl}&w=800 800w, ${baseUrl}&w=1200 1200w`
    }
    return `${baseUrl}?w=400 400w, ${baseUrl}?w=800 800w, ${baseUrl}?w=1200 1200w`
  }

  return (
    <img
      ref={imgRef}
      src={imageSrc}
      srcSet={imageSrc !== placeholder ? generateSrcSet(imageSrc) : undefined}
      sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
      alt={alt}
      onLoad={handleLoad}
      className={`${className} ${
        isLoaded ? 'opacity-100' : 'opacity-0'
      } transition-opacity duration-300`}
      loading="lazy"
      {...props}
    />
  )
}

export default LazyImage
