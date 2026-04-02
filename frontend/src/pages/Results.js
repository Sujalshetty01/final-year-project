
import React from 'react';
import { useParams } from 'react-router-dom';
import ResultsDisplay from '../components/ResultsDisplay';
import Loader from '../components/common/Loader';
import Notification from '../components/common/Notification';
import { fetchResult } from '../services/api';
import GraphVisualization from '../components/GraphVisualization';
import NetworkGraph from '../components/NetworkGraph';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { useApi } from '../hooks/useApi';

const Results = () => {
  const { id } = useParams();
  const { data: result, loading, error } = useApi(() => fetchResult(id), [id]);

  return (
    <Box display="flex" justifyContent="center" alignItems="flex-start" minHeight="60vh" p={2}>
      <Card sx={{ minWidth: 400, maxWidth: 600, width: '100%', boxShadow: 3 }}>
        <CardContent>
          <Typography variant="h5" fontWeight={700} mb={2}>
            Results
          </Typography>
          {loading && <Loader />}
          <ResultsDisplay result={result} />
          {result && result.graph && (
            <>
              <GraphVisualization graph={result.graph} />
              <NetworkGraph graph={result.graph} />
            </>
          )}
        </CardContent>
      </Card>
      {error && (
        <Notification message={"Failed to fetch result: " + (error.response?.data?.message || error.message)} type="error" />
      )}
    </Box>
  );
};

export default Results;
