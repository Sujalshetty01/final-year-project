import React from 'react';
import { motion } from 'framer-motion';

export default function Card({ icon, title, children, ...props }) {
  return (
    <motion.div
      {...props}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 flex flex-col items-center gap-2 hover:shadow-2xl transition-shadow duration-300 cursor-pointer hover:bg-blue-50 dark:hover:bg-gray-700"
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      tabIndex={0}
      role="button"
      onKeyPress={(e) => (e.key === 'Enter' || e.key === ' ') && props.onClick && props.onClick(e)}
    >
      <div className="text-4xl text-primary mb-2">{icon}</div>
      <h3 className="font-semibold text-lg mb-1">{title}</h3>
      <div className="text-gray-600 dark:text-gray-300 text-center">{children}</div>
    </motion.div>
  );
}
