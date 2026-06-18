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

## CSS Custom Properties (Color Tokens)

All color values use project-specific CSS custom properties via Tailwind's arbitrary value syntax. Never use Tailwind palette names (e.g., `bg-blue-600`) or hardcoded hex values for themed colors.

```tsx
// Correct — uses semantic token, supports light/dark theme
<div className="bg-[var(--color-si-card-bg)] border-[var(--color-si-card-border)]">
<p className="text-[var(--color-si-label)]">
<button className="bg-[var(--color-si-btn)] hover:bg-[var(--color-si-btn-hover)]">

// Avoid — breaks theming
<div className="bg-white border-gray-200">
<button className="bg-blue-600 hover:bg-blue-700">
```

Available token categories (defined in `index.css`): `--color-si-card-*`, `--color-si-label`, `--color-si-input-*`, `--color-si-btn*`, `--color-si-link`. Extend them in `index.css` when adding new color tokens (update both `:root` and dark-mode selectors).

Structural utilities (`flex`, `gap-*`, `rounded-*`, `px-*`, `py-*`, `w-*`) use plain Tailwind classes without custom properties.

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
  variant === 'primary' && 'bg-[var(--color-si-btn)] text-white hover:bg-[var(--color-si-btn-hover)]',
  disabled && 'opacity-50 cursor-not-allowed',
)}>
```

## Dark Mode

This project uses the CSS variables approach for theming. Update `:root` and the dark-mode selector in `index.css` when adding new color tokens.
