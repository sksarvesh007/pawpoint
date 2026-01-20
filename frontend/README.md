# PawPoint Frontend

Modern web application for PawPoint - an AI-powered veterinary engagement platform.

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 16.1.3 | React framework with App Router |
| **React** | 19.2.3 | UI library |
| **TypeScript** | ^5 | Type safety |
| **Tailwind CSS** | ^4 | Utility-first styling |
| **Bun** | Latest | Package manager & runtime |
| **ESLint** | ^9 | Code linting |

### Key Features
- ⚡ **React 19** with React Compiler for automatic optimization
- 🎨 **Tailwind CSS v4** with modern PostCSS integration
- 📦 **Bun** for fast dependency installation and builds
- 🔍 **TypeScript** strict mode for type safety
- 🚀 **Vercel** deployment ready

---

## Prerequisites

- **Node.js** 18.17+ (for compatibility)
- **Bun** 1.0+ (recommended) or npm/yarn/pnpm
- Backend API running on `http://localhost:8000`

---

## Getting Started

### 1. Clone and Navigate

```bash
cd frontend
```

### 2. Install Dependencies

```bash
# Using Bun (recommended)
bun install

# Or using npm
npm install
```

### 3. Environment Setup

Create a `.env.local` file for local development:

```bash
# API endpoint (adjust if backend runs on different port)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Run Development Server

```bash
# Using Bun (recommended)
bun dev

# Or using npm
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

---

## Available Scripts

| Command | Description |
|---------|-------------|
| `bun dev` | Start development server with hot reload |
| `bun build` | Create production build |
| `bun start` | Start production server |
| `bun lint` | Run ESLint |
| `bun type-check` | Run TypeScript type checking |

---

## Project Structure

```
frontend/
├── src/
│   └── app/                    # Next.js App Router
│       ├── layout.tsx          # Root layout
│       ├── page.tsx            # Home page
│       ├── globals.css         # Global styles
│       └── favicon.ico         # App favicon
├── public/                     # Static assets
├── package.json                # Dependencies & scripts
├── tsconfig.json               # TypeScript config
├── next.config.ts              # Next.js config
├── postcss.config.mjs          # PostCSS + Tailwind
└── eslint.config.mjs           # ESLint config
```

---

## Development Guidelines

### Code Quality

- **Linting**: ESLint with Next.js recommended rules
- **Type Checking**: Strict TypeScript compilation
- **Formatting**: Consistent code style enforced by ESLint

### Styling

This project uses **Tailwind CSS v4** with the new PostCSS plugin:

```tsx
// Example component with Tailwind
export function Button({ children }) {
  return (
    <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
      {children}
    </button>
  );
}
```

---

## Deployment

### Vercel (Recommended)

The easiest deployment option. Simply connect your GitHub repo to Vercel.

```bash
# Or deploy via CLI
bunx vercel
```

### Docker (Optional)

```bash
# Build and run with Docker Compose from root
docker compose up frontend
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API endpoint | `http://localhost:8000` |

---

## Troubleshooting

### Common Issues

**Port 3000 already in use:**
```bash
bun dev --port 3001
```

**Type errors after pulling changes:**
```bash
bun type-check
```

**Clear cache and reinstall:**
```bash
rm -rf node_modules .next
bun install
```

---

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [React 19 Documentation](https://react.dev)
- [Tailwind CSS v4](https://tailwindcss.com/docs)
- [Bun Documentation](https://bun.sh/docs)
