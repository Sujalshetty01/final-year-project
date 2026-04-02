
import React from 'react';
import HistoryTable from '../components/HistoryTable';
import Notification from '../components/common/Notification';
import { fetchHistory } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, Typography, Box, CircularProgress } from '@mui/material';
import { useApi } from '../hooks/useApi';

const History = () => {
  const navigate = useNavigate();
  const { data: history, loading, error } = useApi(fetchHistory, []);

  const handleSelect = (item) => {
    if (item && item.id) {
      navigate(`/results/${item.id}`);
    }
  };

  return (
    <Box display="flex" justifyContent="center" alignItems="flex-start" minHeight="60vh" p={2}>
      <Card sx={{ minWidth: 400, maxWidth: 900, width: '100%', boxShadow: 3 }}>
        <CardContent>
          <Typography variant="h5" fontWeight={700} mb={2}>
            History
          </Typography>
          {loading ? (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="120px">
              <CircularProgress />
            </Box>
          ) : (
            <HistoryTable history={history} onSelect={handleSelect} />
          )}
        </CardContent>
      </Card>
      {error && (
        <Notification message={"Failed to fetch history: " + (error.response?.data?.message || error.message)} type="error" />
      )}
    </Box>
  );
};

export default History;
