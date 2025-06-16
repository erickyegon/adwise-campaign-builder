import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Edit,
  Play,
  Pause,
  Share,
  Download,
  MoreHorizontal,
  Calendar,
  DollarSign,
  Target,
  TrendingUp,
  Eye,
  MousePointer,
  ShoppingCart,
  Users,
  BarChart3,
  Settings,
  Plus,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
} from 'recharts';

const mockCampaign = {
  id: 'campaign_001',
  name: 'Summer Sale Campaign 2024',
  description: 'Comprehensive summer sale promotion across all digital channels targeting millennials and Gen Z customers with personalized offers and dynamic content.',
  status: 'active',
  budget: 15000,
  spent: 8750,
  impressions: 245000,
  clicks: 7350,
  conversions: 367,
  roas: 4.8,
  ctr: 3.0,
  cpc: 1.19,
  start_date: '2024-06-01',
  end_date: '2024-08-31',
  created_at: '2024-05-15T10:00:00Z',
  updated_at: '2024-06-15T14:30:00Z',
  target_audience: 'Millennials & Gen Z (25-40)',
  platforms: ['Facebook', 'Instagram', 'Google Ads', 'LinkedIn'],
  objectives: ['Brand Awareness', 'Lead Generation', 'Sales'],
};

const performanceData = [
  { date: '2024-06-01', impressions: 8000, clicks: 240, conversions: 12, spend: 285 },
  { date: '2024-06-02', impressions: 12000, clicks: 360, conversions: 18, spend: 428 },
  { date: '2024-06-03', impressions: 9500, clicks: 285, conversions: 14, spend: 339 },
  { date: '2024-06-04', impressions: 15000, clicks: 450, conversions: 23, spend: 535 },
  { date: '2024-06-05', impressions: 11000, clicks: 330, conversions: 16, spend: 392 },
  { date: '2024-06-06', impressions: 13500, clicks: 405, conversions: 20, spend: 481 },
  { date: '2024-06-07', impressions: 10500, clicks: 315, conversions: 15, spend: 374 },
];

const campaignAds = [
  {
    id: 'ad_001',
    name: 'Summer Sale Hero Banner',
    platform: 'Facebook',
    status: 'active',
    impressions: 45000,
    clicks: 1350,
    conversions: 67,
    spend: 1200,
    ctr: 3.0,
    roas: 5.2,
  },
  {
    id: 'ad_002',
    name: 'Product Showcase Video',
    platform: 'Instagram',
    status: 'active',
    impressions: 38000,
    clicks: 1140,
    conversions: 57,
    spend: 980,
    ctr: 3.0,
    roas: 4.8,
  },
  {
    id: 'ad_003',
    name: 'Search Ad - Summer Collection',
    platform: 'Google Ads',
    status: 'paused',
    impressions: 22000,
    clicks: 660,
    conversions: 33,
    spend: 750,
    ctr: 3.0,
    roas: 3.9,
  },
];

export function CampaignDetail() {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'ads', name: 'Ads', icon: Target },
    { id: 'analytics', name: 'Analytics', icon: TrendingUp },
    { id: 'settings', name: 'Settings', icon: Settings },
  ];

  const metrics = [
    {
      name: 'Total Impressions',
      value: mockCampaign.impressions.toLocaleString(),
      change: '+12.5%',
      changeType: 'positive',
      icon: Eye,
    },
    {
      name: 'Total Clicks',
      value: mockCampaign.clicks.toLocaleString(),
      change: '+8.3%',
      changeType: 'positive',
      icon: MousePointer,
    },
    {
      name: 'Conversions',
      value: mockCampaign.conversions.toString(),
      change: '+15.2%',
      changeType: 'positive',
      icon: ShoppingCart,
    },
    {
      name: 'ROAS',
      value: `${mockCampaign.roas}x`,
      change: '+5.1%',
      changeType: 'positive',
      icon: DollarSign,
    },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-xl">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-4">
              <Link
                to="/campaigns"
                className="btn btn-outline mt-1"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Campaigns
              </Link>
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    {mockCampaign.name}
                  </h1>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${mockCampaign.status === 'active'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                    }`}>
                    {mockCampaign.status}
                  </span>
                </div>
                <p className="text-lg text-gray-600 font-medium max-w-3xl">
                  {mockCampaign.description}
                </p>
                <div className="flex items-center space-x-6 mt-4 text-sm text-gray-500">
                  <div className="flex items-center">
                    <Calendar className="h-4 w-4 mr-1" />
                    {mockCampaign.start_date} - {mockCampaign.end_date}
                  </div>
                  <div className="flex items-center">
                    <Users className="h-4 w-4 mr-1" />
                    {mockCampaign.target_audience}
                  </div>
                  <div className="flex items-center">
                    <Target className="h-4 w-4 mr-1" />
                    {mockCampaign.platforms.length} Platforms
                  </div>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button className="btn btn-outline">
                <Share className="h-4 w-4 mr-2" />
                Share
              </button>
              <button className="btn btn-outline">
                <Download className="h-4 w-4 mr-2" />
                Export
              </button>
              <button className="btn btn-secondary">
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </button>
              {mockCampaign.status === 'active' ? (
                <button className="btn btn-outline">
                  <Pause className="h-4 w-4 mr-2" />
                  Pause
                </button>
              ) : (
                <button className="btn btn-primary">
                  <Play className="h-4 w-4 mr-2" />
                  Resume
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Budget Progress */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Budget Overview</h3>
          <div className="text-sm text-gray-500">
            ${mockCampaign.spent.toLocaleString()} of ${mockCampaign.budget.toLocaleString()} spent
          </div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
          <div
            className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${(mockCampaign.spent / mockCampaign.budget) * 100}%` }}
          ></div>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">
            {((mockCampaign.spent / mockCampaign.budget) * 100).toFixed(1)}% used
          </span>
          <span className="text-gray-600">
            ${(mockCampaign.budget - mockCampaign.spent).toLocaleString()} remaining
          </span>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric, index) => (
          <div
            key={metric.name}
            className="card p-6 hover:scale-105 transition-all duration-300"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-center">
              <div className="p-3 rounded-2xl bg-gradient-to-r from-blue-500 to-purple-600 shadow-lg">
                <metric.icon className="h-8 w-8 text-white" />
              </div>
              <div className="ml-4 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-semibold text-gray-500 truncate uppercase tracking-wider">
                    {metric.name}
                  </dt>
                  <dd className="flex items-baseline mt-1">
                    <div className="text-2xl font-bold text-gray-900">{metric.value}</div>
                    <div className={`ml-2 flex items-center text-sm font-bold px-2 py-1 rounded-full ${metric.changeType === 'positive'
                        ? 'text-green-700 bg-green-100'
                        : 'text-red-700 bg-red-100'
                      }`}>
                      <TrendingUp className="h-3 w-3 mr-1" />
                      <span>{metric.change}</span>
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-all duration-200 ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
            >
              <tab.icon className="h-5 w-5 mr-2" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Performance Chart */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Performance Trends</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="impressions"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.1}
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Campaign Info */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Details</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Campaign ID:</span>
                    <span className="font-medium">{mockCampaign.id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Created:</span>
                    <span className="font-medium">{new Date(mockCampaign.created_at).toLocaleDateString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Last Updated:</span>
                    <span className="font-medium">{new Date(mockCampaign.updated_at).toLocaleDateString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">CTR:</span>
                    <span className="font-medium">{mockCampaign.ctr}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">CPC:</span>
                    <span className="font-medium">${mockCampaign.cpc}</span>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Targeting & Objectives</h3>
                <div className="space-y-4">
                  <div>
                    <span className="text-sm font-medium text-gray-600">Target Audience:</span>
                    <p className="text-gray-900">{mockCampaign.target_audience}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-600">Platforms:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {mockCampaign.platforms.map((platform) => (
                        <span key={platform} className="badge bg-blue-100 text-blue-800">
                          {platform}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-600">Objectives:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {mockCampaign.objectives.map((objective) => (
                        <span key={objective} className="badge bg-green-100 text-green-800">
                          {objective}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ads' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Campaign Ads</h3>
              <button className="btn btn-primary">
                <Plus className="h-4 w-4 mr-2" />
                Create Ad
              </button>
            </div>

            <div className="space-y-4">
              {campaignAds.map((ad) => (
                <div key={ad.id} className="card p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="text-lg font-semibold text-gray-900">{ad.name}</h4>
                        <span className={`badge ${ad.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                          }`}>
                          {ad.status}
                        </span>
                        <span className="badge bg-blue-100 text-blue-800">
                          {ad.platform}
                        </span>
                      </div>

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
                          <div className="text-gray-500">Conversions</div>
                          <div className="font-medium">{ad.conversions}</div>
                        </div>
                        <div>
                          <div className="text-gray-500">Spend</div>
                          <div className="font-medium">${ad.spend.toLocaleString()}</div>
                        </div>
                        <div>
                          <div className="text-gray-500">ROAS</div>
                          <div className="font-medium text-green-600">{ad.roas}x</div>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      <button className="btn btn-outline btn-sm">
                        <Edit className="h-4 w-4" />
                      </button>
                      {ad.status === 'active' ? (
                        <button className="btn btn-outline btn-sm">
                          <Pause className="h-4 w-4" />
                        </button>
                      ) : (
                        <button className="btn btn-primary btn-sm">
                          <Play className="h-4 w-4" />
                        </button>
                      )}
                      <button className="btn btn-outline btn-sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Detailed Analytics</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="clicks" stroke="#3b82f6" strokeWidth={2} />
                    <Line type="monotone" dataKey="conversions" stroke="#10b981" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-6">
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Campaign Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campaign Name
                  </label>
                  <input
                    type="text"
                    className="input"
                    defaultValue={mockCampaign.name}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    className="input min-h-[100px] resize-none"
                    defaultValue={mockCampaign.description}
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Start Date
                    </label>
                    <input
                      type="date"
                      className="input"
                      defaultValue={mockCampaign.start_date}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      End Date
                    </label>
                    <input
                      type="date"
                      className="input"
                      defaultValue={mockCampaign.end_date}
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Budget ($)
                  </label>
                  <input
                    type="number"
                    className="input"
                    defaultValue={mockCampaign.budget}
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button className="btn btn-outline">
                    Cancel
                  </button>
                  <button className="btn btn-primary">
                    Save Changes
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
