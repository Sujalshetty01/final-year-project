import React, { useState } from 'react';
import PropTypes from 'prop-types';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  TextField,
  Chip,
  Stack,
} from '@mui/material';
const getStatusColor = (label) => {
  if (!label) return 'default';
  if (label.toLowerCase().includes('malware')) return 'error';
  if (label.toLowerCase().includes('benign')) return 'success';
  if (label.toLowerCase().includes('suspicious')) return 'warning';
  return 'info';
};
const HistoryTable = ({ history, onSelect }) => {
  const [search, setSearch] = useState('');
  const filtered =
    history && history.length > 0
      ? history.filter(
          (item) =>
            String(item.filename).toLowerCase().includes(search.toLowerCase()) ||
            (item.label && String(item.label).toLowerCase().includes(search.toLowerCase())),
        )
      : [];
  return (
    <TableContainer component={Paper} sx={{ mt: 3 }}>
      {' '}
      <Stack direction="row" alignItems="center" justifyContent="space-between" p={2}>
        {' '}
        <Typography variant="h6" fontWeight={600}>
          {' '}
          Analysis History{' '}
        </Typography>{' '}
        <TextField
          size="small"
          variant="outlined"
          placeholder="Search filename or label"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ width: 240 }}
        />{' '}
      </Stack>{' '}
      <Table size="small">
        {' '}
        <TableHead>
          {' '}
          <TableRow>
            {' '}
            <TableCell>Filename</TableCell> <TableCell>Date</TableCell>{' '}
            <TableCell>Status</TableCell> <TableCell>Confidence</TableCell>{' '}
          </TableRow>{' '}
        </TableHead>{' '}
        <TableBody>
          {' '}
          {filtered.length > 0 ? (
            filtered.map((item, idx) => (
              <TableRow key={idx} hover sx={{ cursor: 'pointer' }} onClick={() => onSelect(item)}>
                {' '}
                <TableCell>{String(item.filename)}</TableCell>{' '}
                <TableCell>{String(item.date)}</TableCell>{' '}
                <TableCell>
                  {' '}
                  <Chip
                    label={String(item.label ?? '')}
                    color={getStatusColor(item.label)}
                    size="small"
                  />{' '}
                </TableCell>{' '}
                <TableCell>{(item.confidence * 100).toFixed(2)}%</TableCell>{' '}
              </TableRow>
            ))
          ) : (
            <TableRow>
              {' '}
              <TableCell colSpan={4} align="center">
                No history yet.
              </TableCell>{' '}
            </TableRow>
          )}{' '}
        </TableBody>{' '}
      </Table>{' '}
    </TableContainer>
  );
};
HistoryTable.propTypes = {
  history: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      filename: PropTypes.string,
      date: PropTypes.string,
      label: PropTypes.string,
      confidence: PropTypes.number,
    }),
  ),
  onSelect: PropTypes.func.isRequired,
};
export default HistoryTable;
