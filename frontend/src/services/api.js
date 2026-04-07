import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";

// Remove trailing slash if present
const cleanBase = API_BASE.replace(/\/$/, "");

export const uploadFile = async (file) => {
  console.log('[uploadFile] Called with file:', file);
  // Helper to parse CSV to JSON
  function csvToJson(csv) {
    const lines = csv.split('\n').filter(Boolean);
    const headers = lines[0].split(',').map(h => h.trim());
    return lines.slice(1).map(line => {
      const values = line.split(',');
      const obj = {};
      headers.forEach((header, i) => {
        obj[header] = values[i] ? values[i].trim() : '';
      });
      return obj;
    });
  }

  // Read file as text
  const text = await file.text();
  let parsedData;
  if (file.name.endsWith('.json')) {
    parsedData = JSON.parse(text);
  } else if (file.name.endsWith('.csv')) {
    parsedData = csvToJson(text);
  } else {
    throw new Error('Unsupported file type. Only CSV and JSON are supported.');
  }
  console.log('[uploadFile] Parsed data:', parsedData);


  // Send to backend as JSON
  const endpoint = `${cleanBase}/analyze`;
  console.log('[uploadFile] Posting to:', endpoint);
  try {
    const response = await axios.post(
      endpoint,
      { network_flows: parsedData },
      { headers: { 'Content-Type': 'application/json' } }
    );
    return response.data;
  } catch (error) {
    console.error('[uploadFile] API error:', error);
    alert('Upload failed: ' + (error?.response?.data?.detail || error.message));
    throw error;
  }
};

export const fetchData = async () => {
  try {
    const res = await axios.get(`${API_BASE}/some-endpoint`);
    return res.data;
  } catch (err) {
    console.error("API error:", err);
    throw err;
  }
};

// If you need a raw file upload endpoint, use this:
export const uploadFileRaw = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  try {
    const res = await axios.post(`${API_BASE}/upload`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  } catch (err) {
    console.error("Upload error:", err);
    alert('Upload failed: ' + (err?.response?.data?.detail || err.message));
    throw err;
  }
};
export const fetchResult = async (id) => {
  const response = await axios.get(`${API_BASE}/results/${id}`);
  return response.data;
};

export const fetchHistory = async () => {
  const response = await axios.get(`${API_BASE}/history`);
  return response.data;
};

export const fetchStatus = async () => {
  const response = await axios.get(`${API_BASE}/status`);
  return response.data;
};
