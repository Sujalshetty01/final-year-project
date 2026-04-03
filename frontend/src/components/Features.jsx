import React from "react";
import { FaChartBar, FaShieldAlt, FaCloudUploadAlt } from "react-icons/fa";
import Card from "./Card";

export default function Features() {
  return (
    <section className="py-12 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-6xl mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-8 text-primary dark:text-accent">Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card icon={<FaShieldAlt />} title="Secure Analysis">
            Advanced GNN-based malware detection with robust security.
          </Card>
          <Card icon={<FaCloudUploadAlt />} title="Easy Uploads">
            Drag & drop or browse to upload files for instant analysis.
          </Card>
          <Card icon={<FaChartBar />} title="Insightful Results">
            Visualize predictions and performance with interactive charts.
          </Card>
        </div>
      </div>
    </section>
  );
}
