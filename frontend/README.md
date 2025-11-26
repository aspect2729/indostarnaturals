# IndoStar Naturals Frontend

React + TypeScript frontend for IndoStar Naturals e-commerce platform.

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Local Development

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at http://localhost:5173

## Project Structure

```
frontend/
├── src/
│   ├── components/   # Reusable UI components
│   ├── pages/        # Page components
│   ├── contexts/     # React contexts
│   ├── hooks/        # Custom React hooks
│   ├── services/     # API service functions
│   ├── utils/        # Utility functions
│   ├── App.tsx       # Main app component
│   ├── main.tsx      # Entry point
│   └── index.css     # Global styles
├── public/           # Static assets
└── index.html        # HTML template
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Routing
- **React Query** - Server state management
- **Axios** - HTTP client
- **Formik + Yup** - Form handling and validation

## Code Style

- Use functional components with hooks
- Follow TypeScript strict mode
- Use Tailwind CSS for styling
- Keep components small and focused
- Write meaningful component and variable names
