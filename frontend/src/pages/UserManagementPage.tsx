import React, { useState, useEffect } from 'react'
import { ownerUserService, UserResponse, DistributorStatus } from '../services/ownerUserService'
import { UserRole } from '../types/user'
import UserDetailView from '../components/UserDetailView'
import DistributorApprovalList from '../components/DistributorApprovalList'

const UserManagementPage: React.FC = () => {
  const [users, setUsers] = useState<UserResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedUser, setSelectedUser] = useState<UserResponse | null>(null)
  const [showDistributorApprovals, setShowDistributorApprovals] = useState(false)
  
  // Filters
  const [roleFilter, setRoleFilter] = useState<UserRole | ''>('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [distributorStatusFilter, setDistributorStatusFilter] = useState<DistributorStatus | ''>('')

  const fetchUsers = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const filters: any = {}
      
      if (roleFilter) filters.role_filter = roleFilter
      if (statusFilter !== '') filters.status_filter = statusFilter === 'active'
      if (distributorStatusFilter) filters.distributor_status_filter = distributorStatusFilter
      
      const data = await ownerUserService.getAllUsers(filters)
      setUsers(data)
    } catch (err) {
      setError('Failed to load users')
      console.error('Error fetching users:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [roleFilter, statusFilter, distributorStatusFilter])

  const handleUserUpdate = () => {
    // Refresh users after update
    fetchUsers()
    setSelectedUser(null)
  }

  const handleClearFilters = () => {
    setRoleFilter('')
    setStatusFilter('')
    setDistributorStatusFilter('')
  }

  const pendingDistributors = users.filter(
    (u) => u.role === UserRole.DISTRIBUTOR && u.distributor_status === DistributorStatus.PENDING
  )

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">User Management</h1>
        {pendingDistributors.length > 0 && (
          <button
            onClick={() => setShowDistributorApprovals(true)}
            className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 font-medium flex items-center gap-2"
          >
            <span className="bg-white text-yellow-600 rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">
              {pendingDistributors.length}
            </span>
            Pending Approvals
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Role Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              User Role
            </label>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value as UserRole | '')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">All Roles</option>
              <option value={UserRole.CONSUMER}>Consumer</option>
              <option value={UserRole.DISTRIBUTOR}>Distributor</option>
              <option value={UserRole.OWNER}>Owner</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Account Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          {/* Distributor Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Distributor Status
            </label>
            <select
              value={distributorStatusFilter}
              onChange={(e) => setDistributorStatusFilter(e.target.value as DistributorStatus | '')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">All Statuses</option>
              <option value={DistributorStatus.PENDING}>Pending</option>
              <option value={DistributorStatus.APPROVED}>Approved</option>
              <option value={DistributorStatus.REJECTED}>Rejected</option>
            </select>
          </div>
        </div>

        <div className="mt-4">
          <button
            onClick={handleClearFilters}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Users List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
          <p className="mt-4 text-gray-600">Loading users...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      ) : users.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No users found
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Verification
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{user.name}</div>
                      <div className="text-sm text-gray-500">ID: {user.id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{user.phone}</div>
                      {user.email && (
                        <div className="text-sm text-gray-500">{user.email}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 capitalize">
                        {user.role}
                      </span>
                      {user.distributor_status && (
                        <div className="mt-1">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
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
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        user.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex gap-2">
                        {user.is_email_verified && (
                          <span className="text-green-600" title="Email verified">
                            ✓ Email
                          </span>
                        )}
                        {user.is_phone_verified && (
                          <span className="text-green-600" title="Phone verified">
                            ✓ Phone
                          </span>
                        )}
                        {!user.is_email_verified && !user.is_phone_verified && (
                          <span className="text-gray-400">None</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => setSelectedUser(user)}
                        className="text-green-600 hover:text-green-900"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* User Detail Modal */}
      {selectedUser && (
        <UserDetailView
          user={selectedUser}
          onClose={() => setSelectedUser(null)}
          onUpdate={handleUserUpdate}
        />
      )}

      {/* Distributor Approval Modal */}
      {showDistributorApprovals && (
        <DistributorApprovalList
          distributors={pendingDistributors}
          onClose={() => setShowDistributorApprovals(false)}
          onUpdate={handleUserUpdate}
        />
      )}
    </div>
  )
}

export default UserManagementPage
