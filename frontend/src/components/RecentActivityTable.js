import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
} from '@mui/material';
const RecentActivityTable = ({ data }) => (
  <TableContainer component={Paper} sx={{ mt: 2 }}>
    {' '}
    <Table size="small">
      {' '}
      <TableHead>
        {' '}
        <TableRow>
          {' '}
          <TableCell>Filename</TableCell> <TableCell>Label</TableCell>{' '}
          <TableCell>Confidence</TableCell>{' '}
        </TableRow>{' '}
      </TableHead>{' '}
      <TableBody>
        {' '}
        {data.length === 0 ? (
          <TableRow>
            {' '}
            <TableCell colSpan={3} align="center">
              {' '}
              <Typography variant="body2" color="text.secondary">
                No recent activity.
              </Typography>{' '}
            </TableCell>{' '}
          </TableRow>
        ) : (
          data.map((item, idx) => (
            <TableRow key={idx}>
              {' '}
              <TableCell>{item.filename}</TableCell> <TableCell>{item.label}</TableCell>{' '}
              <TableCell>{(item.confidence * 100).toFixed(2)}%</TableCell>{' '}
            </TableRow>
          ))
        )}{' '}
      </TableBody>{' '}
    </Table>{' '}
  </TableContainer>
);
export default RecentActivityTable;
