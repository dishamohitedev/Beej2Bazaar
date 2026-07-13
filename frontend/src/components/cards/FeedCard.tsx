import React from 'react';
import { Card } from '../ui/Card';
import { Heart, MessageSquare, Share2, ShieldCheck } from 'lucide-react';
import { FeedPost } from '../../pages/Community/mockData';

interface FeedCardProps {
  post: FeedPost;
  onLikeToggle: (postId: string) => void;
  onCommentClick: (post: FeedPost) => void;
  onShareClick: (post: FeedPost) => void;
  delay?: number;
}

export const FeedCard: React.FC<FeedCardProps> = ({
  post,
  onLikeToggle,
  onCommentClick,
  onShareClick,
  delay = 0
}) => {
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
    <Card delay={delay} className="border border-slate-100/60 bg-white relative hover:shadow-subtle duration-300">
      <div className="flex gap-3">
        {/* User Avatar */}
        <div className="h-9 w-9 rounded-full bg-slate-100 overflow-hidden shrink-0 border border-slate-50">
          {post.avatarUrl ? (
            <img src={post.avatarUrl} alt={post.authorName} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center font-bold text-slate-400 bg-slate-50">
              {post.authorName[0]}
            </div>
          )}
        </div>

        {/* Post content area */}
        <div className="flex-1 min-w-0">
          {/* Header row: Author, badge, timestamp */}
          <div className="flex flex-wrap items-center justify-between gap-x-2 gap-y-0.5">
            <div className="flex items-center gap-1.5 min-w-0">
              <span className="font-extrabold text-xs text-slate-800 truncate">
                {post.authorName}
              </span>
              {post.isVerified && (
                <ShieldCheck size={13} className="text-[#2E7D32] fill-[#2E7D32]/10 shrink-0" />
              )}
              <span className={`text-[8px] font-black uppercase tracking-wider px-1.5 py-0.5 rounded border shrink-0 ${getRoleStyle(post.role)}`}>
                {post.role}
              </span>
            </div>
            <span className="text-[10px] font-semibold text-slate-400">
              {post.timestamp}
            </span>
          </div>

          {/* Post content */}
          <p className="text-xs font-semibold text-slate-600 leading-relaxed mt-2.5 whitespace-pre-wrap">
            {post.content}
          </p>

          {/* Optional image attachment */}
          {post.imageUrl && (
            <div className="mt-3 rounded-2xl overflow-hidden aspect-[2/1] border border-slate-50">
              <img src={post.imageUrl} alt="Post Attachment" className="w-full h-full object-cover" />
            </div>
          )}

          {/* Interactive controls row */}
          <div className="flex items-center justify-between pt-3 mt-4 border-t border-slate-100 text-slate-400 select-none">
            {/* Like */}
            <button
              onClick={() => onLikeToggle(post.id)}
              className={`flex items-center gap-1.5 text-[10px] font-bold uppercase transition-colors cursor-pointer group outline-none ${
                post.hasLiked ? 'text-red-500' : 'hover:text-red-500'
              }`}
            >
              <Heart 
                size={14} 
                className={`transition-all duration-200 ${
                  post.hasLiked ? 'fill-red-500 stroke-red-500 scale-110' : 'group-hover:scale-105'
                }`}
              />
              <span>{post.likesCount}</span>
            </button>

            {/* Comment */}
            <button
              onClick={() => onCommentClick(post)}
              className="flex items-center gap-1.5 text-[10px] font-bold uppercase hover:text-purple-650 transition-colors cursor-pointer outline-none group"
            >
              <MessageSquare size={14} className="group-hover:scale-105 transition-transform" />
              <span>{post.commentsCount}</span>
            </button>

            {/* Share */}
            <button
              onClick={() => onShareClick(post)}
              className="flex items-center gap-1.5 text-[10px] font-bold uppercase hover:text-[#2E7D32] transition-colors cursor-pointer outline-none group"
              title="Copy link to post"
            >
              <Share2 size={14} className="group-hover:scale-105 transition-transform" />
              <span>Share</span>
            </button>
          </div>
        </div>
      </div>
    </Card>
  );
};
export default FeedCard;
