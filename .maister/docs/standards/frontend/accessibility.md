# Accessibility

## Semantic HTML First

Use the correct HTML element for the job — it provides keyboard interaction and screen reader support for free.

```tsx
// Correct
<button onClick={handleSubmit}>Submit</button>
<nav aria-label="Main navigation">...</nav>
<main>...</main>

// Wrong — div masquerading as interactive element
<div onClick={handleSubmit}>Submit</div>
```

## Interactive Elements

- Every clickable thing must be a `<button>` or `<a href>` — never a `<div>` or `<span>` with an `onClick`
- All form inputs must have an associated `<label>` (via `for`/`htmlFor` or wrapping)
- Buttons without visible text need `aria-label`: `<button aria-label="Close dialog">✕</button>`

## Keyboard Navigation

- All interactive elements must be reachable and operable via Tab and Enter/Space
- Modals and dialogs must trap focus while open and return focus on close
- Don't remove focus outlines — style them instead: `focus:ring-2 focus:ring-blue-500`

## Color & Contrast

- Text contrast ratio minimum: 4.5:1 for normal text, 3:1 for large text (WCAG AA)
- Never use color as the only means of conveying information — pair it with an icon or text label
- Status indicators (incident severity, assignment status) must have a text label, not just color

## Images & Icons

- Decorative images: `alt=""`
- Informative images: descriptive `alt` text
- Icon-only buttons: always include `aria-label`
- SVG icons used as decoration: `aria-hidden="true"`

## ARIA

Use ARIA only when semantic HTML isn't enough. Common cases:
- `aria-expanded` on disclosure buttons (accordion, dropdown)
- `role="alert"` or `aria-live="polite"` for dynamic status messages (form success/error)
- `aria-label` to disambiguate repeated elements (multiple "Edit" buttons on a list)
