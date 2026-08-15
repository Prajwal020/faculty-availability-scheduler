import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { ArrowLeft, FileQuestion } from 'lucide-react';

export const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-50 text-center">
      <div className="w-16 h-16 bg-slate-200 text-slate-600 rounded-full flex items-center justify-center mb-4">
        <FileQuestion className="w-8 h-8" />
      </div>
      <h1 className="text-3xl font-bold text-slate-900 mb-2">404 — Page Not Found</h1>
      <p className="text-slate-600 max-w-md mb-6 text-sm">
        The requested page does not exist or has been moved.
      </p>
      <Link to="/">
        <Button leftIcon={<ArrowLeft className="w-4 h-4" />}>Return Home</Button>
      </Link>
    </div>
  );
};
