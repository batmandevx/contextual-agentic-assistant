import { useState, KeyboardEvent } from 'react';
import { motion } from 'framer-motion';
import { BiSend, BiPaperclip, BiMicrophone } from 'react-icons/bi';
import { BsCalendarEvent, BsPencil, BsLightningCharge } from 'react-icons/bs';

interface InputBoxProps {
  onSendMessage: (message: string) => void;
  loading?: boolean;
}

export default function InputBox({ onSendMessage, loading }: InputBoxProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !loading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickActions = [
    { icon: BsPencil, label: 'Draft email', prompt: 'Draft an email to ' },
    { icon: BsCalendarEvent, label: 'Schedule', prompt: 'Schedule a meeting for ' },
    { icon: BsLightningCharge, label: 'Summarize', prompt: 'Summarize this: ' },
  ];

  const handleQuickAction = (prompt: string) => {
    setInput(prompt);
  };

  return (
    <div className="w-full relative">
      {/* Quick Actions */}
      <div className="flex gap-2 mb-3 overflow-x-auto pb-1 scrollbar-hide">
        {quickActions.map((action, i) => (
          <motion.button
            key={i}
            whileHover={{ scale: 1.05, backgroundColor: 'rgba(255,255,255,0.1)' }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleQuickAction(action.prompt)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 border border-white/10 rounded-full text-xs text-slate-300 whitespace-nowrap transition-colors"
          >
            <action.icon className="text-secondary-400" />
            {action.label}
          </motion.button>
        ))}
      </div>

      <div className="relative group">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-2xl opacity-20 group-focus-within:opacity-50 transition duration-500 blur"></div>
        <div className="relative bg-dark-surface/90 backdrop-blur-xl rounded-xl border border-white/10 flex items-end p-2 shadow-2xl">
          <button className="p-3 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-white/5">
            <BiPaperclip className="text-xl" />
          </button>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className="flex-1 bg-transparent border-none focus:ring-0 text-slate-100 placeholder-slate-500 resize-none max-h-32 min-h-[50px] py-3 px-2 text-sm md:text-base scrollbar-thin scrollbar-thumb-white/10"
            rows={1}
            style={{ height: 'auto', minHeight: '50px' }}
            disabled={loading}
          />

          <div className="flex items-center gap-1 pb-1">
            <button className="p-3 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-white/5 hidden md:block">
              <BiMicrophone className="text-xl" />
            </button>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className={`p-3 rounded-lg transition-all duration-200
                 ${input.trim() && !loading
                  ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-500/25'
                  : 'bg-white/5 text-slate-500 cursor-not-allowed'}`}
            >
              <BiSend className="text-xl" />
            </motion.button>
          </div>
        </div>
      </div>

      <div className="text-center mt-2.5">
        <p className="text-[10px] text-slate-600">
          AI can make mistakes. Please verify important information.
        </p>
      </div>
    </div>
  );
}
