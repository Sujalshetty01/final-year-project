import React from 'react';
import { Card, CardContent, Typography, Box, Link, List, ListItem, ListItemText } from '@mui/material';

const About = () => (
  <Box display="flex" justifyContent="center" alignItems="flex-start" minHeight="60vh" p={2}>
    <Card sx={{ minWidth: 400, maxWidth: 600, width: '100%', boxShadow: 3 }}>
      <CardContent>
        <Typography variant="h5" fontWeight={700} mb={2}>
          About
        </Typography>
        <Typography variant="body1" mb={2}>
          This project is a malware classification system using a Graph Neural Network (GNN) model.
        </Typography>
        <Typography variant="h6" fontWeight={600} mt={2} mb={1}>
          Tech Stack
        </Typography>
        <List dense>
          <ListItem><ListItemText primary="Frontend: React, Chart.js, React Router" /></ListItem>
          <ListItem><ListItemText primary="Backend: FastAPI, PyTorch, torch_geometric" /></ListItem>
          <ListItem><ListItemText primary="ML: GNN, Cora Dataset, Scikit-learn" /></ListItem>
          <ListItem><ListItemText primary="Tools: Wireshark, Docker" /></ListItem>
        </List>
        <Typography variant="h6" fontWeight={600} mt={2} mb={1}>
          Links
        </Typography>
        <List dense>
          <ListItem>
            <Link href="https://github.com/your-repo" target="_blank" rel="noopener noreferrer">GitHub Repository</Link>
          </ListItem>
          <ListItem>
            <Link href="https://pytorch-geometric.readthedocs.io/" target="_blank" rel="noopener noreferrer">PyTorch Geometric Docs</Link>
          </ListItem>
        </List>
      </CardContent>
    </Card>
  </Box>
);

export default About;
