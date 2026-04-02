import React, { useContext } from 'react';
import { NavLink } from 'react-router-dom';
import { ThemeContext } from '../context/ThemeContext';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, IconButton, Box, Typography, Divider, useTheme } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import HistoryIcon from '@mui/icons-material/History';
import InfoIcon from '@mui/icons-material/Info';
import BarChartIcon from '@mui/icons-material/BarChart';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';

const navItems = [
  { label: 'Dashboard', to: '/', icon: <DashboardIcon /> },
  { label: 'Upload', to: '/upload', icon: <CloudUploadIcon /> },
  { label: 'Results', to: '/results', icon: <BarChartIcon /> },
  { label: 'History', to: '/history', icon: <HistoryIcon /> },
  { label: 'About', to: '/about', icon: <InfoIcon /> },
];

const Sidebar = () => {
  const { theme, toggleTheme } = useContext(ThemeContext);
  const muiTheme = useTheme();
  return (
    <Drawer
      variant="permanent"
      sx={{
        width: 220,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: 220,
          boxSizing: 'border-box',
          background: muiTheme.palette.background.paper,
        },
      }}
    >
      <Box display="flex" flexDirection="column" height="100%">
        <Box p={2} pb={0}>
          <Typography variant="h6" fontWeight={700} color="primary">Malware Classifier</Typography>
        </Box>
        <List>
          {navItems.map((item) => (
            <ListItem
              button
              key={item.label}
              component={NavLink}
              to={item.to}
              exact={item.to === '/'}
              sx={{
                transition: 'background 0.2s, color 0.2s, transform 0.15s',
                '&:hover': {
                  background: muiTheme.palette.action.hover,
                  color: muiTheme.palette.primary.main,
                  transform: 'scale(1.03)',
                },
                '&.active': {
                  background: muiTheme.palette.action.selected,
                  color: muiTheme.palette.primary.main,
                  transform: 'scale(1.05)',
                },
              }}
            >
              <ListItemIcon sx={{
                transition: 'transform 0.2s',
                '.MuiListItem-root:hover &': { transform: 'scale(1.2)' },
                '.MuiListItem-root.active &': { transform: 'scale(1.25)' },
              }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItem>
          ))}
        </List>
        <Box flexGrow={1} />
        <Divider />
        <Box p={2} display="flex" alignItems="center" justifyContent="center">
          <IconButton onClick={toggleTheme} color="primary">
            {theme === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
          <Typography ml={1} variant="body2">
            {theme === 'dark' ? 'Light' : 'Dark'} Mode
          </Typography>
        </Box>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
