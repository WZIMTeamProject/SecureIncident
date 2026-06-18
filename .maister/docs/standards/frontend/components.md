# React Components

## Component Structure

Always use functional components with hooks. No class components.

```tsx
// Preferred structure order within a component file:
// 1. Imports
// 2. Types / interfaces
// 3. Component function
// 4. Sub-components (if small and tightly coupled)
```

## Naming

- **Page-level components**: `SI` prefix + PascalCase — `SILoginPage`, `SIDashboard`, `SIAccountPage`
- **Shared / utility components**: plain PascalCase — `Background`, `Footer`, `IncidentCard`
- Component file name must match the exported component name (`SILoginPage.tsx` exports `SILoginPage`)
- Event handlers: `handle` prefix — `handleSubmit`, `handleStatusChange`
- Boolean props: adjective or `is`/`has` prefix — `disabled`, `isLoading`, `hasError`

## Props

- Define props with a TypeScript interface named `<ComponentName>Props`
- Destructure props in the function signature
- Keep prop lists short — if a component needs more than 6-8 props, consider splitting or composing

```tsx
interface IncidentCardProps {
  incident: Incident
  onAssign: (userId: number) => void
  isLoading?: boolean
}

export function IncidentCard({ incident, onAssign, isLoading = false }: IncidentCardProps) {
  // ...
}
```

## Form Submission

Use React Router's `useFetcher` for form submissions — not controlled state + `useEffect`:

```tsx
export function SILoginPage() {
  const fetcher = useFetcher()
  const busy = fetcher.state !== 'idle'

  return (
    <fetcher.Form method="POST">
      <input name="login" type="text" disabled={busy} />
      <button type="submit" disabled={busy}>
        {busy ? 'Logging in...' : 'Log in'}
      </button>
      {fetcher.data?.error && <p>{fetcher.data.error}</p>}
    </fetcher.Form>
  )
}
```

## State

- Keep state as close to where it's used as possible — lift only when two components genuinely share it
- Use `useState` for local UI state (open/closed, form values)
- Use `useReducer` for multi-field form state or state with complex transitions
- Don't put server data in component state — use React Query or a data-fetching hook

## Hooks

- Extract reusable logic into custom hooks (`useAuth`, `useIncidents`, `useProjectMembers`)
- Custom hooks live in a `hooks/` directory alongside the feature they belong to
- Hook files: `camelCase` starting with `use` (`useAuth.ts`)
- Never call hooks conditionally

## Side Effects

- Use `useEffect` sparingly — prefer event handlers and React Query for data operations
- Always provide a dependency array; never leave it empty unless the effect truly runs once on mount
- Clean up subscriptions, timers, and event listeners in the return function

## Performance

- Don't memoize prematurely — use `useMemo` and `useCallback` only when a profiler shows a problem
- Keep component trees shallow; deeply nested components are hard to debug
