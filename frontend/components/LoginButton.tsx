/**
 * Login button component
 */
import { useAuth } from './AuthProvider';

export default function LoginButton() {
  const { login } = useAuth();

  return (
    <button
      onClick={login}
      className="px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
    >
      Sign in with Google
    </button>
  );
}
