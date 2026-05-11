# CSS & Styling (Tailwind CSS v4)

## Core Rule
Use Tailwind utility classes as the primary styling approach. Avoid writing custom CSS unless the utility classes genuinely cannot express the design.

## Class Organization

Order Tailwind classes consistently within an element:
1. Layout (`flex`, `grid`, `block`, `hidden`)
2. Positioning (`relative`, `absolute`, `top-*`, `z-*`)
3. Box model (`w-*`, `h-*`, `p-*`, `m-*`)
4. Typography (`text-*`, `font-*`, `leading-*`)
5. Visual (`bg-*`, `border-*`, `rounded-*`, `shadow-*`)
6. Interactive (`cursor-*`, `hover:*`, `focus:*`)
7. Responsive prefixes (`sm:*`, `md:*`, `lg:*`)

## CSS Custom Properties (Theming)

Use CSS custom properties defined in `index.css` for design tokens (colors, spacing). This project already has light/dark theme support via CSS variables — extend them rather than hardcoding colors.

```css
/* Preferred — uses theme token */
.element { color: var(--color-text-primary); }

/* Avoid — hardcoded, breaks theming */
.element { color: #1a1a1a; }
```

In Tailwind classes, use the CSS variable via arbitrary values only when a semantic token exists: `text-[var(--color-text-primary)]`. For standard Tailwind colors, use them directly.

## Custom CSS

- Add custom CSS only in `index.css` (global) or as a CSS Module (`.module.css`) co-located with the component
- Never use inline `style` props for anything other than truly dynamic values (e.g., calculated widths from JS)
- Do not use `!important`

## Component Variants

Use `clsx` or `tailwind-merge` (`cn()` utility pattern) to conditionally combine classes:

```tsx
import { cn } from '@/lib/utils'

<button className={cn(
  'px-4 py-2 rounded font-medium',
  variant === 'primary' && 'bg-blue-600 text-white hover:bg-blue-700',
  variant === 'secondary' && 'bg-gray-100 text-gray-900 hover:bg-gray-200',
  disabled && 'opacity-50 cursor-not-allowed',
)}>
```

## Dark Mode

This project uses the CSS variables approach for theming. Update `:root` and a dark-mode selector (e.g., `[data-theme="dark"]`) in `index.css` when adding new color tokens.
