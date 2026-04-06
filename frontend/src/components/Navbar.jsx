import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { ThemeContext } from '../context/ThemeContext';
export default function Navbar() {
  const { toggleTheme } = useContext(ThemeContext);
  return (
    <nav className="flex items-center justify-between px-6 py-4 bg-white dark:bg-gray-900 shadow-md">
      {' '}
      <div className="flex items-center gap-2">
        {' '}
        <Link to="/">
          {' '}
          <img src="/favicon.ico" alt="Logo" className="h-8 w-8" />{' '}
        </Link>{' '}
        <span className="font-bold text-xl text-primary">Malware Classifier</span>{' '}
      </div>{' '}
      <div className="flex items-center gap-4">
        {' '}
        <Link
          to="/#features"
          className="text-gray-700 dark:text-gray-200 hover:text-primary transition"
        >
          Features
        </Link>{' '}
        <Link
          to="/#demo"
          className="text-gray-700 dark:text-gray-200 hover:text-primary transition"
        >
          Demo
        </Link>{' '}
        <button
          onClick={toggleTheme}
          className="ml-4 bg-gray-200 dark:bg-gray-700 rounded-full p-2 hover:bg-primary hover:text-white dark:hover:bg-accent transition"
          aria-label="Toggle dark mode"
        >
          {' '}
          <span role="img" aria-label="theme">
            🌓
          </span>{' '}
        </button>{' '}
      </div>{' '}
    </nav>
  );
}
