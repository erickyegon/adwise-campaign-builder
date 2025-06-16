import React, { useState } from 'react';
import {
  Users as UsersIcon,
  Plus,
  Search,
  Filter,
  MoreVertical,
  Edit,
  Trash2,
  Mail,
  Phone,
  Calendar,
  Shield,
  UserCheck,
  UserX,
  Download,
  Upload,
} from 'lucide-react';

const users = [
  {
    id: 1,
    name: 'Admin User',
    email: 'admin@adwise.ai',
    role: 'Administrator',
    status: 'Active',
    lastLogin: '2024-01-15',
    campaigns: 12,
    avatar: 'AU',
  },
  {
    id: 2,
    name: 'Sarah Johnson',
    email: 'sarah.johnson@company.com',
    role: 'Campaign Manager',
    status: 'Active',
    lastLogin: '2024-01-14',
    campaigns: 8,
    avatar: 'SJ',
  },
  {
    id: 3,
    name: 'Mike Chen',
    email: 'mike.chen@company.com',
    role: 'Content Creator',
    status: 'Active',
    lastLogin: '2024-01-13',
    campaigns: 5,
    avatar: 'MC',
  },
  {
    id: 4,
    name: 'Emily Davis',
    email: 'emily.davis@company.com',
    role: 'Analyst',
    status: 'Inactive',
    lastLogin: '2024-01-10',
    campaigns: 3,
    avatar: 'ED',
  },
  {
    id: 5,
    name: 'David Wilson',
    email: 'david.wilson@company.com',
    role: 'Campaign Manager',
    status: 'Active',
    lastLogin: '2024-01-15',
    campaigns: 7,
    avatar: 'DW',
  },
];

const roles = ['All Roles', 'Administrator', 'Campaign Manager', 'Content Creator', 'Analyst'];
const statuses = ['All Status', 'Active', 'Inactive', 'Pending'];

export function Users() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState('All Roles');
  const [selectedStatus, setSelectedStatus] = useState('All Status');
  const [showAddUser, setShowAddUser] = useState(false);

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = selectedRole === 'All Roles' || user.role === selectedRole;
    const matchesStatus = selectedStatus === 'All Status' || user.status === selectedStatus;
    return matchesSearch && matchesRole && matchesStatus;
  });

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                User Management
              </h1>
              <p className="mt-3 text-lg text-gray-600 font-medium">
                Manage team members, roles, and permissions
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <button className="btn btn-outline">
                <Download className="h-4 w-4 mr-2" />
                Export
              </button>
              <button className="btn btn-outline">
                <Upload className="h-4 w-4 mr-2" />
                Import
              </button>
              <button
                onClick={() => setShowAddUser(true)}
                className="btn btn-primary"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add User
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card p-6 hover:scale-105 transition-all duration-300">
          <div className="flex items-center">
            <div className="p-3 rounded-2xl bg-gradient-to-r from-blue-500 to-purple-600 shadow-lg">
              <UsersIcon className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Total Users</p>
              <p className="text-3xl font-bold text-gray-900">{users.length}</p>
            </div>
          </div>
        </div>
        <div className="card p-6 hover:scale-105 transition-all duration-300">
          <div className="flex items-center">
            <div className="p-3 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 shadow-lg">
              <UserCheck className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Active Users</p>
              <p className="text-3xl font-bold text-gray-900">{users.filter(u => u.status === 'Active').length}</p>
            </div>
          </div>
        </div>
        <div className="card p-6 hover:scale-105 transition-all duration-300">
          <div className="flex items-center">
            <div className="p-3 rounded-2xl bg-gradient-to-r from-orange-500 to-red-600 shadow-lg">
              <UserX className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Inactive Users</p>
              <p className="text-3xl font-bold text-gray-900">{users.filter(u => u.status === 'Inactive').length}</p>
            </div>
          </div>
        </div>
        <div className="card p-6 hover:scale-105 transition-all duration-300">
          <div className="flex items-center">
            <div className="p-3 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-600 shadow-lg">
              <Shield className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Admins</p>
              <p className="text-3xl font-bold text-gray-900">{users.filter(u => u.role === 'Administrator').length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0 md:space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search users by name or email..."
              className="input pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="flex space-x-3">
            <select
              className="input"
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
            >
              {roles.map(role => (
                <option key={role} value={role}>{role}</option>
              ))}
            </select>
            <select
              className="input"
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
            >
              {statuses.map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Login
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Campaigns
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUsers.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50 transition-colors duration-200">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold">
                        {user.avatar}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{user.name}</div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${user.status === 'Active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                      }`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {user.lastLogin}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {user.campaigns}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <button className="text-blue-600 hover:text-blue-900 transition-colors duration-200">
                        <Edit className="h-4 w-4" />
                      </button>
                      <button className="text-red-600 hover:text-red-900 transition-colors duration-200">
                        <Trash2 className="h-4 w-4" />
                      </button>
                      <button className="text-gray-600 hover:text-gray-900 transition-colors duration-200">
                        <MoreVertical className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
