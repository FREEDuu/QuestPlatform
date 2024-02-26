import * as React from 'react';
import { AppBar, Toolbar, Typography, IconButton, useScrollTrigger, Link } from '@mui/material';
import { Box } from '@mui/system';
import HomeIcon from '@mui/icons-material/Home';
import AlarmIcon from '@mui/icons-material/Alarm';
import SportsEsportsIcon from '@mui/icons-material/SportsEsports';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import PersonIcon from '@mui/icons-material/Person';
import '../styles/Home.css'

const pages = [
  { name: 'Home', icon: <HomeIcon />, path: '/' },
  { name: 'Test', icon: <AlarmIcon />, path: '/test' },
  { name: 'Sfide', icon: <SportsEsportsIcon />, path: '/sfide' },
  { name: 'Logout', icon: <ExitToAppIcon />, path: '/logout' },
  { name: 'Profile', icon: <PersonIcon />, path: '/profile' },
];


export default function Home() {
  return (
    <React.Fragment>
        <AppBar sx={{ position: 'fixed', top: 0, zIndex: 1000 }}>
          <Toolbar disableGutters>
            <Typography variant="h6" noWrap component="div" sx={{ mr: 2, display: { xs: 'none', md: 'flex' } }}>
              Your App Name
            </Typography>
            <Box sx={{ flexGrow: 1, display: { xs: 'flex', md: 'none' } }}>
              <IconButton size="large" aria-label="menu" sx={{ color: 'white' }}>
                {/* Your App Menu Icon */}
              </IconButton>
            </Box>
            {pages.map((page) => (
              <Link key={page.name} href={page.path} underline="none" color="inherit">
                {page.name}
                <IconButton size="large" aria-label={page.name} sx={{ color: 'white' }}>
                  {page.icon}
                </IconButton>
              </Link>
            ))}
          </Toolbar>
        </AppBar>
    </React.Fragment>
  );
}
