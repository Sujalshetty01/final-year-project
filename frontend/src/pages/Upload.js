
import React, { useState } from 'react';
import FileUpload from '../components/FileUpload';
import Loader from '../components/common/Loader';
import Notification from '../components/common/Notification';
import { uploadFile } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, Typography, Box } from '@mui/material';
import ErrorBoundary from '../components/ErrorBoundary';

const Upload = () => {
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState({ message: "", type: "" });
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null); // 'success' | 'error' | null
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();

  const handleFileSelect = async (file) => {
    if (!file) return;
    setSelectedFile(file);
    setUploadStatus(null);
    setProgress(0);
    if (!/\.(pcap|csv|json)$/i.test(file.name)) {
      setNotification({ message: "Invalid file type. Please upload PCAP, CSV, or JSON.", type: "error" });
      setUploadStatus('error');
      return;
    }
    setLoading(true);
    setNotification({ message: "", type: "" });
    try {
      // Simulate progress for demo; replace with real upload progress if available
      let fakeProgress = 0;
      const progressInterval = setInterval(() => {
        fakeProgress += 10;
        setProgress(Math.min(fakeProgress, 95));
      }, 100);
      console.log('[Upload.js] Calling uploadFile with:', file);
      const data = await uploadFile(file);
      console.log('[Upload.js] uploadFile returned:', data);
      clearInterval(progressInterval);
      setProgress(100);
      setUploadStatus('success');
      setNotification({ message: "File uploaded and analysis started!", type: "success" });
      if (data && data.id) {
        setTimeout(() => navigate(`/results/${data.id}`), 1000);
      }
    } catch (e) {
      setUploadStatus('error');
      setNotification({ message: "Upload failed: " + (e.response?.data?.message || e.message), type: "error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <ErrorBoundary>
      <Box display="flex" justifyContent="center" alignItems="flex-start" minHeight="60vh" p={2}>
        <Card sx={{ minWidth: 400, maxWidth: 500, width: '100%', boxShadow: 3 }}>
          <CardContent>
            <Typography variant="h5" fontWeight={700} mb={2}>
              Upload File
            </Typography>
            <FileUpload
              onFileSelect={handleFileSelect}
              loading={loading}
              progress={progress}
              file={selectedFile}
              status={uploadStatus}
            />
          </CardContent>
        </Card>
        <Notification message={notification.message} type={notification.type} onClose={() => setNotification({ message: '', type: '' })} />
      </Box>
    </ErrorBoundary>
  );
};

export default Upload;
