/**
 * Main chat interface page
 */
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/components/AuthProvider';
import ChatInterface from '@/components/ChatInterface';
import LoginButton from '@/components/LoginButton';

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center space-y-6 p-8">
          <h1 className="text-5xl font-bold text-gray-900">
            Contextual Agentic AI Assistant
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl">
            Your personal Chief of Staff powered by AI. Manage your Gmail, Calendar, and more with intelligent assistance.
          </p>
          <div className="pt-4">
            <LoginButton />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <ChatInterface />
    </div>
  );
}
