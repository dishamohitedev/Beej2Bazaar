import React, { useState } from 'react';
import { X, Send, MessageSquare, ShieldCheck } from 'lucide-react';
import { FeedPost, FeedComment } from '../../pages/Community/mockData';
import { motion } from 'framer-motion';

interface CommentModalProps {
  post: FeedPost;
  onClose: () => void;
  onAddComment: (postId: string, commentContent: string) => void;
}

export const CommentModal: React.FC<CommentModalProps> = ({
  post,
  onClose,
  onAddComment
}) => {
  const [commentText, setCommentText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    onAddComment(post.id, commentText);
    setCommentText('');
  };

  const getRoleStyle = (role: string) => {
    switch (role) {
      case 'Expert':
        return 'text-emerald-600 bg-emerald-50 border-emerald-100';
      case 'Government Officer':
        return 'text-amber-600 bg-amber-50 border-amber-100';
      case 'Trader':
        return 'text-blue-600 bg-blue-50 border-blue-100';
      default:
        return 'text-slate-500 bg-slate-50 border-slate-100';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-slate-900/60 backdrop-blur-sm">
      {/* Background click close handler */}
      <div className="absolute inset-0" onClick={onClose} />

      {/* Modal Container */}
      <motion.div
        initial={{ opacity: 0, y: 100 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 100 }}
        transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
        className="relative w-full sm:max-w-lg bg-white rounded-t-[28px] sm:rounded-[28px] shadow-soft-xl max-h-[85vh] sm:max-h-[75vh] flex flex-col overflow-hidden z-10 border border-slate-100 pb-safe"
      >
        {/* Modal Header */}
        <div className="flex justify-between items-center px-5 py-4 border-b border-slate-100 shrink-0">
          <div className="flex items-center gap-2">
            <MessageSquare size={16} className="text-[#2E7D32]" />
            <h3 className="text-sm font-black text-slate-800 uppercase tracking-wider">Comments</h3>
          </div>
          <button 
            onClick={onClose}
            className="h-8 w-8 rounded-full bg-slate-50 hover:bg-slate-100 transition-colors flex items-center justify-center text-slate-400 hover:text-slate-650 cursor-pointer outline-none"
          >
            <X size={16} />
          </button>
        </div>

        {/* Scrollable Modal Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {/* Post Preview */}
          <div className="flex gap-3 pb-4 border-b border-slate-100/80">
            <div className="h-8 w-8 rounded-full overflow-hidden shrink-0">
              <img src={post.avatarUrl} alt={post.authorName} className="w-full h-full object-cover" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-xs text-slate-800">{post.authorName}</span>
                {post.isVerified && <ShieldCheck size={12} className="text-[#2E7D32]" />}
                <span className="text-[9px] text-slate-400 font-semibold">{post.timestamp}</span>
              </div>
              <p className="text-xs font-semibold text-slate-500 leading-relaxed mt-1.5">
                {post.content}
              </p>
            </div>
          </div>

          {/* Comments List */}
          <div className="space-y-4">
            {post.comments.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-xs font-bold text-slate-400">No comments yet. Start the conversation!</p>
              </div>
            ) : (
              post.comments.map((comment) => (
                <div key={comment.id} className="flex gap-3 items-start bg-slate-50/50 p-3 rounded-2xl border border-slate-100/40">
                  <div className="h-8 w-8 rounded-full bg-slate-100 overflow-hidden shrink-0 border border-slate-50">
                    {comment.avatarUrl ? (
                      <img src={comment.avatarUrl} alt={comment.authorName} className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center font-bold text-xs text-slate-400 bg-slate-100">
                        {comment.authorName[0]}
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-1.5 flex-wrap">
                      <div className="flex items-center gap-1.5">
                        <span className="font-extrabold text-xs text-slate-800">{comment.authorName}</span>
                        <span className={`text-[8px] font-black uppercase tracking-wider px-1.5 py-0.5 rounded border shrink-0 ${getRoleStyle(comment.role)}`}>
                          {comment.role}
                        </span>
                      </div>
                      <span className="text-[9px] text-slate-400 font-semibold">{comment.timestamp}</span>
                    </div>
                    <p className="text-xs font-semibold text-slate-600 leading-relaxed mt-1.5 whitespace-pre-wrap">
                      {comment.content}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Modal Footer: Add Comment input bar */}
        <form onSubmit={handleSubmit} className="border-t border-slate-100 p-4 bg-slate-50 flex gap-2 items-center shrink-0">
          <input
            type="text"
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
            placeholder="Write a comment..."
            className="flex-1 bg-white text-xs font-semibold text-slate-700 placeholder-slate-400 border border-slate-150 rounded-2xl px-4 py-3 outline-none"
            maxLength={180}
          />
          <button
            type="submit"
            disabled={!commentText.trim()}
            className={`h-10 w-10 rounded-2xl flex items-center justify-center transition-all cursor-pointer ${
              commentText.trim()
                ? 'bg-[#2E7D32] hover:bg-[#256428] text-white shadow-sm'
                : 'bg-slate-100 text-slate-350 cursor-not-allowed'
            }`}
          >
            <Send size={15} />
          </button>
        </form>
      </motion.div>
    </div>
  );
};
export default CommentModal;
