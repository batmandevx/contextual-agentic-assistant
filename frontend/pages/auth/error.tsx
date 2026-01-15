/**
 * OAuth error page
 */
import { useRouter } from 'next/router';
import Link from 'next/link';

export default function AuthError() {
  const router = useRouter();
  const { message } = router.query;

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center space-y-4 p-8">
        <div className="text-red-600 text-6xl">⚠️</div>
        <h1 className="text-3xl font-bold text-gray-900">Authentication Failed</h1>
        <p className="text-gray-600">
          {message || 'An error occurred during authentication. Please try again.'}
        </p>
        <Link
          href="/"
          className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          Return to Home
        </Link>
      </div>
    </div>
  );
}
