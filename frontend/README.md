# Stock Intelligence Copilot - Frontend

Modern Next.js frontend for the Stock Intelligence Copilot platform.

## Tech Stack

- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui** conventions
- **React Three Fiber** (3D shader backgrounds)
- **Framer Motion** (animations)
- **Lucide React** (icons)

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

### Available Routes

- `/` - Home page
- `/demo` - Demo landing page with animated shader background

## Project Structure

```
frontend/
├── app/
│   ├── demo/
│   │   └── page.tsx          # Demo page
│   ├── globals.css           # Global styles with theme variables
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Home page
├── components/
│   └── ui/
│       ├── background-paper-shaders.tsx  # Animated shader background
│       └── fin-tech-landing-page.tsx     # Landing page component
├── lib/
│   └── utils.ts              # Utility functions (cn helper)
├── components.json           # shadcn/ui config
├── tailwind.config.ts        # Tailwind configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Dependencies
```

## Components

### BackgroundPaperShaders

Client-side animated shader background using React Three Fiber.

**Usage:**
```tsx
import { BackgroundPaperShaders } from "@/components/ui/background-paper-shaders";

<BackgroundPaperShaders />
```

**Props:**
- `className?: string` - Optional CSS classes

**Features:**
- Animated noise-based paper texture
- Subtle color variations
- Fixed positioning, no pointer events
- Automatic z-index: -1

### FinTechLandingPage

Fintech-themed landing page with animations.

**Usage:**
```tsx
import { FinTechLandingPage } from "@/components/ui/fin-tech-landing-page";

<FinTechLandingPage />
```

**Sections:**
- Hero with CTA buttons
- Features grid (4 key features)
- Benefits list with score visualization
- CTA section
- Footer with disclaimer

## Integration with Backend

The backend API runs on `http://localhost:8000`. To connect the frontend:

1. Create an API client in `lib/api.ts`
2. Add environment variables for API base URL
3. Implement authentication flow
4. Connect portfolio and analysis endpoints

Example:
```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getPortfolio(token: string) {
  const response = await fetch(`${API_BASE}/api/v1/portfolio/positions`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}
```

## Styling

The project uses Tailwind CSS with shadcn/ui conventions:

- Theme variables defined in `globals.css`
- Dark mode support via `class` strategy
- Utility-first approach
- Consistent spacing and color system

### Theme Variables

The theme supports light and dark modes with variables:
- `--background`, `--foreground`
- `--primary`, `--secondary`, `--accent`
- `--muted`, `--border`, `--ring`
- `--radius` for border radius

## Building for Production

```bash
npm run build
npm start
```

## License

Proprietary - Stock Intelligence Copilot © 2026
