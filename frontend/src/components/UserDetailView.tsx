import React, { useState } from 'react'
import { UserResponse, DistributorStatus } from '../services/ownerUserService'
import RoleUpdater from './RoleUpdater'

interface UserDetailViewProps {
  user: UserResponse
  onClose: () => void
  onUpdate: () => void
}

const UserDetailView: React.FC<UserDetailViewProps> = ({ user, onClose, onUpdate }) => {
  const [showRoleUpdater, setShowRoleUpdater] = useState(false)

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">User Details</h2>
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

        <div className="p-6">
          {/* Basic Information */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Basic Information</h3>
            <div className="bg-gray-50 rounded-lg p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">User ID</p>
                <p className="font-medium">{user.id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Name</p>
                <p className="font-medium">{user.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Phone</p>
                <p className="font-medium">{user.phone}</p>
              </div>
              {user.email && (
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="font-medium">{user.email}</p>
                </div>
              )}
            </div>
          </div>

          {/* Role and Status */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Role and Status</h3>
            <div className="bg-gray-50 rounded-lg p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600 mb-2">Role</p>
                <span className="inline-block px-3 py-1 text-sm font-medium rounded-full bg-blue-100 text-blue-800 capitalize">
                  {user.role}
                </span>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-2">Account Status</p>
                <span className={`inline-block px-3 py-1 text-sm font-medium rounded-full ${
                  user.is_active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              {user.distributor_status && (
                <div>
                  <p className="text-sm text-gray-600 mb-2">Distributor Status</p>
                  <span className={`inline-block px-3 py-1 text-sm font-medium rounded-full ${
                    user.distributor_status === DistributorStatus.PENDING
                      ? 'bg-yellow-100 text-yellow-800'
                      : user.distributor_status === DistributorStatus.APPROVED
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {user.distributor_status}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Verification Status */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Verification Status</h3>
            <div className="bg-gray-50 rounded-lg p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Email Verified</span>
                <span className={`flex items-center gap-2 ${
                  user.is_email_verified ? 'text-green-600' : 'text-gray-400'
                }`}>
                  {user.is_email_verified ? (
                    <>
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      Verified
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                      Not Verified
                    </>
                  )}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Phone Verified</span>
                <span className={`flex items-center gap-2 ${
                  user.is_phone_verified ? 'text-green-600' : 'text-gray-400'
                }`}>
                  {user.is_phone_verified ? (
                    <>
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      Verified
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                      Not Verified
                    </>
                  )}
                </span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={() => setShowRoleUpdater(true)}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium"
            >
              Update Role
            </button>
          </div>
        </div>

        {/* Role Updater Modal */}
        {showRoleUpdater && (
          <RoleUpdater
            user={user}
            onClose={() => setShowRoleUpdater(false)}
            onUpdate={() => {
              setShowRoleUpdater(false)
              onUpdate()
            }}
          />
        )}
      </div>
    </div>
  )
}

export default UserDetailView
