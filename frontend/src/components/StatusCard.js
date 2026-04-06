import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
const statusMap = {
  success: { icon: <CheckCircleIcon color="success" />, label: 'Success' },
  error: { icon: <ErrorIcon color="error" />, label: 'Error' },
  warning: { icon: <WarningIcon color="warning" />, label: 'Warning' },
};
const StatusCard = ({ title, value, status = 'success' }) => (
  <Card sx={{ minWidth: 200, m: 1, boxShadow: 2 }}>
    {' '}
    <CardContent>
      {' '}
      <Box display="flex" alignItems="center" mb={1}>
        {' '}
        {statusMap[status]?.icon}{' '}
        <Typography variant="h6" ml={1}>
          {title}
        </Typography>{' '}
      </Box>{' '}
      <Typography variant="h4" fontWeight={600}>
        {value}
      </Typography>{' '}
    </CardContent>{' '}
  </Card>
);
export default StatusCard;
