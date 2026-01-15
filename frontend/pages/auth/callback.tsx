/**
 * OAuth callback page
 */
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/components/AuthProvider';

export default function AuthCallback() {
  const router = useRouter();
  const { setToken } = useAuth();

  useEffect(() => {
    const { token } = router.query;
    
    if (token && typeof token === 'string') {
      setToken(token);
      router.push('/');
    }
  }, [router.query, setToken, router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Completing authentication...</p>
      </div>
    </div>
  );
}
