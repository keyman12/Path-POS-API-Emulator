# Color Customization Guide

All colors are defined as CSS variables at the top of `styles.css`. Simply change the hex values in the `:root` section to customize the entire interface.

## Quick Color Reference

### Primary Colors
- `--path-green` (#2A9D8F) - Used for:
  - Logo text
  - Primary buttons
  - Links and hover states
  - Section borders
  - WebSocket status (connected)
  
- `--path-red` (#E63946) - Used for:
  - Logo handle accent
  - WebSocket received messages border
  - Error states

- `--path-blue` (#457B9D) - Used for:
  - Header gradient
  - Secondary buttons
  - WebSocket sent messages border
  - General UI accents

- `--path-dark-blue` (#1D3557) - Used for:
  - Header background
  - Footer background
  - Headings
  - Form labels

### Supporting Colors
- `--path-charcoal` (#2C3E50) - Text color, response display background
- `--path-white` (#FFFFFF) - Background, text on dark backgrounds
- `--path-grey-light` (#F5F5F5) - Panel backgrounds
- `--path-grey-medium` (#CCCCCC) - Borders, disabled states
- `--path-grey-dark` (#666666) - Secondary text

## How to Change Colors

1. **Open** `frontend/styles.css`
2. **Find** the `:root` section at the top (lines 2-15)
3. **Change** the hex color values
4. **Save** the file
5. **Reload** your browser (the server auto-reloads)

### Example: Change Primary Green to Blue

```css
:root {
    --path-green: #0066CC; /* Changed from #2A9D8F */
    /* ... other colors ... */
}
```

### Example: Change Header Colors

```css
:root {
    --path-dark-blue: #000000; /* Black header */
    --path-blue: #333333;      /* Darker gradient */
    /* ... other colors ... */
}
```

## Color Usage Map

| Element | Color Variable | Current Value |
|---------|---------------|---------------|
| Logo text | `--path-green` | #2A9D8F |
| Logo handle | `--path-red` | #E63946 |
| Header background | `--path-dark-blue` → `--path-blue` | Gradient |
| Primary buttons | `--path-green` | #2A9D8F |
| Secondary buttons | `--path-blue` | #457B9D |
| Section borders | `--path-green` | #2A9D8F |
| Form borders | `--path-grey-medium` | #CCCCCC |
| Form focus | `--path-green` | #2A9D8F |
| Panel backgrounds | `--path-grey-light` | #F5F5F5 |
| Response display | `--path-charcoal` | #2C3E50 |
| Footer | `--path-dark-blue` | #1D3557 |

## Tips

- **Test in browser**: Changes appear immediately after saving (if auto-reload is enabled)
- **Use color picker**: Browser DevTools can help you pick exact colors
- **Maintain contrast**: Ensure text remains readable on backgrounds
- **Keep brand consistency**: Update all related colors together

## Browser DevTools Method

1. Open browser DevTools (F12 or Cmd+Option+I)
2. Go to Elements/Inspector
3. Find the `:root` element
4. Edit CSS variables directly in the Styles panel
5. Copy your changes back to `styles.css`

