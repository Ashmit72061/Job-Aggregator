"use client";
import { useState } from "react";

export default function Resume() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://127.0.0.1:8080/upload", {
      method: "POST",
      body: formData,
    });

    const json = await res.json();
    setData(json);
  };

  return (
    <div className="w-full flex flex-col items-center gap-10">
      <div className="backdrop-blur-md bg-black/40 border border-orange-500 rounded-2xl p-10 w-full max-w-xl shadow-lg flex flex-col justify-between">
        <div>
          <h2 className="text-3xl font-bold mb-4 text-white text-center">Upload Your Resume</h2>
          <p className="text-sm text-gray-300 mb-6 text-center">
            We’ll scan your resume and match you with the best job roles
          </p>
          <input
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="w-full p-3 bg-black bg-opacity-40 text-white border border-orange-400 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
        </div>
        <button
          onClick={handleUpload}
          className="mt-6 w-full bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg transition duration-300"
        >
          Find Jobs
        </button>
      </div>

      {data && (
        <div className="w-full max-w-4xl bg-black/50 backdrop-blur-md text-white border border-orange-400 rounded-2xl p-8 shadow-lg">
          <h3 className="text-2xl font-bold mb-4 text-orange-400">Resume Scan Results</h3>
          <p className="mb-2"><strong>Message:</strong> {data.message}</p>
          <p className="mb-4"><strong>Filename:</strong> {data.filename}</p>

          <div className="mb-4">
            <h4 className="text-xl font-semibold text-orange-300 mb-2">Skills Extracted:</h4>
            <ul className="list-disc list-inside space-y-1 text-gray-200">
              {data.skills.map((skill, i) => (
                <li key={i}>{skill}</li>
              ))}
            </ul>
          </div>

          <div className="mb-4">
            <h4 className="text-xl font-semibold text-orange-300 mb-2">Top Matching Job Titles:</h4>
            <ul className="list-disc list-inside space-y-1 text-gray-200">
              {data.matched_jobs.map((job, i) => (
                <li key={i}>{job}</li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-xl font-semibold text-orange-300 mb-4">Naukri Job Matches:</h4>
            {data.naukri_jobs.length === 0 ? (
              <p className="text-gray-400">No jobs found.</p>
            ) : (
              data.naukri_jobs.map((job, i) => (
                <div key={i} className="mb-6 p-4 bg-black/30 border border-orange-500 rounded-xl">
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-orange-300 text-lg font-semibold hover:underline"
                  >
                    {job.title}
                  </a>
                  <p><strong>Company:</strong> {job.company}</p>
                  <p><strong>Location:</strong> {job.location}</p>
                  <p><strong>Experience:</strong> {job.experience}</p>
                  <p><strong>Salary:</strong> {job.salary}</p>
                  <p className="text-sm text-gray-300 mt-1">{job.description}</p>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
