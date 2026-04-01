'use client';

import React from 'react';

export default function LoginLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-gradient-to-br from-indigo-50 to-blue-100 min-h-screen flex items-center justify-center">
      {children}
    </div>
  );
}
