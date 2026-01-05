# Frontend Setup Instructions

## Quick Start

### 1. Install Dependencies

```powershell
cd frontend
npm install
```

This will install:
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **shadcn/ui** utilities (cn helper, CVA)
- **React Three Fiber** for 3D shader backgrounds
- **Framer Motion** for smooth animations
- **Lucide React** for icons

### 2. Start Development Server

```powershell
npm run dev
```

The app will be available at: **http://localhost:3000**

### 3. View the Demo

Navigate to: **http://localhost:3000/demo**

You'll see:
- Animated shader background (subtle paper texture effect)
- Fintech landing page with smooth animations
- Proper layering (background stays behind, no pointer event blocking)

---

## Project Architecture

### File Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── demo/
│   │   └── page.tsx             # Demo page composing components
│   ├── globals.css              # Tailwind + theme variables
│   ├── layout.tsx               # Root layout with Inter font
│   └── page.tsx                 # Home page
│
├── components/
│   └── ui/                      # UI component library (shadcn convention)
│       ├── background-paper-shaders.tsx  # WebGL shader background
│       └── fin-tech-landing-page.tsx     # Landing page sections
│
├── lib/
│   └── utils.ts                 # Utility functions (cn helper)
│
├── tailwind.config.ts           # Tailwind configuration
├── components.json              # shadcn/ui setup
├── tsconfig.json                # TypeScript config
└── package.json                 # Dependencies
```

### Component Design Decisions

#### 1. BackgroundPaperShaders
**Props:** `className?: string`

**Architecture:**
- Uses `"use client"` directive (React Three Fiber requires client-side rendering)
- Fixed positioning: `position: fixed`, `z-index: -1`
- Pointer events disabled: `pointerEvents: "none"` (UI remains fully interactive)
- Canvas fills viewport: `100vw` x `100vh`
- Shader uniforms: `uTime` (animation), `uResolution` (responsive)

**Why this approach:**
- Performance: GPU-accelerated shader rendering
- Separation: Background completely independent from UI layer
- Accessibility: No interference with interactive elements

#### 2. FinTechLandingPage
**Props:** `className?: string`

**Architecture:**
- Fully presentational component (no business logic)
- Sections: Hero, Features (grid), Benefits (list + visualization), CTA, Footer
- Animations via Framer Motion: stagger reveals, hover effects
- Icons from Lucide React (tree-shakable, consistent)

**Why this approach:**
- Trust-first design: Calm colors, clear typography, no flashy claims
- Fintech conventions: Data visualization, feature cards, disclaimers
- Composable: Can extract sections into separate components

#### 3. Demo Page Composition
**Pattern:** Background + Content layer

```tsx
<div className="relative min-h-screen">
  <BackgroundPaperShaders />  {/* z-index: -1, fixed, no events */}
  <div className="relative z-10">
    <FinTechLandingPage />    {/* z-index: 10, normal flow */}
  </div>
</div>
```

**Why this pattern:**
- Clean separation of concerns
- Easy to swap backgrounds or landing pages
- No z-index conflicts
- Predictable stacking context

---

## Styling System

### Tailwind Configuration

**Theme Variables (Light Mode):**
```css
--background: 0 0% 100%        /* Pure white */
--foreground: 222.2 84% 4.9%   /* Near black */
--primary: 222.2 47.4% 11.2%   /* Dark blue */
--muted: 210 40% 96.1%         /* Light grey */
--border: 214.3 31.8% 91.4%    /* Subtle border */
--radius: 0.5rem               /* Border radius */
```

**Dark Mode:** Automatically inverts via `.dark` class

### Utility Functions

**`cn()` helper:** Merges Tailwind classes intelligently

```typescript
import { cn } from "@/lib/utils"

<div className={cn("base-class", condition && "conditional-class", className)} />
```

---

## Integration with Backend

The FastAPI backend runs on **http://localhost:8000**.

### Connecting the Frontend

Create `lib/api.ts`:

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  return response.json();
}

export async function getPortfolio(token: string) {
  const response = await fetch(`${API_BASE}/api/v1/portfolio/positions`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

export async function getEnhancedAnalysis(ticker: string, token: string) {
  const response = await fetch(`${API_BASE}/api/v1/analysis/enhanced`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ ticker })
  });
  return response.json();
}
```

### Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Performance Considerations

### Why React Three Fiber for Background?

**Alternatives considered:**
1. CSS gradients/animations → Limited visual complexity
2. Canvas 2D → CPU-bound, slower
3. Video background → Large file sizes, not responsive

**Chosen: WebGL shaders**
- GPU-accelerated (60 FPS easily)
- Mathematical precision (noise functions)
- Tiny bundle impact (~5KB shader code)
- Scales to any resolution

### SSR Constraints

**Components marked `"use client"`:**
- `background-paper-shaders.tsx` → Uses React Three Fiber (browser-only)
- `fin-tech-landing-page.tsx` → Uses Framer Motion (browser-only)

**Server components:**
- `app/layout.tsx` → Metadata, font loading
- `app/page.tsx` → Could be server (currently static)

---

## Next Steps

### 1. Add Authentication Pages
```
app/
├── login/
│   └── page.tsx
├── register/
│   └── page.tsx
└── dashboard/
    └── page.tsx
```

### 2. Create Dashboard Components
```
components/ui/
├── portfolio-summary.tsx
├── stock-analysis-card.tsx
├── scenario-chart.tsx
└── risk-gauge.tsx
```

### 3. Add State Management
```powershell
npm install zustand  # Lightweight state manager
```

### 4. Add Form Handling
```powershell
npm install react-hook-form zod
```

---

## Troubleshooting

### Issue: "Module not found: Can't resolve 'three'"
**Solution:** Run `npm install` again, ensure `three` is in dependencies

### Issue: Shader background not showing
**Check:**
1. Browser supports WebGL 2
2. Canvas is not hidden by z-index
3. Parent has `position: relative`

### Issue: Framer Motion warnings in console
**Solution:** Ensure components using motion are client components (`"use client"`)

### Issue: Tailwind classes not applying
**Check:**
1. `globals.css` imported in `layout.tsx`
2. Content paths in `tailwind.config.ts` are correct
3. Run `npm run dev` to rebuild

---

## Production Build

```powershell
npm run build
npm start
```

**Output:**
- Static HTML for pages without dynamic data
- Optimized JavaScript bundles
- Minified CSS
- Image optimization (if using Next.js Image)

**Deployment targets:**
- Vercel (recommended, zero-config)
- Netlify
- Docker (with Node.js runtime)
- Any Node.js hosting

---

## Summary

✅ **Next.js 14** with App Router
✅ **TypeScript** for type safety
✅ **Tailwind CSS** with theme system
✅ **shadcn/ui** conventions (`/components/ui`)
✅ **React Three Fiber** shader background
✅ **Framer Motion** smooth animations
✅ **Lucide React** icon system
✅ **Proper z-index layering** (background behind, content above)
✅ **No SSR breakage** (client components marked)
✅ **Production-ready** structure

**Ready for:** Authentication flow, dashboard UI, API integration, deployment
