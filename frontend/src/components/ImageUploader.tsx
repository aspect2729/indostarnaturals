import React, { useState, useRef } from 'react'

interface ImageUploadItem {
  id?: number
  file?: File
  url: string
  altText: string
  displayOrder: number
  uploading?: boolean
  progress?: number
  error?: string
}

interface ImageUploaderProps {
  images: ImageUploadItem[]
  onImagesChange: (images: ImageUploadItem[]) => void
  maxImages?: number
  maxSizeMB?: number
}

const ImageUploader: React.FC<ImageUploaderProps> = ({
  images,
  onImagesChange,
  maxImages = 10,
  maxSizeMB = 5,
}) => {
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const validateFile = (file: File): string | null => {
    // Check file type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp']
    if (!validTypes.includes(file.type)) {
      return 'Invalid file type. Only JPEG, PNG, and WebP are allowed.'
    }

    // Check file size
    const maxSizeBytes = maxSizeMB * 1024 * 1024
    if (file.size > maxSizeBytes) {
      return `File size exceeds ${maxSizeMB}MB limit.`
    }

    return null
  }

  const handleFiles = (files: FileList | null) => {
    if (!files) return

    const newImages: ImageUploadItem[] = []
    const errors: string[] = []

    Array.from(files).forEach((file) => {
      const error = validateFile(file)
      if (error) {
        errors.push(`${file.name}: ${error}`)
        return
      }

      if (images.length + newImages.length >= maxImages) {
        errors.push(`Maximum ${maxImages} images allowed.`)
        return
      }

      const url = URL.createObjectURL(file)
      newImages.push({
        file,
        url,
        altText: file.name.replace(/\.[^/.]+$/, ''), // Remove extension
        displayOrder: images.length + newImages.length,
        uploading: false,
      })
    })

    if (errors.length > 0) {
      alert(errors.join('\n'))
    }

    if (newImages.length > 0) {
      onImagesChange([...images, ...newImages])
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    handleFiles(e.dataTransfer.files)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    handleFiles(e.target.files)
  }

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  const handleRemove = (index: number) => {
    const newImages = [...images]
    const removed = newImages.splice(index, 1)[0]
    
    // Revoke object URL if it's a local file
    if (removed.file) {
      URL.revokeObjectURL(removed.url)
    }

    // Update display orders
    newImages.forEach((img, idx) => {
      img.displayOrder = idx
    })

    onImagesChange(newImages)
  }

  const handleAltTextChange = (index: number, altText: string) => {
    const newImages = [...images]
    newImages[index].altText = altText
    onImagesChange(newImages)
  }

  const handleReorder = (fromIndex: number, toIndex: number) => {
    if (toIndex < 0 || toIndex >= images.length) return

    const newImages = [...images]
    const [moved] = newImages.splice(fromIndex, 1)
    newImages.splice(toIndex, 0, moved)

    // Update display orders
    newImages.forEach((img, idx) => {
      img.displayOrder = idx
    })

    onImagesChange(newImages)
  }

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-green-500 bg-green-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/jpeg,image/png,image/webp"
          onChange={handleChange}
          className="hidden"
        />
        
        <div className="space-y-2">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <div className="text-sm text-gray-600">
            <button
              type="button"
              onClick={handleButtonClick}
              className="font-medium text-green-600 hover:text-green-500 focus:outline-none focus:underline"
            >
              Upload images
            </button>
            {' or drag and drop'}
          </div>
          <p className="text-xs text-gray-500">
            JPEG, PNG, WebP up to {maxSizeMB}MB (max {maxImages} images)
          </p>
        </div>
      </div>

      {/* Image preview grid */}
      {images.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {images.map((image, index) => (
            <div
              key={index}
              className="relative group border rounded-lg overflow-hidden bg-gray-50"
            >
              {/* Image */}
              <div className="aspect-square">
                <img
                  src={image.url}
                  alt={image.altText}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Upload progress */}
              {image.uploading && (
                <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                  <div className="text-white text-center">
                    <div className="text-sm font-medium">Uploading...</div>
                    <div className="text-xs">{image.progress}%</div>
                  </div>
                </div>
              )}

              {/* Error */}
              {image.error && (
                <div className="absolute inset-0 bg-red-500 bg-opacity-90 flex items-center justify-center p-2">
                  <div className="text-white text-xs text-center">{image.error}</div>
                </div>
              )}

              {/* Controls */}
              <div className="p-2 space-y-2">
                {/* Alt text input */}
                <input
                  type="text"
                  value={image.altText}
                  onChange={(e) => handleAltTextChange(index, e.target.value)}
                  placeholder="Alt text"
                  className="w-full px-2 py-1 text-xs border rounded focus:outline-none focus:ring-1 focus:ring-green-500"
                  disabled={image.uploading}
                />

                {/* Action buttons */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1">
                    {/* Move up */}
                    <button
                      type="button"
                      onClick={() => handleReorder(index, index - 1)}
                      disabled={index === 0 || image.uploading}
                      className="p-1 text-gray-600 hover:text-gray-900 disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Move up"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                      </svg>
                    </button>

                    {/* Move down */}
                    <button
                      type="button"
                      onClick={() => handleReorder(index, index + 1)}
                      disabled={index === images.length - 1 || image.uploading}
                      className="p-1 text-gray-600 hover:text-gray-900 disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Move down"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>

                    <span className="text-xs text-gray-500">#{index + 1}</span>
                  </div>

                  {/* Remove button */}
                  <button
                    type="button"
                    onClick={() => handleRemove(index)}
                    disabled={image.uploading}
                    className="p-1 text-red-600 hover:text-red-900 disabled:opacity-30 disabled:cursor-not-allowed"
                    title="Remove"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ImageUploader
