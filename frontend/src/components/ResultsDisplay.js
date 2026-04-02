import React from 'react';
import PropTypes from 'prop-types';
import { Box, Typography, Paper, Chip, Stack, Divider } from '@mui/material';

const getRiskColor = (risk) => {
  switch (risk) {
    case 'High': return 'error';
    case 'Medium': return 'warning';
    case 'Low': return 'success';
    default: return 'default';
  }
};

const ResultsDisplay = ({ result }) => {
  if (!result) return null;
  // Example: result.risk, result.protocols, result.anomalies, result.suspicious
  return (
    <Paper elevation={2} sx={{ bgcolor: 'background.paper', borderRadius: 2, p: 3, mt: 3 }}>
      <Typography variant="h6" fontWeight={600} mb={2}>
        Classification Result
      </Typography>
      <Stack direction="row" spacing={2} alignItems="center" mb={2}>
        <Typography variant="body1"><strong>Label:</strong> {String(result.label ?? '')}</Typography>
        {result.risk && (
          <Chip label={String(result.risk) + ' Risk'} color={getRiskColor(result.risk)} size="small" sx={{ fontWeight: 600 }} />
        )}
      </Stack>
      <Typography variant="body1" mb={1}><strong>Confidence:</strong> {(result.confidence * 100).toFixed(2)}%</Typography>
      {result.protocols && result.protocols.length > 0 && (
        <Box mb={1}>
          <Divider sx={{ my: 1 }} />
          <Typography variant="subtitle2" fontWeight={600} color="text.secondary">Protocols:</Typography>
          <Stack direction="row" spacing={1} mt={1}>
            {result.protocols.map((proto, idx) => (
              <Chip key={idx} label={String(proto)} color="info" size="small" />
            ))}
          </Stack>
        </Box>
      )}
      {result.anomalies && result.anomalies.length > 0 && (
        <Box mb={1}>
          <Divider sx={{ my: 1 }} />
          <Typography variant="subtitle2" fontWeight={600} color="text.secondary">Anomalies:</Typography>
          <Stack direction="row" spacing={1} mt={1}>
            {result.anomalies.map((anom, idx) => (
              <Chip key={idx} label={String(anom)} color="warning" size="small" />
            ))}
          </Stack>
        </Box>
      )}
      {result.suspicious && result.suspicious.length > 0 && (
        <Box mb={1}>
          <Divider sx={{ my: 1 }} />
          <Typography variant="subtitle2" fontWeight={600} color="error">Suspicious Patterns:</Typography>
          <Stack direction="row" spacing={1} mt={1}>
            {result.suspicious.map((item, idx) => (
              <Chip key={idx} label={String(item)} color="error" size="small" variant="outlined" />
            ))}
          </Stack>
        </Box>
      )}
      {/* Optional: Graph visualization can be added here */}
      {result.graph && <Box mt={2}>{/* Graph visualization placeholder */}</Box>}
    </Paper>
  );
};

ResultsDisplay.propTypes = {
  result: PropTypes.shape({
    label: PropTypes.string,
    confidence: PropTypes.number,
    graph: PropTypes.object,
  }),
};

export default ResultsDisplay;
