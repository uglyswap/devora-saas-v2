# Devora User Guide

Welcome to Devora! This guide will help you build full-stack applications with AI in minutes.

## Table of Contents

1. [Getting Started](#getting-started)
2. [The Editor Interface](#the-editor-interface)
3. [Building with AI](#building-with-ai)
4. [Visual Editing](#visual-editing)
5. [Preview and Testing](#preview-and-testing)
6. [Deploying Your App](#deploying-your-app)
7. [Templates and Marketplace](#templates-and-marketplace)
8. [Tips and Best Practices](#tips-and-best-practices)

---

## Getting Started

### Creating Your First Project

1. **Open Devora** at [devora.app](https://devora.app)
2. **Sign in** with your account (or continue as guest for quick prototyping)
3. **Click "New Project"** or start typing in the chat
4. **Describe what you want to build** - be as specific as possible

**Example prompts to get started:**

```
"Create a modern landing page for a productivity app called TaskFlow"

"Build a dashboard with user analytics, charts, and a sidebar navigation"

"Make an e-commerce product page with image gallery, reviews, and add to cart"
```

### Understanding the Workflow

Devora uses a multi-agent AI system:

```
Your Request
     │
     ▼
┌─────────────┐
│  Architect  │  Plans the structure
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Frontend   │  Builds UI components
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Backend    │  Creates API logic
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Reviewer   │  Checks quality
└──────┬──────┘
       │
       ▼
   Your App!
```

---

## The Editor Interface

### Overview

```
┌────────────────────────────────────────────────────────────┐
│ [Logo] [Project Name]                    [Deploy] [Share]  │
├──────────┬────────────────────────┬────────────────────────┤
│          │                        │                        │
│  File    │    Code Editor         │      Preview           │
│  Tree    │    (Monaco)            │      (WebContainer)    │
│          │                        │                        │
├──────────┼────────────────────────┤                        │
│          │                        │                        │
│  Chat    │    Terminal Output     │                        │
│  Panel   │                        │                        │
│          │                        │                        │
└──────────┴────────────────────────┴────────────────────────┘
```

### Panels

#### File Tree (Left)
- Browse all project files
- Create, rename, delete files
- Drag to reorganize
- Search files with `Ctrl/Cmd + P`

#### Code Editor (Center)
- Monaco editor (same as VS Code)
- Full syntax highlighting
- IntelliSense autocomplete
- Multiple tabs
- Split view support

#### Preview (Right)
- Live preview using WebContainers
- Runs actual Node.js in browser
- Hot reload on changes
- Terminal output below

#### Chat Panel (Bottom Left)
- Communicate with AI
- Request changes
- Ask questions about your code

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + K` | Open command palette |
| `Ctrl/Cmd + S` | Save current file |
| `Ctrl/Cmd + P` | Quick file search |
| `Ctrl/Cmd + B` | Toggle sidebar |
| `Ctrl/Cmd + /` | Focus chat |
| `Ctrl/Cmd + Enter` | Send chat message |
| `Ctrl/Cmd + Shift + E` | Toggle file explorer |
| `Ctrl/Cmd + Shift + P` | Toggle preview |
| `Escape` | Close dialogs/panels |

---

## Building with AI

### Writing Effective Prompts

**Good prompts are:**
- Specific about what you want
- Clear about design preferences
- Include technical requirements

**Example Good Prompt:**
```
Create a user authentication page with:
- Email and password login form
- "Remember me" checkbox
- Forgot password link
- Social login buttons (Google, GitHub)
- Modern design with a split layout
- Form validation with helpful error messages
- Use Tailwind CSS for styling
```

**Example Weak Prompt:**
```
Make a login page
```

### Iterative Development

Build your app step by step:

1. **Start with the structure**
   ```
   Create the basic layout with header, sidebar, and main content area
   ```

2. **Add features incrementally**
   ```
   Add a user profile dropdown in the header with avatar and menu
   ```

3. **Refine the design**
   ```
   Make the sidebar collapsible and add hover effects to menu items
   ```

4. **Add functionality**
   ```
   Connect the login form to a mock authentication API
   ```

### Refining Generated Code

Use follow-up prompts to refine:

```
"Make the button larger and change the color to blue"

"Add animation when the modal opens"

"The form should validate on blur, not just on submit"

"Add loading states to all buttons"
```

### Debugging with AI

When something doesn't work:

```
"I'm getting this error: [paste error message]"

"The sidebar isn't scrolling properly on mobile"

"Why is the button click not working?"
```

---

## Visual Editing

### Select & Edit Mode

1. **Enable Select Mode** by clicking the cursor icon or pressing `S`
2. **Hover** over elements in the preview to highlight them
3. **Click** to select an element
4. **Choose from quick suggestions** or type custom instructions

### Quick Suggestions

When you select an element, you'll see context-aware suggestions:

**For Buttons:**
- Change color
- Add icon
- Make rounded
- Add hover effect
- Change text

**For Text:**
- Change font size
- Make bold/italic
- Change color
- Adjust spacing

**For Containers:**
- Change background
- Add border
- Adjust padding
- Change layout

### Custom Edits

Type any instruction:

```
"Make this button pulse when hovered"

"Add a gradient background from blue to purple"

"Center this text and make it larger"

"Add a shadow and rounded corners"
```

---

## Preview and Testing

### WebContainer Preview

The preview runs actual Node.js code in your browser:

1. **Automatic hot reload** - changes appear instantly
2. **Full npm support** - install any package
3. **Terminal access** - see build output and errors
4. **Network requests** - make API calls (with limitations)

### Preview Controls

| Button | Action |
|--------|--------|
| ▶ Play | Start/restart preview |
| ↻ Refresh | Reload the preview |
| ⛶ Fullscreen | Expand preview |
| ↗ External | Open in new tab |
| 📋 Copy URL | Copy preview URL |

### Terminal

The terminal shows:
- npm install progress
- Build output
- Runtime errors
- Console logs

**Color coding:**
- 🔵 Blue: System messages
- ⚪ White: Standard output
- 🔴 Red: Errors

### Device Preview

Test on different screen sizes:
- Desktop (default)
- Tablet
- Mobile
- Custom dimensions

---

## Deploying Your App

### One-Click Deploy

Deploy to production in seconds:

1. **Click "Deploy"** in the header
2. **Choose a provider:**
   - Vercel (recommended for Next.js)
   - Netlify (great for static sites)
   - Cloudflare Pages (edge deployment)
3. **Connect your account** (one-time setup)
4. **Click "Deploy Now"**
5. **Get your live URL!**

### Provider Comparison

| Provider | Best For | Build Time | Free Tier |
|----------|----------|------------|-----------|
| Vercel | Next.js, React | ~30s | Generous |
| Netlify | Static sites, Forms | ~45s | Generous |
| Cloudflare | Edge, Performance | ~20s | Generous |

### Deployment Settings

**Project Name:**
- Determines your URL (e.g., `my-app.vercel.app`)
- Must be unique
- Lowercase letters, numbers, and hyphens only

**Framework Detection:**
- Automatic for most projects
- Can override if needed

**Environment Variables:**
- Add API keys and secrets
- Never commit these to code

### Custom Domains

1. Deploy your app first
2. Go to your provider's dashboard
3. Add your custom domain
4. Update DNS records
5. SSL is automatic

---

## Templates and Marketplace

### Using Templates

1. **Open Marketplace** from the sidebar
2. **Browse categories:**
   - Landing Pages
   - Dashboards
   - E-commerce
   - Portfolios
   - And more...
3. **Preview** templates before using
4. **Click "Use Template"**
5. **Customize** with AI or manually

### Template Categories

| Category | Description |
|----------|-------------|
| Landing | Marketing and product pages |
| Dashboard | Admin panels and analytics |
| E-commerce | Online stores and shops |
| Blog | Content and publishing |
| Portfolio | Personal and agency sites |
| SaaS | Software as a service apps |
| Mobile | Mobile-first applications |
| API | Backend and API templates |
| Full Stack | Complete applications |
| Components | Reusable UI components |

### Creating Your Own Templates

1. Build an awesome project
2. Click "Publish as Template"
3. Add description and tags
4. Set pricing (free or premium)
5. Submit for review
6. Earn when others use it!

---

## Tips and Best Practices

### For Best Results

1. **Be specific** - The more detail, the better the output
2. **Iterate** - Build step by step, not all at once
3. **Review code** - AI is great but not perfect
4. **Use visual editing** - For quick styling changes
5. **Save often** - Use `Ctrl/Cmd + S` frequently

### Performance Tips

1. **Keep files focused** - Split large files
2. **Use lazy loading** - For images and components
3. **Minimize dependencies** - Only install what you need
4. **Optimize images** - Use WebP format
5. **Enable caching** - In your deployment settings

### Common Issues

**Preview not loading?**
- Check terminal for errors
- Verify package.json is valid
- Try clicking "Restart" button

**AI not understanding?**
- Be more specific in your prompt
- Provide examples of what you want
- Break complex requests into steps

**Deployment failing?**
- Check build logs
- Verify all dependencies are installed
- Ensure environment variables are set

### Getting Help

- 📚 [Documentation](https://docs.devora.app)
- 💬 [Discord Community](https://discord.gg/devora)
- 🐛 [Report a Bug](https://github.com/devora/devora-saas-v2/issues)
- 📧 [Email Support](mailto:support@devora.app)

---

## Next Steps

Now that you know the basics:

1. **Try a template** - Start with a pre-built design
2. **Join Discord** - Connect with other builders
3. **Share your creations** - We love seeing what you build!
4. **Contribute** - Help make Devora even better

Happy building!
