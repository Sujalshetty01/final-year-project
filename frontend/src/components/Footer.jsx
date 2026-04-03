import React from "react";
import { FaGithub } from "react-icons/fa";

export default function Footer() {
  return (
    <footer className="py-6 bg-gray-100 dark:bg-gray-900 text-center text-gray-500 dark:text-gray-400 mt-12">
      <div className="flex justify-center items-center gap-2">
        <span>© {new Date().getFullYear()} Malware Classification Project</span>
        <a
          href="https://github.com/your-repo"
          target="_blank"
          rel="noopener noreferrer"
          className="ml-2 text-primary hover:text-accent"
        >
          <FaGithub size={20} />
        </a>
      </div>
    </footer>
  );
}
