# LensCraft - Professional Photography Platform

A mesmerizing, modern frontend for the LensCraft photography platform built with React, Tailwind CSS, and Framer Motion.

## ✨ Features

- **Stunning UI/UX**: Glassmorphism design with smooth animations
- **Responsive Design**: Works perfectly on all devices
- **Modern Tech Stack**: React 18, Vite, Tailwind CSS, Framer Motion
- **Multiple Pages**: Home, About, Services, Portfolio, Pricing, Contact, Login, Register, Dashboard
- **Interactive Components**: Animated navigation, photo gallery, forms
- **Ready for GitHub Pages**: Static site optimized for deployment

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📁 Project Structure

```
photoshoot-frontend/
├── src/
│   ├── components/     # Reusable components (Navbar, Footer)
│   ├── pages/          # Page components
│   ├── hooks/          # Custom hooks
│   ├── assets/         # Static assets
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Public assets
├── dist/               # Production build
└── package.json
```

## 🌐 Deploy to GitHub Pages

1. Create a new repository on GitHub
2. Push this code to the repository
3. Enable GitHub Pages in repository settings
4. Your site will be live!

Or use automated deployment:

```bash
npm install -g gh-pages
gh-pages -d dist
```

## 🎨 Customization

### Colors
Edit `tailwind.config.cjs` to customize the color scheme:
- primary: #6366f1 (Indigo)
- secondary: #8b5cf6 (Purple)
- accent: #ec4899 (Pink)
- dark: #0f172a (Dark Slate)
- light: #f8fafc (Off-white)

### Fonts
The project uses Google Fonts:
- Inter (sans-serif)
- Playfair Display (serif/display)

## 📄 License

MIT License
