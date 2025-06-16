import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart3,
  TrendingUp,
  Users,
  Target,
  DollarSign,
  Eye,
  MousePointer,
  ShoppingCart,
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { api } from '../lib/api';

const stats = [
  {
    name: 'Total Campaigns',
    value: '15',
    change: '+12%',
    changeType: 'positive',
    icon: Target,
  },
  {
    name: 'Active Ads',
    value: '32',
    change: '+8%',
    changeType: 'positive',
    icon: Eye,
  },
  {
    name: 'Total Spend',
    value: '$2,500',
    change: '+15%',
    changeType: 'positive',
    icon: DollarSign,
  },
  {
    name: 'Conversions',
    value: '187',
    change: '+23%',
    changeType: 'positive',
    icon: ShoppingCart,
  },
];

const chartData = [
  { name: 'Jan', impressions: 4000, clicks: 240, conversions: 24 },
  { name: 'Feb', impressions: 3000, clicks: 139, conversions: 22 },
  { name: 'Mar', impressions: 2000, clicks: 980, conversions: 29 },
  { name: 'Apr', impressions: 2780, clicks: 390, conversions: 20 },
  { name: 'May', impressions: 1890, clicks: 480, conversions: 27 },
  { name: 'Jun', impressions: 2390, clicks: 380, conversions: 25 },
];

const campaignData = [
  { name: 'Summer Sale', spend: 900, roas: 4.8, status: 'active' },
  { name: 'Brand Awareness', spend: 650, roas: 3.9, status: 'active' },
  { name: 'Product Launch', spend: 450, roas: 5.2, status: 'paused' },
  { name: 'Holiday Special', spend: 320, roas: 3.1, status: 'active' },
];

export function Dashboard() {
  const { data: analyticsData, isLoading } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => api.get('/analytics/overview'),
  });

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-xl">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <p className="mt-3 text-lg text-gray-600 font-medium">
            Welcome back! Here's what's happening with your campaigns today.
          </p>
          <div className="mt-4 flex items-center space-x-2">
            <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-green-600 font-semibold">All systems operational</span>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <div
            key={stat.name}
            className="card p-8 group hover:scale-105 transition-all duration-300"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-2xl bg-gradient-to-r from-blue-500 to-purple-600 shadow-lg group-hover:shadow-xl transition-all duration-300">
                  <stat.icon className="h-8 w-8 text-white" />
                </div>
              </div>
              <div className="ml-6 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-semibold text-gray-500 truncate uppercase tracking-wider">{stat.name}</dt>
                  <dd className="flex items-baseline mt-2">
                    <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
                    <div
                      className={`ml-3 flex items-center text-sm font-bold px-2 py-1 rounded-full ${stat.changeType === 'positive'
                        ? 'text-green-700 bg-green-100'
                        : 'text-red-700 bg-red-100'
                        }`}
                    >
                      <TrendingUp className="h-4 w-4 flex-shrink-0 mr-1" />
                      <span>{stat.change}</span>
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Performance Chart */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-gray-900">Performance Overview</h3>
            <div className="flex space-x-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                Impressions
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Clicks
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                Conversions
              </span>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="impressions" stroke="#3b82f6" strokeWidth={2} />
                <Line type="monotone" dataKey="clicks" stroke="#10b981" strokeWidth={2} />
                <Line type="monotone" dataKey="conversions" stroke="#8b5cf6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Campaign Performance */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-6">Top Campaigns</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={campaignData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="spend" fill="#3b82f6" />
                <Bar dataKey="roas" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {[
            {
              id: 1,
              action: 'Campaign "Summer Sale" was updated',
              user: 'Admin User',
              time: '2 hours ago',
              type: 'update',
            },
            {
              id: 2,
              action: 'New ad "Premium Products" was created',
              user: 'Content Creator',
              time: '4 hours ago',
              type: 'create',
            },
            {
              id: 3,
              action: 'Analytics report was generated',
              user: 'Manager',
              time: '6 hours ago',
              type: 'report',
            },
            {
              id: 4,
              action: 'Team member was added to "Marketing Team"',
              user: 'Admin User',
              time: '1 day ago',
              type: 'team',
            },
          ].map((activity) => (
            <div key={activity.id} className="px-6 py-4">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                    <BarChart3 className="h-4 w-4 text-primary-600" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900">{activity.action}</p>
                  <p className="text-sm text-gray-500">
                    by {activity.user} • {activity.time}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
