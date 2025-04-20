"use client";

export default function Navbar() {
  return (
    <nav className="fixed top-0 w-full z-50 bg-black/70 backdrop-blur-lg text-orange-400 shadow-md">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <h1 className="text-2xl font-extrabold tracking-wide">FindMyJob</h1>
        <div className="space-x-6 hidden md:flex">
          <a href="#" className="hover:text-white transition duration-200">Home</a>
          <a href="#upload-section" className="hover:text-white transition duration-200">Upload</a>
          <a href="#" className="hover:text-white transition duration-200">About</a>
        </div>
      </div>
    </nav>
  );
}
