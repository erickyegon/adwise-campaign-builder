import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Plus,
  Search,
  Users,
  Crown,
  Shield,
  User,
  MoreHorizontal,
  Edit,
  Trash2,
  UserPlus,
  Settings,
} from 'lucide-react';
import { api } from '../lib/api';

const roleIcons = {
  owner: Crown,
  manager: Shield,
  member: User,
};

const roleColors = {
  owner: 'bg-purple-100 text-purple-800',
  manager: 'bg-blue-100 text-blue-800',
  member: 'bg-gray-100 text-gray-800',
};

const mockTeams = [
  {
    id: 'team_001',
    name: 'Marketing Team',
    description: 'Main marketing team for digital campaigns',
    is_active: true,
    owner_id: 'user_001',
    member_count: 5,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    members: [
      {
        user_id: 'user_001',
        username: 'admin',
        email: 'admin@adwise.ai',
        role: 'owner',
        joined_at: '2024-01-01T00:00:00Z',
      },
      {
        user_id: 'user_002',
        username: 'manager',
        email: 'manager@adwise.ai',
        role: 'manager',
        joined_at: '2024-01-02T00:00:00Z',
      },
      {
        user_id: 'user_003',
        username: 'creator',
        email: 'creator@adwise.ai',
        role: 'member',
        joined_at: '2024-01-03T00:00:00Z',
      },
    ],
  },
  {
    id: 'team_002',
    name: 'Creative Team',
    description: 'Content creation and design team',
    is_active: true,
    owner_id: 'user_002',
    member_count: 3,
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
    members: [
      {
        user_id: 'user_002',
        username: 'manager',
        email: 'manager@adwise.ai',
        role: 'owner',
        joined_at: '2024-01-02T00:00:00Z',
      },
      {
        user_id: 'user_004',
        username: 'designer',
        email: 'designer@adwise.ai',
        role: 'member',
        joined_at: '2024-01-04T00:00:00Z',
      },
      {
        user_id: 'user_005',
        username: 'copywriter',
        email: 'copywriter@adwise.ai',
        role: 'member',
        joined_at: '2024-01-05T00:00:00Z',
      },
    ],
  },
  {
    id: 'team_003',
    name: 'Analytics Team',
    description: 'Data analysis and reporting team',
    is_active: true,
    owner_id: 'user_001',
    member_count: 2,
    created_at: '2024-01-03T00:00:00Z',
    updated_at: '2024-01-03T00:00:00Z',
    members: [
      {
        user_id: 'user_001',
        username: 'admin',
        email: 'admin@adwise.ai',
        role: 'owner',
        joined_at: '2024-01-03T00:00:00Z',
      },
      {
        user_id: 'user_006',
        username: 'analyst',
        email: 'analyst@adwise.ai',
        role: 'member',
        joined_at: '2024-01-06T00:00:00Z',
      },
    ],
  },
];

export function Teams() {
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState<any>(null);

  const { data: teams, isLoading } = useQuery({
    queryKey: ['teams', { search: searchTerm }],
    queryFn: () => api.getTeams({
      search: searchTerm || undefined,
    }),
  });

  const displayTeams = teams || mockTeams;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Teams</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage your teams and collaborate on campaigns
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary btn-md"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Team
        </button>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search teams..."
          className="input pl-10"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Teams Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-2/3 mb-4"></div>
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/3"></div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayTeams.map((team: any) => (
            <div key={team.id} className="card p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <div className="h-10 w-10 bg-primary-100 rounded-lg flex items-center justify-center">
                      <Users className="h-5 w-5 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{team.name}</h3>
                      <p className="text-sm text-gray-500">{team.member_count} members</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {team.description}
                  </p>
                </div>
                <button className="p-1 text-gray-400 hover:text-gray-600">
                  <MoreHorizontal className="h-4 w-4" />
                </button>
              </div>

              {/* Team Members Preview */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Members</span>
                  <button className="text-sm text-primary-600 hover:text-primary-700">
                    View all
                  </button>
                </div>
                <div className="space-y-2">
                  {team.members?.slice(0, 3).map((member: any) => {
                    const RoleIcon = roleIcons[member.role as keyof typeof roleIcons];
                    return (
                      <div key={member.user_id} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="h-6 w-6 bg-gray-200 rounded-full flex items-center justify-center">
                            <User className="h-3 w-3 text-gray-600" />
                          </div>
                          <span className="text-sm text-gray-900">{member.username}</span>
                        </div>
                        <span className={`badge text-xs ${roleColors[member.role as keyof typeof roleColors]}`}>
                          <RoleIcon className="h-3 w-3 mr-1" />
                          {member.role}
                        </span>
                      </div>
                    );
                  })}
                  {team.member_count > 3 && (
                    <div className="text-xs text-gray-500 text-center">
                      +{team.member_count - 3} more members
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="flex space-x-2">
                  <button className="btn-ghost btn-sm">
                    <UserPlus className="h-4 w-4 mr-1" />
                    Add Member
                  </button>
                </div>
                <div className="flex space-x-1">
                  <button className="btn-ghost btn-sm">
                    <Settings className="h-4 w-4" />
                  </button>
                  <button className="btn-ghost btn-sm">
                    <Edit className="h-4 w-4" />
                  </button>
                  <button className="btn-ghost btn-sm text-red-600 hover:text-red-700">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && displayTeams.length === 0 && (
        <div className="text-center py-12">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No teams found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating your first team.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary btn-md"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Team
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
