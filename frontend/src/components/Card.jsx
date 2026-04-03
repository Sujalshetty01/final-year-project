import React from "react";
import { motion } from "framer-motion";

export default function Card({ icon, title, children }) {
  return (
    <motion.div
      className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 flex flex-col items-center gap-2 hover:shadow-2xl transition-shadow duration-300"
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-4xl text-primary mb-2">{icon}</div>
      <h3 className="font-semibold text-lg mb-1">{title}</h3>
      <div className="text-gray-600 dark:text-gray-300 text-center">{children}</div>
    </motion.div>
  );
}
