import React, { useState } from 'react'
import { UserResponse, ownerUserService } from '../services/ownerUserService'
import { UserRole } from '../types/user'

interface DistributorApprovalListProps {
  distributors: UserResponse[]
  onClose: () => void
  onUpdate: () => void
}

const DistributorApprovalList: React.FC<DistributorApprovalListProps> = ({
  distributors,
  onClose,
  onUpdate,
}) => {
  const [processing, setProcessing] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleApprove = async (distributor: UserResponse) => {
    try {
      setProcessing(distributor.id)
      setError(null)
      
      // Approve by ensuring role is distributor (backend handles approval logic)
      await ownerUserService.updateUserRole(distributor.id, { role: UserRole.DISTRIBUTOR })
      onUpdate()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to approve distributor')
      console.error('Error approving distributor:', err)
    } finally {
      setProcessing(null)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">
            Pending Distributor Approvals ({distributors.length})
          </h2>
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
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {distributors.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No pending distributor approvals
            </div>
          ) : (
            <div className="space-y-4">
              {distributors.map((distributor) => (
                <div
                  key={distributor.id}
                  className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {distributor.name}
                        </h3>
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800">
                          Pending Approval
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                        <div>
                          <span className="text-gray-600">User ID:</span>
                          <span className="ml-2 font-medium text-gray-900">{distributor.id}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Phone:</span>
                          <span className="ml-2 font-medium text-gray-900">{distributor.phone}</span>
                        </div>
                        {distributor.email && (
                          <div>
                            <span className="text-gray-600">Email:</span>
                            <span className="ml-2 font-medium text-gray-900">{distributor.email}</span>
                          </div>
                        )}
                        <div>
                          <span className="text-gray-600">Verification:</span>
                          <span className="ml-2">
                            {distributor.is_email_verified && (
                              <span className="text-green-600 text-xs mr-2">✓ Email</span>
                            )}
                            {distributor.is_phone_verified && (
                              <span className="text-green-600 text-xs">✓ Phone</span>
                            )}
                            {!distributor.is_email_verified && !distributor.is_phone_verified && (
                              <span className="text-gray-400 text-xs">None</span>
                            )}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="ml-4">
                      <button
                        onClick={() => handleApprove(distributor)}
                        disabled={processing === distributor.id}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {processing === distributor.id ? 'Approving...' : 'Approve'}
                      </button>
                    </div>
                  </div>

                  <div className="mt-3 bg-blue-50 border border-blue-200 rounded p-3">
                    <p className="text-sm text-blue-700">
                      <strong>Note:</strong> Approving this user will grant them access to distributor pricing
                      and features. They will be able to purchase products at wholesale prices.
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DistributorApprovalList
