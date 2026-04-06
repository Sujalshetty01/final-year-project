import React, { useRef } from 'react';
import { Box, Button, Typography, LinearProgress, IconButton } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
const FileUpload = ({ onFileSelect, loading, progress = 0, file, status }) => {
  const fileInput = useRef();
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };
  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };
  return (
    <Box
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
      sx={{
        border: '2px dashed',
        borderColor: 'primary.light',
        borderRadius: 2,
        p: 4,
        textAlign: 'center',
        bgcolor: 'background.paper',
        color: 'primary.main',
        mb: 3,
      }}
    >
      {' '}
      <input
        type="file"
        accept=".pcap,.csv,.json"
        style={{ display: 'none' }}
        ref={fileInput}
        onChange={handleFileChange}
        disabled={loading}
      />{' '}
      <Typography variant="body1" mb={2}>
        {' '}
        Drag & drop a PCAP, CSV, or JSON file here, or{' '}
      </Typography>{' '}
      <Button
        variant="contained"
        color="primary"
        onClick={() => fileInput.current && fileInput.current.click()}
        disabled={loading}
        sx={{
          fontWeight: 600,
          transition: 'transform 0.15s',
          '&:hover': { transform: 'scale(1.07)' },
        }}
      >
        {' '}
        Browse{' '}
      </Button>{' '}
      {file && (
        <Box mt={3} display="flex" alignItems="center" justifyContent="center">
          {' '}
          <InsertDriveFileIcon
            color="primary"
            sx={{
              mr: 1,
              transition: 'transform 0.3s',
              transform:
                status === 'success'
                  ? 'scale(1.2) rotate(-10deg)'
                  : status === 'error'
                    ? 'scale(1.2) rotate(10deg)'
                    : 'scale(1)',
            }}
          />{' '}
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            {' '}
            {file.name}{' '}
          </Typography>{' '}
          {status === 'success' && (
            <CheckCircleIcon
              color="success"
              sx={{
                ml: 1,
                transition: 'transform 0.3s',
                transform: 'scale(1.3)',
                animation: 'pop 0.4s',
              }}
            />
          )}{' '}
          {status === 'error' && (
            <ErrorIcon
              color="error"
              sx={{
                ml: 1,
                transition: 'transform 0.3s',
                transform: 'scale(1.3)',
                animation: 'shake 0.4s',
              }}
            />
          )}{' '}
        </Box>
      )}{' '}
      {loading && (
        <Box mt={2}>
          {' '}
          <LinearProgress
            variant={progress > 0 ? 'determinate' : 'indeterminate'}
            value={progress}
          />{' '}
        </Box>
      )}{' '}
    </Box>
  );
};
export default FileUpload;
