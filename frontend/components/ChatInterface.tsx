import { useState, useEffect, useRef } from 'react';
import { useAuth } from './AuthProvider';
import MessageList from './MessageList';
import InputBox from './InputBox';
import { motion, AnimatePresence } from 'framer-motion';
import { BiMenu, BiPlus, BiLogOut, BiMessageSquareDetail, BiUser } from 'react-icons/bi';
import { chatAPI } from '../lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatInterface() {
  const { user, logout } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [conversationId, setConversationId] = useState<string | null>(null);

  // Initialize with a welcome message
  useEffect(() => {
    setMessages([
      { role: 'assistant', content: `Hello ${user?.name || 'there'}! I'm your advanced contextual assistant. How can I help you today?` }
    ]);
  }, [user]);

  const sendMessage = async (content: string) => {
    if (!content.trim()) return;

    const newMessages = [...messages, { role: 'user', content } as Message];
    setMessages(newMessages);
    setLoading(true);

    try {
      const data = await chatAPI.sendMessage(content, conversationId || undefined);

      const assistantMessage = data.response;

      setMessages([...newMessages, { role: 'assistant', content: assistantMessage }]);

      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      setMessages([...newMessages, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-dark-bg text-slate-100 font-sans">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="h-full bg-dark-card/50 backdrop-blur-xl border-r border-white/5 flex flex-col z-20"
          >
            <div className="p-4 border-b border-white/5 flex items-center justify-between">
              <span className="font-semibold text-white/80 flex items-center gap-2">
                <BiMessageSquareDetail className="text-primary-500" /> History
              </span>
              <button onClick={() => setConversationId(null)} className="p-2 hover:bg-white/5 rounded-lg text-primary-400">
                <BiPlus />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              <div className="text-xs text-slate-500 uppercase font-medium mb-3">Recent Chats</div>
              {/* Placeholder for history items */}
              <button className="w-full text-left p-3 rounded-lg bg-primary-500/10 text-primary-200 text-sm border border-primary-500/20 truncate">
                New Conversation
              </button>
            </div>

            <div className="p-4 border-t border-white/5">
              <div className="flex items-center gap-3 p-2 rounded-lg bg-white/5 mb-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-xs font-bold">
                  {user?.name?.[0] || 'U'}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{user?.name}</div>
                  <div className="text-xs text-slate-400 truncate">{user?.email}</div>
                </div>
              </div>
              <button
                onClick={logout}
                className="w-full flex items-center gap-2 p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg text-sm transition-colors"
              >
                <BiLogOut /> Sign Out
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative z-10 w-full">
        {/* Header */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-white/5 bg-dark-bg/80 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white transition-colors"
            >
              <BiMenu className="text-xl" />
            </button>
            <h1 className="text-lg font-medium text-white/90">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-secondary-400">Contextual AI</span> Assistant
            </h1>
          </div>
          <div className="flex items-center gap-2">
            {/* Header actions can go here */}
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-hidden relative">
          <div className="absolute inset-0 z-0">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-600/10 rounded-full blur-[100px] animate-pulse-slow"></div>
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary-600/10 rounded-full blur-[100px] animate-pulse-slow animate-delay-300"></div>
          </div>
          <MessageList messages={messages} loading={loading} />
        </div>

        {/* Input */}
        <div className="p-4 md:p-6 bg-dark-bg/50 backdrop-blur-sm">
          <div className="max-w-4xl mx-auto">
            <InputBox onSendMessage={sendMessage} loading={loading} />
          </div>
        </div>
      </main>
    </div>
  );
}
