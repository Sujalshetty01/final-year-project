
import axios from "axios";
import { API_BASE_URL } from "../config";
const cleanBase = API_BASE_URL;

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


      function handleApiError(error) {
        let message = error?.response?.data?.error || error?.response?.data?.detail || error.message || 'Unknown error';
        throw new Error(message);
      }
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


// Removed unused fetchData, uploadFileRaw, fetchHistory, fetchStatus endpoints



export const fetchResult = async (id) => {
  const response = await axios.get(`${cleanBase}/result/${id}`);
  return response.data;
};


// fetchHistory and fetchStatus removed: not implemented in backend
