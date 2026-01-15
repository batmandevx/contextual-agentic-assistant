import { motion } from 'framer-motion';
import { FcGoogle } from 'react-icons/fc';
import { useAuth } from './AuthProvider';

export default function LoginButton() {
  const { login } = useAuth();

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={login}
      className="flex items-center gap-3 px-8 py-4 bg-white/10 hover:bg-white/20 
                 text-white font-medium rounded-xl border border-white/10 
                 backdrop-blur-md shadow-lg hover:shadow-primary-500/20 
                 transition-all duration-300 group"
    >
      <div className="bg-white p-1.5 rounded-full group-hover:shadow-md transition-shadow">
        <FcGoogle className="text-xl" />
      </div>
      <span className="text-lg tracking-wide">Sign in with Google</span>
    </motion.button>
  );
}
