import Head from 'next/head';
import { useEffect, useState } from 'react';
import { useAuth } from '../components/AuthProvider';
import ChatInterface from '../components/ChatInterface';
import LoginButton from '../components/LoginButton';
import { motion } from 'framer-motion';
import { BsStars, BsShieldLock, BsLightningCharge, BsCpu } from 'react-icons/bs';
import { healthCheck } from '../lib/api';

export default function Home() {
  const { user, loading } = useAuth();
  const [backendHealth, setBackendHealth] = useState<boolean>(false);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await healthCheck();
        setBackendHealth(true);
      } catch (error) {
        console.error('Backend offline', error);
      }
    };
    checkHealth();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-bg">
        <div className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (user) {
    return <ChatInterface />;
  }

  const features = [
    { icon: BsStars, title: 'Contextual AI', desc: 'Remembers conversation history & details' },
    { icon: BsLightningCharge, title: 'Real-time', desc: 'Instant responses with low latency' },
    { icon: BsShieldLock, title: 'Secure', desc: 'Enterprise-grade encryption' },
    { icon: BsCpu, title: 'Agentic', desc: 'Autonomous task execution capabilities' },
  ];

  return (
    <div className="min-h-screen relative overflow-hidden flex flex-col items-center justify-center px-4">
      <Head>
        <title>Contextual AI Assistant</title>
      </Head>

      {/* Background Orbs */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-600/30 rounded-full blur-[120px] animate-float" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary-600/30 rounded-full blur-[120px] animate-float animate-delay-200" />
      </div>

      <motion.main
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="w-full max-w-5xl flex flex-col items-center text-center z-10"
      >
        <div className="mb-8 inline-flex items-center gap-2 px-4 py-2 rounded-full glass border-primary-500/30 text-primary-200 text-sm font-medium">
          <span className="relative flex h-3 w-3">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${backendHealth ? 'bg-green-400' : 'bg-red-400'}`}></span>
            <span className={`relative inline-flex rounded-full h-3 w-3 ${backendHealth ? 'bg-green-500' : 'bg-red-500'}`}></span>
          </span>
          {backendHealth ? 'Systems Operational' : 'Connecting to Backend...'}
        </div>

        <h1 className="text-5xl md:text-7xl font-bold mb-6 tracking-tight">
          Experience the <br />
          <span className="text-gradient">Future of AI Chat</span>
        </h1>

        <p className="text-xl md:text-2xl text-slate-300 max-w-2xl mb-12 text-balance leading-relaxed">
          A truly contextual, agentic assistant that remembers you and helps you achieve more.
        </p>

        <div className="mb-20">
          <LoginButton />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full">
          {features.map((feature, i) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + (i * 0.1) }}
                className="glass p-6 rounded-2xl flex flex-col items-center hover:bg-white/5 transition-colors"
              >
                <Icon className="text-4xl text-secondary-400 mb-4" />
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-slate-400 text-sm">{feature.desc}</p>
              </motion.div>
            );
          })}
        </div>
      </motion.main>
    </div>
  );
}
