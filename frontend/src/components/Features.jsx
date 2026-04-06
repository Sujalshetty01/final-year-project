import React from 'react';
import { FaChartBar, FaShieldAlt, FaCloudUploadAlt } from 'react-icons/fa';
import Card from './Card';
import { useNavigate, Link } from 'react-router-dom';
export default function Features() {
  const navigate = useNavigate();
  const cardClass =
    'feature-card bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 flex flex-col items-center gap-2 hover:shadow-2xl transition-shadow duration-300 cursor-pointer hover:bg-blue-50 dark:hover:bg-gray-700';
  return (
    <section className="py-12 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
      {' '}
      <div className="max-w-6xl mx-auto px-4">
        {' '}
        <h2 className="text-3xl font-bold text-center mb-8 text-primary dark:text-accent">
          Features
        </h2>{' '}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {' '}
          <Link
            to="/dashboard"
            className={cardClass}
            style={{ textDecoration: 'none', position: 'relative', zIndex: 10 }}
            onClick={() => {
              console.log('Navigating to Dashboard');
            }}
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter') navigate('/dashboard');
            }}
          >
            {' '}
            <Card icon={<FaShieldAlt />} title="Secure Analysis">
              {' '}
              Advanced GNN-based malware detection with robust security.{' '}
            </Card>{' '}
          </Link>{' '}
          <Link
            to="/upload"
            className={cardClass}
            style={{ textDecoration: 'none', position: 'relative', zIndex: 10 }}
            onClick={() => {
              console.log('Navigating to Upload');
            }}
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter') navigate('/upload');
            }}
          >
            {' '}
            <Card icon={<FaCloudUploadAlt />} title="Easy Uploads">
              {' '}
              Drag & drop or browse to upload files for instant analysis.{' '}
            </Card>{' '}
          </Link>{' '}
          <Link
            to="/results"
            className={cardClass}
            style={{ textDecoration: 'none', position: 'relative', zIndex: 10 }}
            onClick={() => {
              console.log('Navigating to Results');
            }}
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter') navigate('/results');
            }}
          >
            {' '}
            <Card icon={<FaChartBar />} title="Insightful Results">
              {' '}
              Visualize predictions and performance with interactive charts.{' '}
            </Card>{' '}
          </Link>{' '}
        </div>{' '}
      </div>{' '}
    </section>
  );
}
