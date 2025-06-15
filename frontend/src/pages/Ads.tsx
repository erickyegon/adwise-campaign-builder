import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
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
  Zap,
  Target,
  TrendingUp,
  Facebook,
  Instagram,
} from 'lucide-react';
import { apiEndpoints } from '../lib/api';

const statusColors = {
  active: 'bg-green-100 text-green-800',
  paused: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-blue-100 text-blue-800',
  draft: 'bg-gray-100 text-gray-800',
};

const platformIcons = {
  facebook: Facebook,
  instagram: Instagram,
  google_ads: Target,
  linkedin: Target,
  twitter: Target,
  tiktok: Target,
};

const mockAds = [
  {
    id: 'ad_001',
    name: 'Summer Sale Facebook Ad',
    campaign_id: 'campaign_001',
    campaign_name: 'Summer Sale Campaign',
    platform: 'facebook',
    ad_type: 'image',
    headline: 'Summer Sale - Up to 50% Off!',
    description: "Don't miss our biggest summer sale. Shop now and save big on all your favorite items.",
    call_to_action: 'Shop Now',
    status: 'active',
    budget: 1000,
    spent: 250,
    impressions: 15000,
    clicks: 450,
    conversions: 23,
    ctr: 3.0,
    cpc: 0.56,
    roas: 4.2,
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'ad_002',
    name: 'Google Search Ad - Premium Products',
    campaign_id: 'campaign_001',
    campaign_name: 'Summer Sale Campaign',
    platform: 'google_ads',
    ad_type: 'text',
    headline: 'Premium Quality Products',
    description: 'Discover our premium collection with free shipping and 30-day returns.',
    call_to_action: 'Learn More',
    status: 'active',
    budget: 500,
    spent: 180,
    impressions: 8000,
    clicks: 320,
    conversions: 18,
    ctr: 4.0,
    cpc: 0.56,
    roas: 3.8,
    created_at: '2024-01-02T00:00:00Z',
  },
  {
    id: 'ad_003',
    name: 'Instagram Story - New Collection',
    campaign_id: 'campaign_002',
    campaign_name: 'Brand Awareness Q3',
    platform: 'instagram',
    ad_type: 'story',
    headline: 'New Collection Drop',
    description: 'Check out our latest collection featuring trending styles.',
    call_to_action: 'View Collection',
    status: 'paused',
    budget: 300,
    spent: 120,
    impressions: 5000,
    clicks: 200,
    conversions: 8,
    ctr: 4.0,
    cpc: 0.60,
    roas: 2.5,
    created_at: '2024-01-03T00:00:00Z',
  },
];

export function Ads() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [platformFilter, setPlatformFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: ads, isLoading } = useQuery({
    queryKey: ['ads', { search: searchTerm, status: statusFilter, platform: platformFilter }],
    queryFn: () => apiEndpoints.ads.list({
      search: searchTerm || undefined,
      status: statusFilter !== 'all' ? statusFilter : undefined,
      platform: platformFilter !== 'all' ? platformFilter : undefined,
    }),
  });

  const displayAds = ads || mockAds;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Ads</h1>
          <p className="mt-2 text-sm text-gray-700">
            Create, manage, and optimize your advertising campaigns
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-secondary btn-md"
          >
            <Zap className="h-4 w-4 mr-2" />
            AI Generate
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary btn-md"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Ad
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search ads..."
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
        <select
          className="input w-auto"
          value={platformFilter}
          onChange={(e) => setPlatformFilter(e.target.value)}
        >
          <option value="all">All Platforms</option>
          <option value="facebook">Facebook</option>
          <option value="instagram">Instagram</option>
          <option value="google_ads">Google Ads</option>
          <option value="linkedin">LinkedIn</option>
          <option value="twitter">Twitter</option>
        </select>
      </div>

      {/* Ads List */}
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="flex items-start space-x-4">
                <div className="h-16 w-16 bg-gray-200 rounded-lg"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {displayAds.map((ad: any) => {
            const PlatformIcon = platformIcons[ad.platform as keyof typeof platformIcons] || Target;

            return (
              <div key={ad.id} className="card p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    {/* Platform Icon */}
                    <div className="flex-shrink-0">
                      <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
                        <PlatformIcon className="h-6 w-6 text-primary-600" />
                      </div>
                    </div>

                    {/* Ad Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 truncate">
                          {ad.name}
                        </h3>
                        <span className={`badge ${statusColors[ad.status as keyof typeof statusColors]}`}>
                          {ad.status}
                        </span>
                        <span className="badge-outline">
                          {ad.platform.replace('_', ' ')}
                        </span>
                      </div>

                      <p className="text-sm text-gray-600 mb-2">
                        Campaign: {ad.campaign_name}
                      </p>

                      <div className="mb-3">
                        <p className="text-sm font-medium text-gray-900 mb-1">
                          {ad.headline}
                        </p>
                        <p className="text-sm text-gray-600 line-clamp-2">
                          {ad.description}
                        </p>
                      </div>

                      {/* Performance Metrics */}
                      <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-sm">
                        <div>
                          <div className="text-gray-500">Impressions</div>
                          <div className="font-medium">{ad.impressions.toLocaleString()}</div>
                        </div>
                        <div>
                          <div className="text-gray-500">Clicks</div>
                          <div className="font-medium">{ad.clicks.toLocaleString()}</div>
                        </div>
                        <div>
                          <div className="text-gray-500">CTR</div>
                          <div className="font-medium">{ad.ctr}%</div>
                        </div>
                        <div>
                          <div className="text-gray-500">CPC</div>
                          <div className="font-medium">${ad.cpc}</div>
                        </div>
                        <div>
                          <div className="text-gray-500">Conversions</div>
                          <div className="font-medium">{ad.conversions}</div>
                        </div>
                        <div>
                          <div className="text-gray-500">ROAS</div>
                          <div className="font-medium text-green-600">{ad.roas}x</div>
                        </div>
                      </div>

                      {/* Budget Progress */}
                      <div className="mt-4">
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-500">Budget</span>
                          <span className="font-medium">
                            ${ad.spent.toLocaleString()} / ${ad.budget.toLocaleString()}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full"
                            style={{ width: `${(ad.spent / ad.budget) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-2 ml-4">
                    <button className="btn-ghost btn-sm">
                      <Eye className="h-4 w-4" />
                    </button>
                    <button className="btn-ghost btn-sm">
                      <Edit className="h-4 w-4" />
                    </button>
                    {ad.status === 'active' ? (
                      <button className="btn-ghost btn-sm text-yellow-600 hover:text-yellow-700">
                        <Pause className="h-4 w-4" />
                      </button>
                    ) : (
                      <button className="btn-ghost btn-sm text-green-600 hover:text-green-700">
                        <Play className="h-4 w-4" />
                      </button>
                    )}
                    <button className="btn-ghost btn-sm">
                      <MoreHorizontal className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && displayAds.length === 0 && (
        <div className="text-center py-12">
          <Target className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No ads found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating your first ad or use AI to generate one.
          </p>
          <div className="mt-6 flex justify-center space-x-3">
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-secondary btn-md"
            >
              <Zap className="h-4 w-4 mr-2" />
              AI Generate
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary btn-md"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Ad
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
