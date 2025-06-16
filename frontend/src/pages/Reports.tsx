import React, { useState } from 'react';
import {
  FileText,
  Download,
  Calendar,
  Filter,
  Search,
  BarChart3,
  TrendingUp,
  Users,
  Target,
  DollarSign,
  Eye,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  Share,
  Mail,
} from 'lucide-react';

const reportTypes = [
  {
    id: 'campaign_performance',
    name: 'Campaign Performance',
    description: 'Detailed analysis of campaign metrics and ROI',
    icon: BarChart3,
    color: 'from-blue-500 to-purple-600',
    lastGenerated: '2024-01-15',
    status: 'ready',
  },
  {
    id: 'audience_insights',
    name: 'Audience Insights',
    description: 'Demographics and behavior analysis',
    icon: Users,
    color: 'from-green-500 to-emerald-600',
    lastGenerated: '2024-01-14',
    status: 'ready',
  },
  {
    id: 'ad_performance',
    name: 'Ad Performance',
    description: 'Individual ad metrics and optimization recommendations',
    icon: Target,
    color: 'from-orange-500 to-red-600',
    lastGenerated: '2024-01-13',
    status: 'generating',
  },
  {
    id: 'roi_analysis',
    name: 'ROI Analysis',
    description: 'Return on investment and cost analysis',
    icon: DollarSign,
    color: 'from-purple-500 to-pink-600',
    lastGenerated: '2024-01-12',
    status: 'ready',
  },
  {
    id: 'traffic_analysis',
    name: 'Traffic Analysis',
    description: 'Website traffic and conversion funnel analysis',
    icon: TrendingUp,
    color: 'from-indigo-500 to-blue-600',
    lastGenerated: '2024-01-11',
    status: 'ready',
  },
  {
    id: 'competitive_analysis',
    name: 'Competitive Analysis',
    description: 'Market positioning and competitor insights',
    icon: Eye,
    color: 'from-teal-500 to-cyan-600',
    lastGenerated: '2024-01-10',
    status: 'ready',
  },
];

const recentReports = [
  {
    id: 'report_001',
    name: 'Q4 2024 Campaign Performance Report',
    type: 'Campaign Performance',
    generatedAt: '2024-01-15T10:30:00Z',
    size: '2.4 MB',
    format: 'PDF',
    status: 'completed',
  },
  {
    id: 'report_002',
    name: 'December Audience Insights',
    type: 'Audience Insights',
    generatedAt: '2024-01-14T15:45:00Z',
    size: '1.8 MB',
    format: 'Excel',
    status: 'completed',
  },
  {
    id: 'report_003',
    name: 'Holiday Campaign ROI Analysis',
    type: 'ROI Analysis',
    generatedAt: '2024-01-13T09:20:00Z',
    size: '3.1 MB',
    format: 'PDF',
    status: 'completed',
  },
  {
    id: 'report_004',
    name: 'Weekly Traffic Report',
    type: 'Traffic Analysis',
    generatedAt: '2024-01-12T14:15:00Z',
    size: '1.2 MB',
    format: 'CSV',
    status: 'completed',
  },
];

export function Reports() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [dateRange, setDateRange] = useState('last_30_days');

  const filteredReports = recentReports.filter(report => {
    const matchesSearch = report.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedType === 'all' || report.type === selectedType;
    return matchesSearch && matchesType;
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
                Reports & Analytics
              </h1>
              <p className="mt-3 text-lg text-gray-600 font-medium">
                Generate comprehensive reports and export campaign insights
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <button className="btn btn-outline">
                <Calendar className="h-4 w-4 mr-2" />
                Schedule Report
              </button>
              <button className="btn btn-primary">
                <Plus className="h-4 w-4 mr-2" />
                Generate Report
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Report Types Grid */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Available Reports</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {reportTypes.map((report, index) => (
            <div
              key={report.id}
              className="card p-6 hover:scale-105 transition-all duration-300 group"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-2xl bg-gradient-to-r ${report.color} shadow-lg group-hover:shadow-xl transition-all duration-300`}>
                  <report.icon className="h-8 w-8 text-white" />
                </div>
                <div className="flex items-center space-x-2">
                  {report.status === 'ready' && (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  )}
                  {report.status === 'generating' && (
                    <div className="flex items-center">
                      <Clock className="h-5 w-5 text-orange-500 animate-spin" />
                    </div>
                  )}
                </div>
              </div>

              <h3 className="text-lg font-bold text-gray-900 mb-2">{report.name}</h3>
              <p className="text-sm text-gray-600 mb-4">{report.description}</p>

              <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                <span>Last generated: {report.lastGenerated}</span>
                <span className={`px-2 py-1 rounded-full ${report.status === 'ready'
                  ? 'bg-green-100 text-green-700'
                  : 'bg-orange-100 text-orange-700'
                  }`}>
                  {report.status}
                </span>
              </div>

              <div className="flex space-x-2">
                <button
                  className="btn btn-primary flex-1"
                  disabled={report.status === 'generating'}
                >
                  <Download className="h-4 w-4 mr-2" />
                  {report.status === 'generating' ? 'Generating...' : 'Generate'}
                </button>
                <button className="btn btn-outline">
                  <Share className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Reports */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Recent Reports</h2>
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search reports..."
                className="input pl-10 w-64"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <select
              className="input"
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="Campaign Performance">Campaign Performance</option>
              <option value="Audience Insights">Audience Insights</option>
              <option value="ROI Analysis">ROI Analysis</option>
              <option value="Traffic Analysis">Traffic Analysis</option>
            </select>
          </div>
        </div>

        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Report Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Generated
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Size
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Format
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredReports.map((report) => (
                  <tr key={report.id} className="hover:bg-gray-50 transition-colors duration-200">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <FileText className="h-5 w-5 text-blue-500 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">{report.name}</div>
                          <div className="text-sm text-gray-500">ID: {report.id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {report.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(report.generatedAt).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {report.size}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${report.format === 'PDF'
                          ? 'bg-red-100 text-red-800'
                          : report.format === 'Excel'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                        {report.format}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <button className="text-blue-600 hover:text-blue-900 transition-colors duration-200">
                          <Download className="h-4 w-4" />
                        </button>
                        <button className="text-green-600 hover:text-green-900 transition-colors duration-200">
                          <Share className="h-4 w-4" />
                        </button>
                        <button className="text-purple-600 hover:text-purple-900 transition-colors duration-200">
                          <Mail className="h-4 w-4" />
                        </button>
                        <button className="text-gray-600 hover:text-gray-900 transition-colors duration-200">
                          <Eye className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {filteredReports.length === 0 && (
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No reports found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search criteria or generate a new report.
            </p>
          </div>
        )}
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card p-6 hover:scale-105 transition-all duration-300">
          <div className="flex items-center">
            <div className="p-3 rounded-2xl bg-gradient-to-r from-blue-500 to-purple-600 shadow-lg">
              <FileText className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Total Reports</p>
              <p className="text-3xl font-bold text-gray-900">{recentReports.length}</p>
            </div>
          </div>
        </div>
        <div className="card p-6 hover:scale-105 transition-all duration-300">
          <div className="flex items-center">
            <div className="p-3 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 shadow-lg">
              <CheckCircle className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Completed</p>
              <p className="text-3xl font-bold text-gray-900">{recentReports.filter(r => r.status === 'completed').length}</p>
            </div>
          </div>
        </div>
        <div className="card p-6 hover:scale-105 transition-all duration-300">
          <div className="flex items-center">
            <div className="p-3 rounded-2xl bg-gradient-to-r from-orange-500 to-red-600 shadow-lg">
              <Download className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Downloads</p>
              <p className="text-3xl font-bold text-gray-900">1,247</p>
            </div>
          </div>
        </div>
        <div className="card p-6 hover:scale-105 transition-all duration-300">
          <div className="flex items-center">
            <div className="p-3 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-600 shadow-lg">
              <Calendar className="h-8 w-8 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Scheduled</p>
              <p className="text-3xl font-bold text-gray-900">8</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
