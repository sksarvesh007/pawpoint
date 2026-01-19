---
applyTo: "frontend/**/*.{ts,tsx,js,jsx}"
---

# Frontend TypeScript/React Instructions

## TypeScript Style
- Use TypeScript for all new files
- Define explicit types for props, state, and function parameters
- Avoid using `any` type - use `unknown` or proper types
- Use interface for object shapes, type for unions/intersections
- Export types alongside components when needed

## React Patterns
- Prefer functional components over class components
- Use React hooks (useState, useEffect, useCallback, useMemo) appropriately
- Mark client-side components with 'use client' directive
- Use Server Components by default (no 'use client' unless needed)
- Avoid prop drilling - use Context API or state management when needed

## Next.js App Router Conventions
- Place pages in `app/` directory with `page.tsx` files
- Use `layout.tsx` for shared layouts
- Use `loading.tsx` for loading states
- Use `error.tsx` for error boundaries
- Follow file-based routing conventions
- Use Server Actions for form submissions and mutations
- Prefer `async` Server Components for data fetching

## Component Structure
- Keep components small and focused
- Extract reusable components to separate files
- Use descriptive component and prop names
- Place shared components in a `components/` directory
- Colocate related files (component, styles, tests)

## Styling
- Use Tailwind CSS utility classes for styling
- Follow Tailwind CSS 4 conventions
- Use CSS modules only when Tailwind is insufficient
- Maintain consistent spacing and color schemes
- Ensure responsive design for mobile, tablet, and desktop

## Performance
- Use `next/image` for image optimization
- Implement proper code splitting
- Use dynamic imports for heavy components
- Minimize client-side JavaScript
- Leverage Server Components for better performance

## State Management
- Use React hooks (useState, useReducer) for local state
- Consider Context API for app-wide state
- Keep state as close to where it's used as possible
- Avoid unnecessary re-renders with useMemo/useCallback

## Error Handling
- Implement error boundaries with `error.tsx`
- Provide user-friendly error messages
- Log errors appropriately for debugging
- Handle loading and error states in UI

## Package Management
- Use Bun for all package operations
- Add dependencies carefully - prefer standard libraries
- Always check for security vulnerabilities before adding new dependencies
- Keep dependencies up to date

## Testing
- Follow existing test patterns if tests are added
- Test critical user flows and edge cases
- Mock external API calls in tests
