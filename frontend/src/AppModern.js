import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Features from "./components/Features";
import DemoResults from "./components/DemoResults";
import Footer from "./components/Footer";
import Spinner from "./components/Spinner";
import "./index.css";

export default function App() {
  const [dark, setDark] = useState(() =>
    window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
  );
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  const handleCTAClick = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 1200); // Simulate loading
    document.getElementById("demo")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700 dark:from-gray-900 dark:to-gray-800">
      <Navbar onToggleDark={() => setDark((d) => !d)} />
      <Hero onCTAClick={handleCTAClick} />
      <Features />
      {loading ? <Spinner /> : <DemoResults />}
      <Footer />
    </div>
  );
}
