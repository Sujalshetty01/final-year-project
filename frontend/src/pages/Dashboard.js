import React from 'react';
import { Box, Grid, Typography } from '@mui/material';
import Loader from '../components/common/Loader';
import StatusCard from '../components/StatusCard';
import SummaryCard from '../components/common/SummaryCard';
import RecentActivityTable from '../components/RecentActivityTable';
import MalwareBarChart from '../components/charts/MalwareBarChart';
import MalwarePieChart from '../components/charts/MalwarePieChart';
import MalwareLineChart from '../components/charts/MalwareLineChart';
import { useApi } from '../hooks/useApi';
import { fetchStatus, fetchHistory } from '../services/api';
import BarChartIcon from '@mui/icons-material/BarChart';
import InsertChartIcon from '@mui/icons-material/InsertChart';
import TimelineIcon from '@mui/icons-material/Timeline';
import ErrorBoundary from '../components/ErrorBoundary';

const Dashboard = () => {
  const { data: status, loading: loadingStatus } = useApi(fetchStatus, []);
  const { data: recent, loading: loadingRecent } = useApi(fetchHistory, []);

  // Example summary stats (replace with real API data as needed)
  const summaryStats = [
    { title: 'Total Files', value: status?.total_files ?? 0, icon: <BarChartIcon color="primary" /> },
    { title: 'Malware Detected', value: status?.malware_count ?? 0, icon: <InsertChartIcon color="error" /> },
    { title: 'Benign Files', value: status?.benign_count ?? 0, icon: <TimelineIcon color="success" /> },
  ];

  return (
    <ErrorBoundary>
      <Box p={3}>
        <Typography variant="h4" fontWeight={700} mb={2}>Dashboard</Typography>
        {(loadingStatus || loadingRecent) && <Loader />}
        <Grid container spacing={2} mb={2}>
          <Grid item xs={12} md={4}>
            <StatusCard title="API Status" value={status?.api || 'Unknown'} status={status?.api === 'OK' ? 'success' : 'error'} />
          </Grid>
          <Grid item xs={12} md={4}>
            <StatusCard title="Model" value={status?.model || 'Unknown'} status={status?.model ? 'success' : 'warning'} />
          </Grid>
        </Grid>
        <Grid container spacing={2} mb={2}>
          {summaryStats.map((stat, idx) => (
            <Grid item xs={12} sm={4} md={2} key={stat.title}>
              <SummaryCard {...stat} />
            </Grid>
          ))}
        </Grid>
        <Grid container spacing={2} mb={2}>
          <Grid item xs={12} md={4}>
            <MalwareBarChart data={[
              { type: 'Malware', count: status?.malware_count ?? 0 },
              { type: 'Benign', count: status?.benign_count ?? 0 },
            ]} />
          </Grid>
          <Grid item xs={12} md={4}>
            <MalwarePieChart data={[
              { type: 'Malware', value: status?.malware_count ?? 0 },
              { type: 'Benign', value: status?.benign_count ?? 0 },
            ]} />
          </Grid>
          <Grid item xs={12} md={4}>
            <MalwareLineChart data={[
              { date: '2024-01', malware: 2, benign: 5 },
              { date: '2024-02', malware: 3, benign: 7 },
              { date: '2024-03', malware: 1, benign: 6 },
              { date: '2024-04', malware: 4, benign: 8 },
              { date: '2024-05', malware: 2, benign: 9 },
            ]} />
          </Grid>
        </Grid>
        <Box mt={4}>
          <Typography variant="h6" fontWeight={600} mb={1}>Recent Activity</Typography>
          <RecentActivityTable data={recent ? recent.slice(0, 5) : []} />
        </Box>
      </Box>
    </ErrorBoundary>
  );
};

export default Dashboard;
