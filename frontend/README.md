# Frontend - Hoax Detection News App

React frontend untuk menampilkan berita dan hasil deteksi hoaks.

## Features

- Modern React dengan Vite
- Responsive design
- Real-time data fetching
- Clean & intuitive UI
- Hoax detection visualization

## Installation

```bash
npm install
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env`:
```env
VITE_API_URL=http://localhost:8000/api
```

## Running

### Development
```bash
npm run dev
```

Open browser: `http://localhost:3000`

### Build for Production
```bash
npm run build
```

Output will be in `dist/` folder

### Preview Production Build
```bash
npm run preview
```

### Using Scripts
```bash
# Windows
run.bat

# Linux/Mac
chmod +x run.sh
./run.sh
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   │   ├── NewsCard.jsx     # Individual news card
│   │   └── NewsList.jsx     # News list container
│   ├── services/        # API integration
│   │   └── api.js          # API calls
│   ├── styles/         # CSS files
│   │   └── index.css       # Global styles
│   ├── App.jsx         # Main component
│   └── main.jsx        # Entry point
├── index.html
├── vite.config.js
└── package.json
```

## Components

### App.jsx
Main application component:
- Manages state (news, loading, error)
- Handles data fetching
- Renders header and news list

### NewsList.jsx
List container component:
- Displays loading state
- Handles errors
- Renders NewsCard components

### NewsCard.jsx
Individual news card:
- Displays news information
- Shows hoax label and confidence
- Provides link to original article

## Styling

Custom CSS with:
- Responsive grid layout
- Gradient backgrounds
- Hover effects
- Color-coded hoax indicators
- Mobile-friendly design

## API Integration

Uses Axios for API calls:
```javascript
import { newsAPI } from './services/api';

// Get all news
const data = await newsAPI.getAllNews();

// Fetch new RSS
const result = await newsAPI.fetchRSS();
```

## Deployment

### Vercel (Recommended)
```bash
npm run build
# Deploy dist/ folder to Vercel
```

### Netlify
```bash
npm run build
# Deploy dist/ folder to Netlify
```

### Firebase Hosting
```bash
npm run build
firebase init hosting
firebase deploy
```

## Environment Variables

For production, update `.env`:
```env
VITE_API_URL=https://your-backend-api.com/api
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Dependencies

- React 18
- Vite 5
- Axios
- No additional UI libraries (pure CSS)

## Performance

- Lazy loading images
- Optimized bundle size
- Fast refresh in development
- Production build optimizations

## License

Educational project
