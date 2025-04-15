// app/page.js
"use client"

import { useRef, useState, useEffect } from 'react';
import FloatBt from "@/components/FloatBt";


export default function Home() {
  const secondSlideRef = useRef(null);

  const scrollToNextSlide = () => {
    secondSlideRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const headings = [
    "Find Your Job In One Click",
    "Get Matched Instantly"
  ];
  const animationDuration = 4000; // Match the CSS animation duration
  const [textIndex, setTextIndex] = useState(0);
  const [key, setKey] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setTextIndex((prevIndex) => {
        const nextIndex = (prevIndex + 1) % headings.length;
        setKey((prevKey) => prevKey + 1);
        return nextIndex;
      });
    }, animationDuration);
    return () => clearInterval(interval);
  }, [headings.length, animationDuration]);

  return (<>
  <FloatBt/>

    <video className="absolute top-0 left-0 w-full h-full object-cover" src="/vid1.mp4" 
   autoPlay={true}
   loop={true}
   muted={true} />
    <div className="bg-black text-orange-400 min-h-screen font-sans">
      {/* Hero Section */}
      <section className="h-screen relative overflow-hidden flex items-center justify-center px-4">
  <div className="relative z-10 flex flex-col items-center justify-center text-center w-full max-w-4xl mx-auto">
    <h1
      key={key}
      className="text-3xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold text-orange-400 mb-10 animate-typing overflow-hidden whitespace-nowrap border-r-4 border-orange-400"
    >
      {headings[textIndex]}
    </h1>
    <button
      onClick={scrollToNextSlide}
      className="animate-bounce text-orange-400 hover:text-white text-4xl md:text-5xl lg:text-6xl cursor-pointer"
    >
      ↓
    </button>
  </div>
</section>


      {/* Upload Section */}
      <section
  ref={secondSlideRef}
  id="upload-section"
  className="h-screen w-full flex flex-col md:flex-row pt-50 justify-center gap-12 px-6  bg-black bg-opacity-80 text-orange-400"
>
  {/* Left side – Upload card */}
  <div className="backdrop-blur-md bg-black/40 border border-orange-500 rounded-2xl p-10 w-full max-w-xl h-[400px] shadow-lg flex flex-col justify-between">
    <div>
      <h2 className="text-3xl font-bold mb-4 text-white text-center">Upload Your Resume</h2>
      <p className="text-sm text-gray-300 mb-6 text-center">We’ll scan your resume and match you with the best job roles</p>
      <input
        type="file"
        accept="application/pdf"
        className="w-full p-3 bg-black bg-opacity-40 text-white border border-orange-400 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
      />
    </div>
    <button className="mt-6 w-full bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg transition duration-300">
      Find Jobs
    </button>
  </div>

  {/* Right side – Illustration or Image */}
  <div className="hidden md:block w-80 max-w-md">
    <img
      src="/MGlass2.png"
      alt="Job search illustration"
      className="rounded-2xl shadow-lg opacity-90 hover:opacity-100 transition duration-300"
    />
  </div>
</section>
    </div>
    </>);
}
