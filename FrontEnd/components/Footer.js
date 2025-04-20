export default function Footer() {
    return (
      <footer className="bg-black bg-opacity-40 backdrop-blur-md text-orange-400 text-center py-6 mt-20 border-t border-orange-500">
        <p>&copy; {new Date().getFullYear()} FindMyJob. All rights reserved.</p>
      </footer>
    );
  }
  