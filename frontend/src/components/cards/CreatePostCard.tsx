import React, { useState, useRef } from 'react';
import { Card } from '../ui/Card';
import { Camera, Image as ImageIcon, Send, HelpCircle, FileText, Check, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface CreatePostCardProps {
  onPostCreated: (content: string, type: 'update' | 'question', imageUrl?: string) => void;
  userAvatar?: string;
  userName?: string;
}

export const CreatePostCard: React.FC<CreatePostCardProps> = ({
  onPostCreated,
  userAvatar = 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80',
  userName = 'Ramesh Patil'
}) => {
  const [content, setContent] = useState('');
  const [postType, setPostType] = useState<'update' | 'question'>('update');
  const [attachedImage, setAttachedImage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handlePost = () => {
    if (!content.trim()) return;
    setIsSubmitting(true);
    
    // Simulate short submission delay for micro-animation
    setTimeout(() => {
      onPostCreated(content, postType, attachedImage || undefined);
      setContent('');
      setAttachedImage(null);
      setIsSubmitting(false);
    }, 800);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const fileUrl = URL.createObjectURL(e.target.files[0]);
      setAttachedImage(fileUrl);
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  // Pre-configured mock images for easy crop attachment demo
  const selectMockAttachment = (url: string) => {
    setAttachedImage(url);
  };

  return (
    <Card className="border border-slate-100/60 bg-white">
      <div className="flex gap-4 items-start">
        {/* Left User Avatar */}
        <div className="h-10 w-10 rounded-full bg-slate-100 overflow-hidden shrink-0 border border-slate-100">
          <img src={userAvatar} alt="User Profile" className="w-full h-full object-cover" />
        </div>

        {/* Right Input Area */}
        <div className="flex-1 space-y-3 min-w-0">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder={
              postType === 'question' 
                ? "What farming question do you have today?" 
                : "Share your crop updates or experiences..."
            }
            className="w-full text-sm font-semibold text-slate-700 placeholder-slate-400 border-none outline-none resize-none min-h-[70px] bg-transparent py-1.5"
            maxLength={280}
          />

          {/* Attached image preview */}
          <AnimatePresence>
            {attachedImage && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="relative rounded-2xl overflow-hidden aspect-[2/1] border border-slate-100"
              >
                <img src={attachedImage} alt="Attached Preview" className="w-full h-full object-cover" />
                <button
                  onClick={() => setAttachedImage(null)}
                  className="absolute top-2 right-2 h-7 w-7 rounded-full bg-black/60 hover:bg-black/80 flex items-center justify-center text-white transition-colors cursor-pointer"
                >
                  <X size={14} />
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            accept="image/*" 
            className="hidden" 
          />

          {/* Classification buttons and Actions row */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100">
            {/* Toggle Classifications */}
            <div className="flex gap-1.5">
              <button
                type="button"
                onClick={() => setPostType('update')}
                className={`px-3 py-1.5 rounded-full text-[10px] font-black uppercase tracking-wider transition-all flex items-center gap-1 cursor-pointer border ${
                  postType === 'update'
                    ? 'bg-[#2E7D32]/10 text-[#2E7D32] border-[#2E7D32]/20'
                    : 'bg-slate-50 text-slate-400 border-slate-150 hover:bg-slate-100'
                }`}
              >
                <FileText size={11} />
                <span>Share Update</span>
              </button>

              <button
                type="button"
                onClick={() => setPostType('question')}
                className={`px-3 py-1.5 rounded-full text-[10px] font-black uppercase tracking-wider transition-all flex items-center gap-1 cursor-pointer border ${
                  postType === 'question'
                    ? 'bg-purple-50 text-purple-700 border-purple-100'
                    : 'bg-slate-50 text-slate-400 border-slate-150 hover:bg-slate-100'
                }`}
              >
                <HelpCircle size={11} />
                <span>Ask Question</span>
              </button>
            </div>

            {/* Photo Attachment & Submit controls */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={triggerFileSelect}
                className="h-9 w-9 rounded-xl bg-slate-50 border border-slate-100 hover:bg-slate-100 text-slate-500 transition-colors flex items-center justify-center cursor-pointer"
                title="Attach Crop Photo"
              >
                <Camera size={16} className="text-slate-500" />
              </button>

              <button
                type="button"
                onClick={handlePost}
                disabled={!content.trim() || isSubmitting}
                className={`px-4 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-wider transition-all flex items-center gap-1.5 shadow-sm cursor-pointer ${
                  content.trim() && !isSubmitting
                    ? 'bg-[#2E7D32] hover:bg-[#256428] text-white'
                    : 'bg-slate-100 text-slate-350 cursor-not-allowed shadow-none'
                }`}
              >
                {isSubmitting ? (
                  <>
                    <Send size={11} className="animate-pulse" />
                    <span>Posting...</span>
                  </>
                ) : (
                  <>
                    <Send size={11} />
                    <span>Post</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
