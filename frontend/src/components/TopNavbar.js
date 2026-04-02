import React, { useContext } from 'react';
import { AppBar, Toolbar, Typography, Box, IconButton, Avatar } from '@mui/material';
import { ThemeContext } from '../context/ThemeContext';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';

const TopNavbar = () => {
  const { theme, toggleTheme } = useContext(ThemeContext);
  return (
    <AppBar position="fixed" color="default" elevation={1} sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <Typography variant="h6" color="primary" sx={{ flexGrow: 1, fontWeight: 700 }}>
          Malware Analytics Dashboard
        </Typography>
        <Box display="flex" alignItems="center">
          <IconButton onClick={toggleTheme} color="primary">
            {theme === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
          <Avatar sx={{ ml: 2, bgcolor: 'primary.main' }}>U</Avatar>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default TopNavbar;
