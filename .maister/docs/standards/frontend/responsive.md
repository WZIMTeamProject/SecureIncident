# Responsive Design

## Mobile-First with Tailwind

Write base styles for mobile, then layer on `sm:`, `md:`, `lg:` prefixes for larger screens. This aligns with Tailwind's default breakpoint system:

| Prefix | Min-width | Target |
|--------|-----------|--------|
| (none) | 0px | Mobile |
| `sm:` | 640px | Large mobile / small tablet |
| `md:` | 768px | Tablet |
| `lg:` | 1024px | Desktop |
| `xl:` | 1280px | Wide desktop |

```tsx
// Mobile-first: stack vertically on mobile, side-by-side on tablet+
<div className="flex flex-col md:flex-row gap-4">
```

## Layout Patterns

- Use `flex` and `grid` for layouts, not absolute positioning
- Prefer `gap-*` over `margin` for consistent spacing between flex/grid children
- Use `max-w-*` with `mx-auto` to constrain content width on large screens
- Sidebars and navigation should collapse on mobile (hamburger menu or bottom nav)

## Touch Targets

Interactive elements must be at least 44×44px on touch devices. Tailwind helpers:
- `min-h-11 min-w-11` (44px = 11 × 4px)
- For small icon buttons, add padding: `p-3` around a 20px icon gives a 44px target

## Typography

- Use `rem`-based font sizes (Tailwind's defaults are rem) — never `px` for font sizes
- Body text minimum: `text-base` (16px) on mobile
- Line height: `leading-relaxed` or `leading-normal` for body text

## Testing

Before marking a feature as done, verify it at mobile (375px), tablet (768px), and desktop (1280px) viewports using browser dev tools. Pay particular attention to:
- Navigation and header
- Forms and input fields
- Tables and data-heavy views (consider horizontal scroll or card layout on mobile)
- Modals and dialogs
