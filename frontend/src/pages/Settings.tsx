import React, { useState } from 'react';
import {
  User,
  Bell,
  Shield,
  Palette,
  Globe,
  Database,
  Key,
  Mail,
  Smartphone,
  Save,
  RefreshCw,
  Eye,
  EyeOff,
  Check,
} from 'lucide-react';

export function Settings() {
  const [activeTab, setActiveTab] = useState('profile');
  const [showApiKey, setShowApiKey] = useState(false);
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    sms: false,
    campaigns: true,
    reports: true,
  });

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'appearance', name: 'Appearance', icon: Palette },
    { id: 'integrations', name: 'Integrations', icon: Globe },
    { id: 'api', name: 'API Keys', icon: Key },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-xl">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Settings
          </h1>
          <p className="mt-3 text-lg text-gray-600 font-medium">
            Manage your account preferences and application settings
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <nav className="space-y-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center px-4 py-3 text-left rounded-xl transition-all duration-200 ${activeTab === tab.id
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                    : 'text-gray-600 hover:bg-blue-50 hover:text-blue-700'
                  }`}
              >
                <tab.icon className="h-5 w-5 mr-3" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <div className="card p-8">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-900">Profile Information</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      className="input"
                      defaultValue="Admin"
                      placeholder="Enter your first name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      className="input"
                      defaultValue="User"
                      placeholder="Enter your last name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      className="input"
                      defaultValue="admin@adwise.ai"
                      placeholder="Enter your email"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      className="input"
                      defaultValue="+1 (555) 123-4567"
                      placeholder="Enter your phone number"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Bio
                  </label>
                  <textarea
                    className="input min-h-[100px] resize-none"
                    defaultValue="Digital marketing professional with expertise in AI-powered campaign optimization."
                    placeholder="Tell us about yourself"
                  />
                </div>
                <div className="flex justify-end">
                  <button className="btn btn-primary">
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-900">Notification Preferences</h2>
                <div className="space-y-4">
                  {Object.entries(notifications).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div className="flex items-center">
                        {key === 'email' && <Mail className="h-5 w-5 text-blue-500 mr-3" />}
                        {key === 'push' && <Bell className="h-5 w-5 text-green-500 mr-3" />}
                        {key === 'sms' && <Smartphone className="h-5 w-5 text-purple-500 mr-3" />}
                        {key === 'campaigns' && <Globe className="h-5 w-5 text-orange-500 mr-3" />}
                        {key === 'reports' && <Database className="h-5 w-5 text-red-500 mr-3" />}
                        <div>
                          <p className="font-semibold text-gray-900 capitalize">
                            {key === 'push' ? 'Push Notifications' : key} Notifications
                          </p>
                          <p className="text-sm text-gray-600">
                            Receive notifications via {key === 'push' ? 'browser push' : key}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => setNotifications(prev => ({ ...prev, [key]: !value }))}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${value ? 'bg-blue-600' : 'bg-gray-300'
                          }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${value ? 'translate-x-6' : 'translate-x-1'
                            }`}
                        />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-900">Security Settings</h2>
                <div className="space-y-6">
                  <div className="p-6 bg-green-50 border border-green-200 rounded-xl">
                    <div className="flex items-center">
                      <Check className="h-5 w-5 text-green-600 mr-3" />
                      <div>
                        <p className="font-semibold text-green-800">Two-Factor Authentication Enabled</p>
                        <p className="text-sm text-green-600">Your account is protected with 2FA</p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Change Password</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Current Password
                        </label>
                        <input type="password" className="input" placeholder="Enter current password" />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          New Password
                        </label>
                        <input type="password" className="input" placeholder="Enter new password" />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Confirm New Password
                        </label>
                        <input type="password" className="input" placeholder="Confirm new password" />
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex justify-end">
                  <button className="btn btn-primary">
                    <Shield className="h-4 w-4 mr-2" />
                    Update Password
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'api' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-900">API Keys</h2>
                <div className="space-y-4">
                  <div className="p-6 bg-blue-50 border border-blue-200 rounded-xl">
                    <h3 className="font-semibold text-blue-900 mb-2">EURI AI API Key</h3>
                    <div className="flex items-center space-x-3">
                      <input
                        type={showApiKey ? 'text' : 'password'}
                        className="input flex-1"
                        defaultValue="euri_sk_1234567890abcdef"
                        readOnly
                      />
                      <button
                        onClick={() => setShowApiKey(!showApiKey)}
                        className="btn btn-outline"
                      >
                        {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                      <button className="btn btn-secondary">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Regenerate
                      </button>
                    </div>
                    <p className="text-sm text-blue-600 mt-2">
                      This key is used for AI content generation and optimization
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
