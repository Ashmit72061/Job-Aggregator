"use client";

import { useState } from "react";

export default function FloatBt() {
  const [showSteps, setShowSteps] = useState(false);

  return (
    <div className="fixed bottom-6 right-6 z-50 mb-20">
      {/* Floating Button */}
    

      {/* Steps Box */}
      {showSteps && (
        <div className="mt-4 w-80 bg-gray-900 bg-opacity-90 text-white p-6 rounded-2xl shadow-xl border border-orange-400 backdrop-blur-md transition-all duration-300">
          <h3 className="text-xl font-bold mb-3 text-orange-400">How It Works</h3>
          <ol className="list-decimal list-inside space-y-2 text-sm text-gray-200">
            <li>
              <span className="font-medium">Upload your resume</span><br />
              (Make sure it includes <span className="text-orange-300">skills</span> & <span className="text-orange-300">location</span>)
            </li>
            <li>
              <span className="font-medium">FindMyJob searches top platforms</span><br />
              Like <span className="text-orange-300">Naukri.com</span>, <span className="text-orange-300">LinkedIn</span>, and more
            </li>
            <li>
              <span className="font-medium">You get instant job links</span><br />
              Click to explore & apply directly!
            </li>
          </ol>
        </div>
      )}

        <button
        onClick={() => setShowSteps(!showSteps)}
        className="bg-orange-500 hover:bg-orange-600 text-white p-4 rounded-full shadow-lg transition duration-300 absolute right-0 cursor-pointer"
        aria-label="How it works"
      >
        ?
      </button>
    </div>
  );
}
