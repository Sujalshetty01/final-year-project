import React from "react";
import { Box } from "@mui/material";
import Sidebar from "./components/Sidebar";
import TopNavbar from "./components/TopNavbar";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Results from "./pages/Results";
import History from "./pages/History";
import About from "./pages/About";
import { ThemeProvider } from "./context/ThemeContext";
import { Routes, Route } from "react-router-dom";
import ErrorBoundary from "./components/ErrorBoundary";
import "./App.css";
import "./theme.css";

function App() {
  return (
    <ThemeProvider>
      <ErrorBoundary>
        <div className="app-container" style={{ display: 'flex', minHeight: '100vh' }}>
          <Sidebar />
          <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
            <TopNavbar />
            <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
              <noscript style={{ color: "red", background: "white", padding: 20, display: "block" }}>
                JavaScript is required to run this app.
              </noscript>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/upload" element={<Upload />} />
                <Route path="/results/:id" element={<Results />} />
                <Route path="/history" element={<History />} />
                <Route path="/about" element={<About />} />
              </Routes>
            </Box>
          </Box>
        </div>
      </ErrorBoundary>
    </ThemeProvider>
  );
}

export default App;
