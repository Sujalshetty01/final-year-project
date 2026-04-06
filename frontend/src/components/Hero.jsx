import React from 'react';
import { motion } from 'framer-motion';
export default function Hero({ onCTAClick }) {
  return (
    <section className="py-16 bg-gradient-to-br from-blue-600 to-purple-700 text-white">
      {' '}
      <div className="max-w-4xl mx-auto px-4 text-center">
        {' '}
        <motion.h1
          className="text-4xl md:text-5xl font-extrabold mb-4"
          initial={{ opacity: 0, y: -40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          {' '}
          Malware Classification System{' '}
        </motion.h1>{' '}
        <motion.p
          className="text-lg md:text-xl mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9 }}
        >
          {' '}
          Deep Learning-powered malware detection using Graph Neural Networks.{' '}
        </motion.p>{' '}
        <motion.button
          className="bg-accent hover:bg-primary text-white font-semibold py-3 px-8 rounded-full shadow-lg transition-colors duration-300"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.97 }}
          onClick={onCTAClick}
        >
          {' '}
          Try the Demo{' '}
        </motion.button>{' '}
      </div>{' '}
    </section>
  );
}
