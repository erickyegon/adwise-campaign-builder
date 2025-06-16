import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Calendar,
  Download,
  Filter,
  TrendingUp,
  TrendingDown,
  Eye,
  MousePointer,
  ShoppingCart,
  DollarSign,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from 'recharts';
import { api } from '../lib/api';

const timeRanges = [
  { label: 'Last 7 days', value: 'last_7_days' },
  { label: 'Last 30 days', value: 'last_30_days' },
  { label: 'Last 90 days', value: 'last_90_days' },
  { label: 'Custom', value: 'custom' },
];

const performanceData = [
  { date: '2024-06-01', impressions: 12000, clicks: 360, conversions: 18, spend: 450 },
  { date: '2024-06-02', impressions: 15000, clicks: 450, conversions: 23, spend: 520 },
  { date: '2024-06-03', impressions: 11000, clicks: 330, conversions: 16, spend: 410 },
  { date: '2024-06-04', impressions: 18000, clicks: 540, conversions: 27, spend: 630 },
  { date: '2024-06-05', impressions: 14000, clicks: 420, conversions: 21, spend: 480 },
  { date: '2024-06-06', impressions: 16000, clicks: 480, conversions: 24, spend: 550 },
  { date: '2024-06-07', impressions: 13000, clicks: 390, conversions: 19, spend: 470 },
];

const platformData = [
  { name: 'Facebook', value: 35, color: '#1877F2' },
  { name: 'Google Ads', value: 30, color: '#4285F4' },
  { name: 'Instagram', value: 20, color: '#E4405F' },
  { name: 'LinkedIn', value: 10, color: '#0A66C2' },
  { name: 'Twitter', value: 5, color: '#1DA1F2' },
];

const campaignPerformance = [
  { name: 'Summer Sale', impressions: 45000, clicks: 1350, conversions: 67, spend: 900, roas: 4.8 },
  { name: 'Brand Awareness', impressions: 35000, clicks: 1050, conversions: 52, spend: 650, roas: 3.9 },
  { name: 'Product Launch', impressions: 28000, clicks: 840, conversions: 42, spend: 520, roas: 5.2 },
  { name: 'Holiday Special', impressions: 17000, clicks: 510, conversions: 25, spend: 320, roas: 3.1 },
];

export function Analytics() {
  const [timeRange, setTimeRange] = useState('last_30_days');
  const [selectedMetric, setSelectedMetric] = useState('impressions');

  const { data: analyticsData, isLoading } = useQuery({
    queryKey: ['analytics', 'overview', timeRange],
    queryFn: () => api.getAnalytics(),
  });

  const metrics = [
    {
      name: 'Total Impressions',
      value: '125,000',
      change: '+12.5%',
      changeType: 'positive',
      icon: Eye,
    },
    {
      name: 'Total Clicks',
      value: '3,750',
      change: '+8.3%',
      changeType: 'positive',
      icon: MousePointer,
    },
    {
      name: 'Conversions',
      value: '187',
      change: '+15.2%',
      changeType: 'positive',
      icon: ShoppingCart,
    },
    {
      name: 'Total Spend',
      value: '$2,500',
      change: '+5.1%',
      changeType: 'positive',
      icon: DollarSign,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="mt-2 text-sm text-gray-700">
            Comprehensive insights into your campaign performance
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            className="input w-auto"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            {timeRanges.map((range) => (
              <option key={range.value} value={range.value}>
                {range.label}
              </option>
            ))}
          </select>
          <button className="btn-outline btn-md">
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <div key={metric.name} className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <metric.icon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">{metric.name}</dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">{metric.value}</div>
                    <div
                      className={`ml-2 flex items-baseline text-sm font-semibold ${
                        metric.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {metric.changeType === 'positive' ? (
                        <TrendingUp className="h-4 w-4 flex-shrink-0 self-center" />
                      ) : (
                        <TrendingDown className="h-4 w-4 flex-shrink-0 self-center" />
                      )}
                      <span className="ml-1">{metric.change}</span>
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Performance Chart */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-gray-900">Performance Trends</h3>
          <div className="flex items-center space-x-2">
            <select
              className="input w-auto text-sm"
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
            >
              <option value="impressions">Impressions</option>
              <option value="clicks">Clicks</option>
              <option value="conversions">Conversions</option>
              <option value="spend">Spend</option>
            </select>
          </div>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area
                type="monotone"
                dataKey={selectedMetric}
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.1}
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Platform Distribution & Campaign Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Platform Distribution */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-6">Traffic by Platform</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={platformData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {platformData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 space-y-2">
            {platformData.map((platform) => (
              <div key={platform.name} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div
                    className="w-3 h-3 rounded-full mr-2"
                    style={{ backgroundColor: platform.color }}
                  ></div>
                  <span className="text-sm text-gray-600">{platform.name}</span>
                </div>
                <span className="text-sm font-medium">{platform.value}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Campaign Performance */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-6">Campaign Performance</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={campaignPerformance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="roas" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Detailed Campaign Table */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Campaign Details</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Campaign
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Impressions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Clicks
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Conversions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Spend
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ROAS
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {campaignPerformance.map((campaign) => (
                <tr key={campaign.name} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {campaign.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {campaign.impressions.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {campaign.clicks.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {campaign.conversions}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${campaign.spend.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {campaign.roas}x
                    </span>
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
