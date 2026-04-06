
import React from "react";
import { Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Results from "./pages/Results";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import Features from "./components/Features";
import DemoResults from "./components/DemoResults";
import TestIcon from "./components/TestIcon";
import Footer from "./components/Footer";
import { ThemeProvider } from "./context/ThemeContext";
import "./App.css";
import "./theme.css";


function LandingPage() {
  // Demo scroll handler
  const scrollToDemo = () => {
    document.getElementById("demo-section")?.scrollIntoView({ behavior: "smooth" });
  };
  return (
    <div>
      <Navbar />
      <Features />
      <button onClick={scrollToDemo} style={{margin: 24, padding: 12, fontSize: 18}}>Try the Demo</button>
      <div id="demo-section">
        <DemoResults />
      </div>
      <TestIcon />
      <Footer />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<><Sidebar /><Dashboard /></>} />
        <Route path="/upload" element={<><Sidebar /><Upload /></>} />
        <Route path="/results/:id" element={<><Sidebar /><Results /></>} />
      </Routes>
    </ThemeProvider>
  );
}
