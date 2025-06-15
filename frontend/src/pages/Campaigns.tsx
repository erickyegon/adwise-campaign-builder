import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Play,
  Pause,
  Edit,
  Trash2,
  Eye,
  TrendingUp,
  DollarSign,
} from 'lucide-react';
import { apiEndpoints } from '../lib/api';

const statusColors = {
  active: 'bg-green-100 text-green-800',
  paused: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-blue-100 text-blue-800',
  draft: 'bg-gray-100 text-gray-800',
};

export function Campaigns() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: campaigns, isLoading, error } = useQuery({
    queryKey: ['campaigns', { search: searchTerm, status: statusFilter }],
    queryFn: () => apiEndpoints.campaigns.list({
      search: searchTerm || undefined,
      status: statusFilter !== 'all' ? statusFilter : undefined,
    }),
  });

  const mockCampaigns = [
    {
      id: 'campaign_001',
      name: 'Summer Sale Campaign',
      description: 'Comprehensive summer sale promotion across all channels',
      status: 'active',
      budget: 5000,
      spent: 3200,
      impressions: 125000,
      clicks: 3750,
      conversions: 187,
      roas: 4.2,
      start_date: '2024-06-01',
      end_date: '2024-08-31',
      created_at: '2024-05-15T10:00:00Z',
    },
    {
      id: 'campaign_002',
      name: 'Brand Awareness Q3',
      description: 'Building brand recognition for Q3 product launches',
      status: 'active',
      budget: 3000,
      spent: 1800,
      impressions: 89000,
      clicks: 2670,
      conversions: 134,
      roas: 3.8,
      start_date: '2024-07-01',
      end_date: '2024-09-30',
      created_at: '2024-06-20T14:30:00Z',
    },
    {
      id: 'campaign_003',
      name: 'Holiday Special 2024',
      description: 'Holiday season promotional campaign',
      status: 'draft',
      budget: 8000,
      spent: 0,
      impressions: 0,
      clicks: 0,
      conversions: 0,
      roas: 0,
      start_date: '2024-11-01',
      end_date: '2024-12-31',
      created_at: '2024-06-25T09:15:00Z',
    },
  ];

  const displayCampaigns = campaigns || mockCampaigns;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage and monitor your marketing campaigns
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary btn-md"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Campaign
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search campaigns..."
            className="input pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <select
          className="input w-auto"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="completed">Completed</option>
          <option value="draft">Draft</option>
        </select>
      </div>

      {/* Campaigns Grid */}
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
          {displayCampaigns.map((campaign: any) => (
            <div key={campaign.id} className="card p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <Link
                    to={`/campaigns/${campaign.id}`}
                    className="text-lg font-semibold text-gray-900 hover:text-primary-600"
                  >
                    {campaign.name}
                  </Link>
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                    {campaign.description}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`badge ${statusColors[campaign.status as keyof typeof statusColors]}`}>
                    {campaign.status}
                  </span>
                  <button className="p-1 text-gray-400 hover:text-gray-600">
                    <MoreHorizontal className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Budget</span>
                  <span className="text-sm font-medium">
                    ${campaign.spent.toLocaleString()} / ${campaign.budget.toLocaleString()}
                  </span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full"
                    style={{ width: `${(campaign.spent / campaign.budget) * 100}%` }}
                  ></div>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div>
                    <div className="text-xs text-gray-500">Impressions</div>
                    <div className="text-sm font-medium">{campaign.impressions.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">Clicks</div>
                    <div className="text-sm font-medium">{campaign.clicks.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">Conversions</div>
                    <div className="text-sm font-medium">{campaign.conversions}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">ROAS</div>
                    <div className="text-sm font-medium text-green-600">{campaign.roas}x</div>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
                <div className="flex space-x-2">
                  <button className="btn-ghost btn-sm">
                    <Eye className="h-4 w-4 mr-1" />
                    View
                  </button>
                  <button className="btn-ghost btn-sm">
                    <Edit className="h-4 w-4 mr-1" />
                    Edit
                  </button>
                </div>
                <div className="flex space-x-1">
                  {campaign.status === 'active' ? (
                    <button className="btn-ghost btn-sm text-yellow-600 hover:text-yellow-700">
                      <Pause className="h-4 w-4" />
                    </button>
                  ) : (
                    <button className="btn-ghost btn-sm text-green-600 hover:text-green-700">
                      <Play className="h-4 w-4" />
                    </button>
                  )}
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
      {!isLoading && displayCampaigns.length === 0 && (
        <div className="text-center py-12">
          <TrendingUp className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No campaigns found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating your first campaign.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary btn-md"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Campaign
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
