import React, { useState } from 'react'
import { UserResponse, ownerUserService } from '../services/ownerUserService'
import { UserRole } from '../types/user'

interface RoleUpdaterProps {
  user: UserResponse
  onClose: () => void
  onUpdate: () => void
}

const RoleUpdater: React.FC<RoleUpdaterProps> = ({ user, onClose, onUpdate }) => {
  const [selectedRole, setSelectedRole] = useState<UserRole>(user.role)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (selectedRole === user.role) {
      setError('Please select a different role')
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      await ownerUserService.updateUserRole(user.id, { role: selectedRole })
      onUpdate()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update user role')
      console.error('Error updating user role:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h3 className="text-xl font-bold text-gray-900">Update User Role</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Close"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6">
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">
              User: <span className="font-medium text-gray-900">{user.name}</span>
            </p>
            <p className="text-sm text-gray-600 mb-4">
              Current Role: <span className="font-medium text-gray-900 capitalize">{user.role}</span>
            </p>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              New Role
            </label>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value as UserRole)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            >
              <option value={UserRole.CONSUMER}>Consumer</option>
              <option value={UserRole.DISTRIBUTOR}>Distributor</option>
              <option value={UserRole.OWNER}>Owner</option>
            </select>
            <p className="mt-2 text-sm text-gray-500">
              Changing a user's role will affect their access permissions and pricing.
            </p>
          </div>

          {selectedRole === UserRole.DISTRIBUTOR && user.role !== UserRole.DISTRIBUTOR && (
            <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex">
                <svg className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <div>
                  <h4 className="text-sm font-medium text-blue-800 mb-1">Note</h4>
                  <p className="text-sm text-blue-700">
                    Changing to distributor role will grant access to wholesale pricing and distributor features.
                  </p>
                </div>
              </div>
            </div>
          )}

          {selectedRole === UserRole.OWNER && user.role !== UserRole.OWNER && (
            <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex">
                <svg className="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div>
                  <h4 className="text-sm font-medium text-yellow-800 mb-1">Warning</h4>
                  <p className="text-sm text-yellow-700">
                    Changing to owner role will grant full administrative access to the system.
                  </p>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 font-medium"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || selectedRole === user.role}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Updating...' : 'Update Role'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RoleUpdater
