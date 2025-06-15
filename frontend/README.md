# 🎨 AdWise AI Frontend Application

Modern React + TypeScript frontend for the AdWise AI Digital Marketing Campaign Builder.

## 🚀 Quick Start

### Prerequisites
- Node.js 18 or higher
- npm or yarn package manager

### Installation & Setup

1. **Install dependencies:**
```bash
npm install
```

2. **Start development server:**
```bash
npm run dev
```

3. **Access the application:**
- Frontend: http://localhost:3000 (or next available port)
- Backend API: http://127.0.0.1:8002 (must be running)

## 🛠️ Technology Stack

- **⚛️ React 18** - Modern React with hooks and concurrent features
- **📘 TypeScript** - Type-safe JavaScript development
- **⚡ Vite** - Fast build tool and development server
- **🎨 Tailwind CSS** - Utility-first CSS framework
- **🔄 React Query** - Server state management and caching
- **🧭 React Router v6** - Client-side routing
- **📊 Recharts** - Data visualization and charts
- **🌐 Axios** - HTTP client with interceptors
- **🎯 React Hook Form** - Form management and validation

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   └── Layout.tsx      # Main application layout
│   ├── pages/              # Page components
│   │   ├── Dashboard.tsx   # Analytics dashboard
│   │   ├── Campaigns.tsx   # Campaign management
│   │   ├── Ads.tsx         # Ad management
│   │   ├── Analytics.tsx   # Detailed analytics
│   │   ├── Teams.tsx       # Team management
│   │   ├── Users.tsx       # User management
│   │   ├── Reports.tsx     # Report generation
│   │   └── Settings.tsx    # Application settings
│   ├── lib/                # Utilities and configurations
│   │   └── api.ts          # API client and endpoints
│   ├── App.tsx             # Main application component
│   ├── main.tsx            # Application entry point
│   └── index.css           # Global styles and Tailwind
├── public/                 # Static assets
├── index.html              # HTML template
├── package.json            # Dependencies and scripts
├── tailwind.config.js      # Tailwind CSS configuration
├── postcss.config.js       # PostCSS configuration
├── tsconfig.json           # TypeScript configuration
└── vite.config.ts          # Vite configuration
```

## 🎯 Key Features

### 📊 Dashboard
- Real-time performance metrics
- Interactive charts and visualizations
- Campaign overview and insights
- Recent activity tracking

### 🎯 Campaign Management
- Create, edit, and manage campaigns
- Campaign status tracking
- Budget management and monitoring
- Performance analytics integration

### 📢 Ad Management
- Multi-platform ad creation
- AI-powered ad generation
- Performance tracking and optimization
- Platform-specific configurations

### 📈 Analytics
- Comprehensive performance metrics
- Time-series data visualization
- Platform distribution analysis
- Campaign comparison tools

### 👥 Team Collaboration
- Team creation and management
- Member role assignments
- Real-time collaboration features
- Activity tracking and notifications

## 🔧 Configuration

### Environment Variables
The frontend uses Vite's environment variable system. Create a `.env.local` file:

```env
# API Configuration
VITE_API_BASE_URL=http://127.0.0.1:8002
VITE_API_TIMEOUT=10000

# Application Configuration
VITE_APP_NAME=AdWise AI
VITE_APP_VERSION=1.0.0
```

### API Proxy
The Vite configuration includes a proxy for API requests:

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
```

## 🎨 Styling & UI

### Tailwind CSS
The application uses Tailwind CSS for styling with a custom design system:

- **Color Palette**: Primary blue theme with semantic colors
- **Typography**: Inter font family for modern readability
- **Components**: Custom button, card, input, and badge components
- **Responsive Design**: Mobile-first approach with breakpoints

### Custom Components
- **Buttons**: Primary, secondary, outline, and ghost variants
- **Cards**: Consistent card layout with shadows and borders
- **Forms**: Styled inputs with focus states and validation
- **Badges**: Status indicators with color coding

## 🔄 State Management

### React Query
Server state is managed using React Query (TanStack Query):

- **Caching**: Automatic caching of API responses
- **Background Updates**: Automatic refetching and synchronization
- **Error Handling**: Comprehensive error states and retry logic
- **Loading States**: Built-in loading and pending states

### Local State
Component state is managed using React hooks:

- **useState**: For simple component state
- **useReducer**: For complex state logic
- **useContext**: For shared state across components

## 🌐 API Integration

### API Client
Centralized API client with interceptors:

```typescript
// src/lib/api.ts
export const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
});

// Request interceptor for authentication
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Endpoint Organization
API endpoints are organized by feature:

- **Analytics**: Performance metrics and insights
- **Campaigns**: Campaign CRUD operations
- **Ads**: Ad management and generation
- **Users**: User management and preferences
- **Teams**: Team collaboration features

## 🧪 Testing

### Running Tests
```bash
# Run unit tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

### Testing Strategy
- **Unit Tests**: Component testing with React Testing Library
- **Integration Tests**: API integration and user flows
- **E2E Tests**: End-to-end testing with Playwright

## 🚀 Build & Deployment

### Development Build
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

### Build Output
The build process creates optimized assets in the `dist/` directory:
- Minified JavaScript and CSS
- Optimized images and assets
- Source maps for debugging

## 🔧 Troubleshooting

### Common Issues

1. **Tailwind CSS not working:**
   - Ensure PostCSS configuration is correct
   - Check that Tailwind directives are in index.css
   - Verify tailwind.config.js content paths

2. **API requests failing:**
   - Check that backend server is running on port 8002
   - Verify proxy configuration in vite.config.ts
   - Check browser network tab for CORS issues

3. **Build errors:**
   - Clear node_modules and reinstall dependencies
   - Check TypeScript errors with `npm run type-check`
   - Verify all imports and exports are correct

### Development Tips
- Use React Developer Tools for debugging
- Enable TypeScript strict mode for better type safety
- Use ESLint and Prettier for code quality
- Monitor bundle size with `npm run analyze`

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React Query Documentation](https://tanstack.com/query/latest)

---

**Built with ❤️ for modern digital marketing teams**
