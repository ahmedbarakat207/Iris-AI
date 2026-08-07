---
title: Material UI Web Design – Complete Reference
tags: [material-ui, material-design, UI, UX, components, theming, layout, typography, CSS, React, web-design, accessibility]
version: 1.0
audience: frontend developers, UI/UX designers, web developers
prerequisites: HTML, CSS, JavaScript, basic React
---

# Material UI Web Design – Complete Reference

## Introduction

Material Design is a design language created by Google in 2014. It is based on the metaphor of physical paper and ink, using depth, motion, and consistent visual cues to create intuitive, beautiful interfaces. Material UI (MUI) is the most popular React component library implementing Material Design, offering pre-built, customizable components that follow the specification closely.

This document covers design principles, component usage, theming, layout systems, typography, accessibility, and best practices for building Material Design–inspired websites — whether using MUI, plain CSS, or any other framework.

---

## Core Design Principles

### 1. Material as a Metaphor

Material Design treats surfaces as physical sheets of paper existing in 3D space. Elevation, shadows, and z-layers communicate hierarchy and interactivity.

- Surfaces have consistent thickness (1dp).
- Light comes from above, casting shadows downward.
- Higher elevation = larger, softer shadow.

### 2. Bold, Graphic, Intentional

- Typography, color, and imagery are the primary tools for visual hierarchy.
- White space is used generously to create breathing room.
- Color is applied purposefully — not decoratively.

### 3. Motion Provides Meaning

- Animations should reflect real-world physics (easing, inertia).
- Transitions guide the user's attention between states.
- Never animate for decoration alone — every motion should communicate something.

### 4. Adaptive Design

Material Design adapts layouts across screen sizes — from mobile to desktop — using a responsive 12-column grid and breakpoints.

---

## Color System

### Color Palette Structure

Material Design uses a structured color system built on **primary**, **secondary**, and **surface** colors, each with light and dark variants.

| Role            | Purpose                                               |
|-----------------|-------------------------------------------------------|
| Primary         | Main brand color. Used for key UI elements.           |
| Primary Variant | Darker or lighter shade of primary.                   |
| Secondary       | Accent color for interactive elements and highlights. |
| Background      | Page and surface background.                          |
| Surface         | Card and sheet backgrounds.                           |
| Error           | Errors, destructive actions.                          |
| On-Primary      | Text/icons on primary color (usually white).          |
| On-Secondary    | Text/icons on secondary color.                        |
| On-Surface      | Text/icons on surface color (usually dark grey).      |

### Defining a Color Theme in MUI

```jsx
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      light: '#6ec6ff',
      main: '#2196f3',    // Blue 500
      dark: '#0069c0',
      contrastText: '#ffffff',
    },
    secondary: {
      light: '#ff79b0',
      main: '#ff4081',    // Pink A200
      dark: '#c60055',
      contrastText: '#ffffff',
    },
    error: {
      main: '#f44336',
    },
    background: {
      default: '#fafafa',
      paper: '#ffffff',
    },
  },
});
```

### Defining a Color Theme in Plain CSS

```css
:root {
  --color-primary: #2196f3;
  --color-primary-dark: #0069c0;
  --color-primary-light: #6ec6ff;
  --color-secondary: #ff4081;
  --color-error: #f44336;
  --color-background: #fafafa;
  --color-surface: #ffffff;
  --color-on-primary: #ffffff;
  --color-on-surface: #212121;
  --color-on-surface-medium: #757575;
  --color-divider: #bdbdbd;
}
```

### Material Color Palette Reference

Material Design provides a palette of 19 color families, each with 10 shades (50, 100, 200 … 900) plus 4 accent variants (A100, A200, A400, A700).

```
Blue:    #E3F2FD (50) → #2196F3 (500) → #0D47A1 (900)
Red:     #FFEBEE (50) → #F44336 (500) → #B71C1C (900)
Green:   #E8F5E9 (50) → #4CAF50 (500) → #1B5E20 (900)
Purple:  #F3E5F5 (50) → #9C27B0 (500) → #4A148C (900)
Orange:  #FFF3E0 (50) → #FF9800 (500) → #E65100 (900)
Grey:    #FAFAFA (50) → #9E9E9E (500) → #212121 (900)
```

### Dark Mode

Material Design has a well-defined dark mode specification. In dark mode, surfaces use dark grey (not pure black) with color overlays to indicate elevation.

```jsx
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#90caf9' },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
});
```

```css
/* Dark mode with CSS */
@media (prefers-color-scheme: dark) {
  :root {
    --color-background: #121212;
    --color-surface: #1e1e1e;
    --color-on-surface: #ffffff;
    --color-primary: #90caf9;
  }
}
```

---

## Typography

### Type Scale

Material Design defines a type scale with 13 named styles covering all UI text needs.

| Style       | Size  | Weight | Usage                              |
|-------------|-------|--------|------------------------------------|
| h1          | 96px  | 300    | Large display text                 |
| h2          | 60px  | 300    | Display text                       |
| h3          | 48px  | 400    | Section headers                    |
| h4          | 34px  | 400    | Card titles, dialog headers        |
| h5          | 24px  | 400    | Subtitles                          |
| h6          | 20px  | 500    | List headers                       |
| subtitle1   | 16px  | 400    | Secondary headers                  |
| subtitle2   | 14px  | 500    | Supporting titles                  |
| body1       | 16px  | 400    | Primary body text                  |
| body2       | 14px  | 400    | Secondary body text                |
| button      | 14px  | 500    | Button labels (uppercase)          |
| caption     | 12px  | 400    | Captions, helper text              |
| overline    | 10px  | 400    | Labels (uppercase, spaced)         |

### Recommended Font — Roboto

Material Design was designed with Roboto as its default typeface. Import it via Google Fonts:

```html
<link
  href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap"
  rel="stylesheet"
/>
```

```css
body {
  font-family: 'Roboto', sans-serif;
  font-size: 16px;
  line-height: 1.5;
  color: var(--color-on-surface);
}
```

### Typography in MUI

```jsx
import Typography from '@mui/material/Typography';

function Page() {
  return (
    <>
      <Typography variant="h4" gutterBottom>Page Title</Typography>
      <Typography variant="body1">
        This is the main content paragraph with body1 styling.
      </Typography>
      <Typography variant="caption" color="text.secondary">
        Last updated: today
      </Typography>
    </>
  );
}
```

### Configuring Typography in MUI Theme

```jsx
const theme = createTheme({
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: '2.5rem', fontWeight: 300 },
    h4: { fontSize: '2rem', fontWeight: 400 },
    body1: { fontSize: '1rem', lineHeight: 1.6 },
    button: { textTransform: 'none', fontWeight: 500 }, // disable uppercase
  },
});
```

---

## Elevation and Shadows

Elevation communicates the relative depth of components. Material Design defines 24 elevation levels.

| Elevation | Component Example                  |
|-----------|------------------------------------|
| 0         | Background, flat surfaces          |
| 1         | Cards (resting)                    |
| 2         | Cards (hovered), raised buttons    |
| 4         | App bar                            |
| 6         | FAB (resting)                      |
| 8         | Menus, side drawers                |
| 12        | FAB (pressed)                      |
| 16        | Modal side drawers                 |
| 24        | Dialogs                            |

### CSS Shadow Scale

```css
.elevation-1  { box-shadow: 0 1px 3px rgba(0,0,0,.12), 0 1px 2px rgba(0,0,0,.24); }
.elevation-2  { box-shadow: 0 3px 6px rgba(0,0,0,.16), 0 3px 6px rgba(0,0,0,.23); }
.elevation-4  { box-shadow: 0 10px 20px rgba(0,0,0,.19), 0 6px 6px rgba(0,0,0,.23); }
.elevation-8  { box-shadow: 0 14px 28px rgba(0,0,0,.25), 0 10px 10px rgba(0,0,0,.22); }
.elevation-16 { box-shadow: 0 19px 38px rgba(0,0,0,.30), 0 15px 12px rgba(0,0,0,.22); }
```

### Elevation in MUI

```jsx
import Paper from '@mui/material/Paper';

// elevation prop accepts 0–24
<Paper elevation={4}>App bar content</Paper>
<Paper elevation={1}>Card content</Paper>
<Paper elevation={0} variant="outlined">Flat outlined card</Paper>
```

---

## Layout System

### Grid — 12 Column System

Material Design uses a 12-column responsive grid with margins and gutters that adapt per breakpoint.

| Breakpoint | Width        | Columns | Margin | Gutter |
|------------|--------------|---------|--------|--------|
| xs         | 0–599px      | 4       | 16px   | 16px   |
| sm         | 600–959px    | 8       | 24px   | 24px   |
| md         | 960–1279px   | 12      | 24px   | 24px   |
| lg         | 1280–1919px  | 12      | 24px   | 24px   |
| xl         | 1920px+      | 12      | 24px   | 24px   |

### Grid in MUI

```jsx
import Grid from '@mui/material/Grid';

function Layout() {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} sm={6} md={4}>
        {/* Full width on mobile, half on tablet, third on desktop */}
        <Card />
      </Grid>
      <Grid item xs={12} sm={6} md={4}>
        <Card />
      </Grid>
      <Grid item xs={12} sm={12} md={4}>
        <Card />
      </Grid>
    </Grid>
  );
}
```

### Grid in Plain CSS

```css
.grid-container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
  padding: 0 24px;
  max-width: 1280px;
  margin: 0 auto;
}

.col-4  { grid-column: span 4; }
.col-6  { grid-column: span 6; }
.col-12 { grid-column: span 12; }

@media (max-width: 599px) {
  .grid-container { grid-template-columns: repeat(4, 1fr); gap: 16px; padding: 0 16px; }
  .col-4, .col-6 { grid-column: span 4; }
}
```

### Container and Box

```jsx
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';

function Page() {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
        {/* Content */}
      </Box>
    </Container>
  );
}
```

---

## Core Components

### App Bar

The App Bar is the top navigation bar providing brand identity, navigation, and actions.

```jsx
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';

function TopBar() {
  return (
    <AppBar position="sticky" color="primary" elevation={4}>
      <Toolbar>
        <IconButton edge="start" color="inherit" aria-label="menu" sx={{ mr: 2 }}>
          <MenuIcon />
        </IconButton>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          My App
        </Typography>
        <Button color="inherit">Login</Button>
      </Toolbar>
    </AppBar>
  );
}
```

### App Bar in Plain CSS/HTML

```html
<header class="app-bar">
  <div class="toolbar">
    <button class="icon-btn" aria-label="Open menu">☰</button>
    <span class="app-title">My App</span>
    <nav class="app-nav">
      <a href="/login">Login</a>
    </nav>
  </div>
</header>
```

```css
.app-bar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}
.toolbar {
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 64px;
  gap: 16px;
}
.app-title { flex: 1; font-size: 1.25rem; font-weight: 500; }
```

---

### Buttons

Material Design defines three button variants that communicate different levels of emphasis.

| Variant   | Use Case                           | Emphasis  |
|-----------|------------------------------------|-----------|
| Contained | Primary actions (Save, Submit)     | High      |
| Outlined  | Secondary actions (Cancel, Back)   | Medium    |
| Text      | Low-priority, tertiary actions     | Low       |

```jsx
import Button from '@mui/material/Button';

<Button variant="contained" color="primary">Save</Button>
<Button variant="outlined" color="primary">Cancel</Button>
<Button variant="text" color="primary">Learn More</Button>

{/* With icon */}
<Button variant="contained" startIcon={<SaveIcon />}>Save</Button>

{/* Sizes */}
<Button size="small">Small</Button>
<Button size="medium">Medium</Button>
<Button size="large">Large</Button>

{/* Loading state */}
<Button variant="contained" disabled>Saving...</Button>
```

### Buttons in Plain CSS

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
  transition: background-color 0.2s, box-shadow 0.2s;
  border: none;
}

.btn-contained {
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.btn-contained:hover {
  background-color: var(--color-primary-dark);
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.btn-outlined {
  background: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}
.btn-outlined:hover {
  background-color: rgba(33, 150, 243, 0.08);
}

.btn-text {
  background: transparent;
  color: var(--color-primary);
}
.btn-text:hover {
  background-color: rgba(33, 150, 243, 0.08);
}
```

---

### Floating Action Button (FAB)

The FAB is the primary action of a screen — one per page, placed in the bottom-right corner.

```jsx
import Fab from '@mui/material/Fab';
import AddIcon from '@mui/icons-material/Add';

{/* Standard FAB */}
<Fab color="secondary" aria-label="add" sx={{ position: 'fixed', bottom: 24, right: 24 }}>
  <AddIcon />
</Fab>

{/* Extended FAB with label */}
<Fab variant="extended" color="primary">
  <AddIcon sx={{ mr: 1 }} />
  New Post
</Fab>
```

### FAB in Plain CSS

```css
.fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: var(--color-secondary);
  color: white;
  border: none;
  font-size: 24px;
  box-shadow: 0 6px 10px rgba(0,0,0,0.3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: box-shadow 0.2s, transform 0.2s;
  z-index: 100;
}
.fab:hover {
  box-shadow: 0 12px 20px rgba(0,0,0,0.35);
  transform: scale(1.05);
}
```

---

### Cards

Cards are surfaces that display content and actions on a single topic.

```jsx
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import CardMedia from '@mui/material/CardMedia';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

function ArticleCard() {
  return (
    <Card sx={{ maxWidth: 345 }} elevation={2}>
      <CardMedia
        component="img"
        height="140"
        image="/thumbnail.jpg"
        alt="Article thumbnail"
      />
      <CardContent>
        <Typography variant="h6" gutterBottom>Card Title</Typography>
        <Typography variant="body2" color="text.secondary">
          Supporting text that describes the card content in brief.
        </Typography>
      </CardContent>
      <CardActions>
        <Button size="small" color="primary">Share</Button>
        <Button size="small" color="primary">Learn More</Button>
      </CardActions>
    </Card>
  );
}
```

### Cards in Plain CSS/HTML

```html
<div class="card">
  <img class="card-media" src="/thumbnail.jpg" alt="Thumbnail" />
  <div class="card-content">
    <h3 class="card-title">Card Title</h3>
    <p class="card-body">Supporting text describing the card content.</p>
  </div>
  <div class="card-actions">
    <button class="btn btn-text">Share</button>
    <button class="btn btn-text">Learn More</button>
  </div>
</div>
```

```css
.card {
  background: var(--color-surface);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,.12), 0 1px 2px rgba(0,0,0,.24);
  transition: box-shadow 0.2s;
  max-width: 345px;
}
.card:hover { box-shadow: 0 3px 6px rgba(0,0,0,.16), 0 3px 6px rgba(0,0,0,.23); }
.card-media { width: 100%; height: 140px; object-fit: cover; }
.card-content { padding: 16px; }
.card-title { font-size: 1.125rem; font-weight: 500; margin-bottom: 8px; }
.card-body { font-size: 0.875rem; color: var(--color-on-surface-medium); }
.card-actions { padding: 8px; display: flex; gap: 8px; }
```

---

### Text Fields

Text fields allow users to enter and edit text.

```jsx
import TextField from '@mui/material/TextField';

{/* Standard variants */}
<TextField label="Name" variant="outlined" fullWidth />
<TextField label="Email" variant="filled" type="email" />
<TextField label="Message" variant="standard" multiline rows={4} />

{/* With helper text and error */}
<TextField
  label="Password"
  type="password"
  variant="outlined"
  error={!!errorMessage}
  helperText={errorMessage || 'Minimum 8 characters'}
  fullWidth
/>

{/* Controlled input */}
<TextField
  label="Search"
  value={query}
  onChange={(e) => setQuery(e.target.value)}
  variant="outlined"
  size="small"
/>
```

### Text Fields in Plain CSS

```css
.text-field {
  position: relative;
  margin-bottom: 24px;
}

.text-field input, .text-field textarea {
  width: 100%;
  padding: 16px 12px 8px;
  border: 1px solid var(--color-divider);
  border-radius: 4px;
  font-size: 1rem;
  font-family: 'Roboto', sans-serif;
  background: transparent;
  color: var(--color-on-surface);
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.text-field input:focus, .text-field textarea:focus {
  border-color: var(--color-primary);
  border-width: 2px;
}

.text-field label {
  position: absolute;
  top: 50%;
  left: 12px;
  transform: translateY(-50%);
  font-size: 1rem;
  color: var(--color-on-surface-medium);
  pointer-events: none;
  transition: all 0.2s;
}

.text-field input:focus ~ label,
.text-field input:not(:placeholder-shown) ~ label {
  top: 4px;
  font-size: 0.75rem;
  color: var(--color-primary);
  transform: none;
}

.helper-text {
  font-size: 0.75rem;
  margin-top: 4px;
  color: var(--color-on-surface-medium);
}

.text-field.error input { border-color: var(--color-error); }
.text-field.error label { color: var(--color-error); }
.text-field.error .helper-text { color: var(--color-error); }
```

---

### Navigation Drawer

The navigation drawer provides access to destinations and app features. It can be permanent, persistent, or temporary (modal).

```jsx
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';
import HomeIcon from '@mui/icons-material/Home';
import SettingsIcon from '@mui/icons-material/Settings';

function NavDrawer({ open, onClose }) {
  return (
    <Drawer anchor="left" open={open} onClose={onClose}>
      <Box sx={{ width: 280 }} role="navigation">
        <Box sx={{ p: 2 }}>
          <Typography variant="h6">My App</Typography>
        </Box>
        <Divider />
        <List>
          {[
            { text: 'Home', icon: <HomeIcon /> },
            { text: 'Settings', icon: <SettingsIcon /> },
          ].map(({ text, icon }) => (
            <ListItem button key={text}>
              <ListItemIcon>{icon}</ListItemIcon>
              <ListItemText primary={text} />
            </ListItem>
          ))}
        </List>
      </Box>
    </Drawer>
  );
}
```

---

### Dialogs (Modals)

Dialogs inform users about tasks and require decisions or additional information.

```jsx
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogActions from '@mui/material/DialogActions';

function ConfirmDialog({ open, onClose, onConfirm }) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Confirm Delete</DialogTitle>
      <DialogContent>
        <DialogContentText>
          This action cannot be undone. Are you sure you want to delete this item?
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={onConfirm} color="error" variant="contained">
          Delete
        </Button>
      </DialogActions>
    </Dialog>
  );
}
```

---

### Snackbars (Toasts)

Snackbars provide brief messages about app processes at the bottom of the screen.

```jsx
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';

function Notification({ open, onClose, message, severity }) {
  return (
    <Snackbar
      open={open}
      autoHideDuration={4000}
      onClose={onClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
    >
      <Alert onClose={onClose} severity={severity} variant="filled">
        {message}
      </Alert>
    </Snackbar>
  );
}

// Usage
<Notification open={showSnack} severity="success" message="Saved successfully!" onClose={() => setShowSnack(false)} />
```

---

### Chips

Chips are compact elements representing an attribute, action, or filter.

```jsx
import Chip from '@mui/material/Chip';
import Avatar from '@mui/material/Avatar';

{/* Basic chips */}
<Chip label="React" />
<Chip label="Deletable" onDelete={() => {}} />
<Chip label="Clickable" onClick={() => {}} color="primary" variant="outlined" />

{/* Avatar chip */}
<Chip avatar={<Avatar>U</Avatar>} label="User Name" />

{/* Icon chip */}
<Chip icon={<DoneIcon />} label="Completed" color="success" />
```

---

### Lists

```jsx
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemText from '@mui/material/ListItemText';
import Avatar from '@mui/material/Avatar';

function UserList({ users }) {
  return (
    <List>
      {users.map(user => (
        <ListItem key={user.id} divider secondaryAction={
          <IconButton edge="end"><MoreVertIcon /></IconButton>
        }>
          <ListItemAvatar>
            <Avatar src={user.avatar}>{user.initials}</Avatar>
          </ListItemAvatar>
          <ListItemText
            primary={user.name}
            secondary={user.email}
          />
        </ListItem>
      ))}
    </List>
  );
}
```

---

### Tables

```jsx
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';

function DataTable({ rows }) {
  return (
    <TableContainer component={Paper} elevation={1}>
      <Table>
        <TableHead>
          <TableRow sx={{ bgcolor: 'grey.100' }}>
            <TableCell><strong>Name</strong></TableCell>
            <TableCell><strong>Role</strong></TableCell>
            <TableCell align="right"><strong>Joined</strong></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map(row => (
            <TableRow key={row.id} hover>
              <TableCell>{row.name}</TableCell>
              <TableCell>{row.role}</TableCell>
              <TableCell align="right">{row.joined}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
```

---

### Tabs

```jsx
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';

function PageTabs() {
  const [value, setValue] = React.useState(0);

  return (
    <>
      <Tabs
        value={value}
        onChange={(e, newVal) => setValue(newVal)}
        indicatorColor="primary"
        textColor="primary"
        variant="fullWidth"
      >
        <Tab label="Overview" />
        <Tab label="Details" />
        <Tab label="Reviews" />
      </Tabs>
      {value === 0 && <OverviewPanel />}
      {value === 1 && <DetailsPanel />}
      {value === 2 && <ReviewsPanel />}
    </>
  );
}
```

---

### Progress Indicators

```jsx
import CircularProgress from '@mui/material/CircularProgress';
import LinearProgress from '@mui/material/LinearProgress';

{/* Indeterminate (loading unknown) */}
<CircularProgress />
<LinearProgress />

{/* Determinate (known progress) */}
<CircularProgress variant="determinate" value={75} />
<LinearProgress variant="determinate" value={progress} />

{/* Inline button spinner */}
{loading ? <CircularProgress size={24} /> : <Button>Submit</Button>}
```

---

## Theming and Customization

### Full MUI Theme Setup

```jsx
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary:   { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
  typography: {
    fontFamily: '"Roboto", sans-serif',
    button: { textTransform: 'none' },
  },
  shape: {
    borderRadius: 8,      // applies to all components
  },
  spacing: 8,             // base spacing unit (multiples of 8px)
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: { borderRadius: 24 },  // pill-shaped buttons
      },
    },
    MuiCard: {
      styleOverrides: {
        root: { borderRadius: 12 },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />  {/* Normalize CSS */}
      <MainLayout />
    </ThemeProvider>
  );
}
```

### Dynamic Dark Mode Toggle

```jsx
function App() {
  const [mode, setMode] = React.useState('light');

  const theme = React.useMemo(() =>
    createTheme({ palette: { mode } }),
    [mode]
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Button onClick={() => setMode(m => m === 'light' ? 'dark' : 'light')}>
        Toggle {mode === 'light' ? 'Dark' : 'Light'} Mode
      </Button>
    </ThemeProvider>
  );
}
```

### Using the sx Prop

The `sx` prop is MUI's utility for one-off style customizations using theme tokens.

```jsx
<Box
  sx={{
    bgcolor: 'primary.main',     // theme color token
    color: 'primary.contrastText',
    p: 2,                        // padding: 8px * 2 = 16px
    m: { xs: 1, md: 3 },        // responsive margin
    borderRadius: 2,             // theme shape.borderRadius * 2
    display: 'flex',
    gap: 2,
    '&:hover': { bgcolor: 'primary.dark' },
  }}
>
  Content
</Box>
```

---

## Motion and Animation

### Material Design Easing Curves

| Curve       | Usage                                      | CSS Value                              |
|-------------|--------------------------------------------|-----------------------------------------|
| Standard    | Most transitions (entering + exiting)      | `cubic-bezier(0.4, 0.0, 0.2, 1)`       |
| Decelerate  | Elements entering the screen               | `cubic-bezier(0.0, 0.0, 0.2, 1)`       |
| Accelerate  | Elements leaving the screen                | `cubic-bezier(0.4, 0.0, 1, 1)`         |
| Sharp       | Quick, small transitions                   | `cubic-bezier(0.4, 0.0, 0.6, 1)`       |

### Duration Guidelines

| Transition Type         | Duration  |
|-------------------------|-----------|
| Simple UI elements      | 100–200ms |
| Standard transitions    | 200–300ms |
| Larger surface changes  | 300–500ms |
| Complex orchestrated    | 500ms+    |

### CSS Animation Examples

```css
/* Ripple effect on button click */
.btn { position: relative; overflow: hidden; }
.ripple {
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.4);
  transform: scale(0);
  animation: ripple-effect 0.6s linear;
  pointer-events: none;
}
@keyframes ripple-effect {
  to { transform: scale(4); opacity: 0; }
}

/* Card hover elevation transition */
.card {
  transition: box-shadow 0.2s cubic-bezier(0.4, 0.0, 0.2, 1),
              transform  0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
}
.card:hover {
  box-shadow: 0 8px 16px rgba(0,0,0,0.2);
  transform: translateY(-2px);
}

/* Page fade-in transition */
.page-enter {
  animation: fadeSlideIn 0.3s cubic-bezier(0.0, 0.0, 0.2, 1) forwards;
}
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

### MUI Transitions

```jsx
import Fade from '@mui/material/Fade';
import Slide from '@mui/material/Slide';
import Grow from '@mui/material/Grow';
import Collapse from '@mui/material/Collapse';

{/* Fade in/out */}
<Fade in={visible} timeout={300}>
  <Card>Content</Card>
</Fade>

{/* Slide from bottom */}
<Slide in={open} direction="up" timeout={400}>
  <Paper>Slide content</Paper>
</Slide>

{/* Grow for dialogs and menus */}
<Grow in={show} timeout={200}>
  <Box>Expanded content</Box>
</Grow>
```

---

## Iconography

Material Design uses a consistent icon set — Material Icons — available in five styles.

| Style      | Description                        |
|------------|------------------------------------|
| Filled     | Default solid icons                |
| Outlined   | Outline-only icons                 |
| Rounded    | Rounded corners                    |
| Sharp      | Sharp corners                      |
| Two-tone   | Two-color filled icons             |

### Installing MUI Icons

```bash
npm install @mui/icons-material
```

### Using Icons

```jsx
import HomeIcon from '@mui/icons-material/Home';
import HomeOutlinedIcon from '@mui/icons-material/HomeOutlined';
import FavoriteIcon from '@mui/icons-material/Favorite';

{/* With color and size */}
<HomeIcon color="primary" fontSize="large" />
<FavoriteIcon sx={{ color: 'red', fontSize: 32 }} />

{/* As icon button */}
<IconButton aria-label="favorite" color="secondary">
  <FavoriteIcon />
</IconButton>
```

### Icon Font (No package install)

```html
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet" />

<span class="material-icons">home</span>
<span class="material-icons" style="color: #1976d2; font-size: 32px;">favorite</span>
```

---

## Accessibility

### ARIA Roles and Labels

```jsx
{/* Always label icon-only buttons */}
<IconButton aria-label="Delete item">
  <DeleteIcon />
</IconButton>

{/* Role on custom interactive elements */}
<Box role="button" tabIndex={0} aria-pressed={active} onClick={toggle}>
  Custom Toggle
</Box>

{/* Live regions for dynamic content */}
<Box aria-live="polite" aria-atomic="true">
  {statusMessage}
</Box>
```

### Focus Management

```jsx
{/* Trap focus inside dialogs */}
<Dialog open={open}>
  <DialogTitle>Title</DialogTitle>
  {/* MUI Dialogs handle focus trap automatically */}
</Dialog>

{/* Skip navigation link */}
<a href="#main-content" className="skip-link">
  Skip to main content
</a>
```

```css
.skip-link {
  position: absolute;
  top: -100%;
  left: 16px;
  background: var(--color-primary);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  z-index: 9999;
}
.skip-link:focus { top: 16px; }
```

### Color Contrast

Material Design requires a minimum contrast ratio of:

- **4.5:1** for normal text (body text, captions)
- **3:1** for large text (18px bold or 24px regular)
- **3:1** for UI components (buttons, inputs, icons)

```css
/* Compliant: white text on primary Blue 500 (#2196F3) = 3.1:1 (large text OK) */
/* Compliant: white text on Blue 700 (#1565C0) = 4.9:1 (body text OK) */
/* Non-compliant: Grey 400 (#BDBDBD) on white = 1.8:1 — avoid for text */
```

### Keyboard Navigation

```jsx
{/* All interactive elements must be keyboard accessible */}
<Button>Focusable by default</Button>

{/* Keyboard handler for custom elements */}
function KeyboardCard({ onClick }) {
  const handleKey = (e) => {
    if (e.key === 'Enter' || e.key === ' ') onClick();
  };
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={handleKey}
    >
      Accessible card
    </div>
  );
}
```

---

## Responsive Design Patterns

### Breakpoint Utilities in MUI

```jsx
import { useTheme, useMediaQuery } from '@mui/material';

function ResponsiveComponent() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return isMobile ? <MobileView /> : <DesktopView />;
}
```

### Responsive sx Prop

```jsx
<Typography
  variant="h4"
  sx={{
    fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' },
    textAlign: { xs: 'center', md: 'left' },
  }}
>
  Responsive Title
</Typography>
```

### Responsive CSS

```css
/* Mobile first */
.hero-title { font-size: 1.75rem; text-align: center; }
.hero-grid  { grid-template-columns: 1fr; gap: 16px; }

@media (min-width: 600px) {
  .hero-title { font-size: 2.5rem; }
  .hero-grid  { grid-template-columns: 1fr 1fr; gap: 24px; }
}

@media (min-width: 960px) {
  .hero-title { font-size: 3rem; text-align: left; }
  .hero-grid  { grid-template-columns: repeat(3, 1fr); }
}
```

---

## Common Page Layouts

### Dashboard Layout

```jsx
function DashboardLayout({ children }) {
  return (
    <Box sx={{ display: 'flex' }}>
      {/* Sidebar */}
      <Drawer variant="permanent" sx={{ width: 240 }}>
        <Toolbar />  {/* offset for AppBar */}
        <List>
          <ListItem button><ListItemText primary="Dashboard" /></ListItem>
          <ListItem button><ListItemText primary="Reports" /></ListItem>
          <ListItem button><ListItemText primary="Settings" /></ListItem>
        </List>
      </Drawer>

      {/* Main content */}
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />  {/* offset for AppBar */}
        {children}
      </Box>
    </Box>
  );
}
```

### Landing Page Hero

```jsx
function Hero() {
  return (
    <Box
      sx={{
        minHeight: '80vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        px: 2,
        background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
        color: 'white',
      }}
    >
      <Typography variant="h2" fontWeight={300} gutterBottom>
        Build Something Great
      </Typography>
      <Typography variant="h6" sx={{ mb: 4, opacity: 0.9, maxWidth: 600 }}>
        A brief supporting tagline that explains the value proposition clearly.
      </Typography>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
        <Button variant="contained" color="secondary" size="large">
          Get Started
        </Button>
        <Button variant="outlined" sx={{ color: 'white', borderColor: 'white' }} size="large">
          Learn More
        </Button>
      </Stack>
    </Box>
  );
}
```

### Product Grid (E-commerce)

To display products side-by-side (horizontally), use a `Container` with `maxWidth="lg"` or `"xl"`. If you use `maxWidth="sm"`, the cards will always stack vertically because the container is too narrow.

```jsx
function ProductGrid({ products }) {
  return (
    <Container maxWidth="lg" sx={{ py: 8 }}>
      <Grid container spacing={4}>
        {products.map((product) => (
          <Grid item key={product.id} xs={12} sm={6} md={4} lg={3}>
            <Card>
              <CardMedia
                component="img"
                image={product.image}
                alt={product.title}
                sx={{ height: 200 }}
              />
              <CardContent>
                <Typography variant="h6">{product.title}</Typography>
                <Typography variant="body2" color="text.secondary">
                  ${product.price}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}
```

---

## Best Practices

### Design

- Use only one primary action (FAB or contained button) per screen to establish clear hierarchy.
- Maintain 8px spacing increments for margins, padding, and gaps.
- Apply color sparingly — use it to draw attention to key actions, not for decoration.
- Never use more than two typeface families on a page.
- Keep surfaces flat (elevation 0–2) by default; raise them only to communicate interaction or priority.

### Performance

- Import MUI components individually to enable tree-shaking: `import Button from '@mui/material/Button'`, not `import { Button } from '@mui/material'`.
- Use `sx` for one-off styles; extract repeated styles into `styled()` components or the theme's `components` override.
- Lazy-load heavy components (dialogs, drawers) until needed.
- Preload Google Fonts using `<link rel="preload">` to avoid flash of unstyled text.

### Accessibility

- Test all interactive elements for keyboard navigation (Tab, Enter, Space, Arrow keys).
- Verify color contrast meets WCAG 2.1 AA — minimum 4.5:1 for normal text.
- Provide `aria-label` on all icon-only buttons and icon-only links.
- Use semantic HTML elements (`<nav>`, `<main>`, `<header>`, `<button>`) before reaching for `<div>` with a role.
- Never remove focus outlines without providing an equivalent custom style.

### Consistency

- Define all colors, spacing, and typography in a central theme — never hard-code hex values in component styles.
- Keep component variants consistent across pages (e.g., always use `outlined` for secondary actions).
- Use MUI's built-in `spacing()` function or the `sx` prop's shorthand (`p`, `m`, `gap`) rather than arbitrary pixel values.

---

## Conclusion

Material Design provides a comprehensive, research-backed design system for building interfaces that are intuitive, accessible, and visually consistent. Whether implemented with MUI in React or reproduced in plain HTML/CSS, the principles — intentional color, clear hierarchy, meaningful motion, and adaptive layout — lead to products that feel both familiar and polished. Centralizing design decisions in a theme ensures scalability and consistency as projects grow.
