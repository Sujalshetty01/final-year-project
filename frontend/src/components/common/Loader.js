import React from 'react';
import { CircularProgress, Box } from '@mui/material';
const Loader = () => (
  <Box display="flex" justifyContent="center" alignItems="center" minHeight={120}>
    {' '}
    <CircularProgress />{' '}
  </Box>
);
export default Loader;
