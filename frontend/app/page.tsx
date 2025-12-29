'use client';

/**
 * Home Page - Redirects to auth or tasks
 */

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('auth_token');

    if (token) {
      // Redirect to tasks if authenticated
      router.push('/tasks');
    } else {
      // Redirect to signin if not authenticated
      router.push('/auth/signin');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center">
      <div className="text-white text-lg">Redirecting...</div>
    </div>
  );
}
