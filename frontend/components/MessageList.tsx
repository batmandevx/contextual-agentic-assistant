import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { BsRobot, BsPerson, BsStars } from 'react-icons/bs';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface MessageListProps {
  messages: Message[];
  loading: boolean;
}

export default function MessageList({ messages, loading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  return (
    <div className="h-full overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth z-10 relative">
      {messages.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-slate-500 opacity-60">
          <BsStars className="text-6xl mb-4" />
          <p>Start a conversation...</p>
        </div>
      )}

      {messages.map((msg, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div className={`flex max-w-[85%] md:max-w-[70%] gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
            {/* Avatar */}
            <div className={`w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg
              ${msg.role === 'user'
                ? 'bg-gradient-to-br from-primary-500 to-secondary-500'
                : 'bg-dark-card border border-white/10'}`}>
              {msg.role === 'user' ? <BsPerson className="text-white text-sm md:text-base" /> : <BsRobot className="text-primary-400 text-sm md:text-base" />}
            </div>

            {/* Bubble */}
            <div className={`p-4 rounded-2xl shadow-md text-sm md:text-base leading-relaxed
              ${msg.role === 'user'
                ? 'bg-gradient-to-br from-primary-600 to-primary-700 text-white rounded-tr-sm'
                : 'bg-white/10 backdrop-blur-md border border-white/10 text-slate-100 rounded-tl-sm'
              }`}>
              {msg.content}
            </div>
          </div>
        </motion.div>
      ))}

      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex justify-start w-full"
        >
          <div className="flex gap-3 max-w-[85%]">
            <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-dark-card border border-white/10 flex items-center justify-center shadow-lg">
              <BsRobot className="text-primary-400" />
            </div>
            <div className="bg-white/5 backdrop-blur-md border border-white/5 p-4 rounded-2xl rounded-tl-sm flex items-center gap-1.5">
              <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce"></div>
            </div>
          </div>
        </motion.div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}
