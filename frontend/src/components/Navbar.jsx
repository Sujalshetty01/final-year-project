import React from "react";

export default function Navbar({ onToggleDark }) {
  return (
    <nav className="flex items-center justify-between px-6 py-4 bg-white dark:bg-gray-900 shadow-md">
      <div className="flex items-center gap-2">
        <img src="/favicon.ico" alt="Logo" className="h-8 w-8" />
        <span className="font-bold text-xl text-primary">Malware Classifier</span>
      </div>
      <div className="flex items-center gap-4">
        <a href="#features" className="text-gray-700 dark:text-gray-200 hover:text-primary transition">Features</a>
        <a href="#demo" className="text-gray-700 dark:text-gray-200 hover:text-primary transition">Demo</a>
        <button
          onClick={onToggleDark}
          className="ml-4 bg-gray-200 dark:bg-gray-700 rounded-full p-2 hover:bg-primary hover:text-white dark:hover:bg-accent transition"
          aria-label="Toggle dark mode"
        >
          <span role="img" aria-label="theme">🌓</span>
        </button>
      </div>
    </nav>
  );
}
