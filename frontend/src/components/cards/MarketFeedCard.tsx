import React from 'react';
import { Card } from '../ui/Card';
import { Heart, MessageSquare, Share2, ShieldCheck, TrendingUp, TrendingDown, Store } from 'lucide-react';
import { FeedPost } from '../../pages/Community/mockData';

interface MarketFeedCardProps {
  post: FeedPost;
  onLikeToggle: (postId: string) => void;
  onCommentClick: (post: FeedPost) => void;
  onShareClick: (post: FeedPost) => void;
  delay?: number;
}

export const MarketFeedCard: React.FC<MarketFeedCardProps> = ({
  post,
  onLikeToggle,
  onCommentClick,
  onShareClick,
  delay = 0
}) => {
  const details = post.marketDetails;

  return (
    <Card delay={delay} className="border border-emerald-100 bg-gradient-to-br from-white to-emerald-50/10 hover:shadow-subtle duration-300 relative overflow-hidden">
      {/* Emerald accent ribbon */}
      <div className="absolute top-0 left-0 w-1.5 h-full bg-[#2E7D32]" />

      <div className="pl-1.5 flex gap-3">
        {/* User Avatar */}
        <div className="h-9 w-9 rounded-full bg-slate-100 overflow-hidden shrink-0 border border-slate-50">
          <img src={post.avatarUrl} alt={post.authorName} className="w-full h-full object-cover" />
        </div>

        {/* Post details */}
        <div className="flex-1 min-w-0">
          {/* Header row */}
          <div className="flex flex-wrap items-center justify-between gap-x-2 gap-y-0.5">
            <div className="flex items-center gap-1.5 min-w-0">
              <span className="font-extrabold text-xs text-slate-800 truncate">
                {post.authorName}
              </span>
              {post.isVerified && (
                <ShieldCheck size={13} className="text-[#2E7D32] fill-[#2E7D32]/10 shrink-0" />
              )}
              <span className="text-[8px] font-black uppercase tracking-wider px-1.5 py-0.5 rounded border bg-emerald-50 text-[#2E7D32] border-emerald-100 shrink-0">
                Market Update
              </span>
            </div>
            <span className="text-[10px] font-semibold text-slate-400">
              {post.timestamp}
            </span>
          </div>

          {/* Market report text */}
          <p className="text-xs font-semibold text-slate-650 leading-relaxed mt-2.5 whitespace-pre-wrap">
            {post.content}
          </p>

          {/* Mandi update metrics box */}
          {details && (
            <div className="mt-3.5 p-3.5 bg-emerald-500/[0.02] border border-emerald-500/10 rounded-2xl">
              <div className="flex justify-between items-center mb-2.5">
                <div className="flex items-center gap-1.5 text-[10px] font-black uppercase tracking-wider text-[#2E7D32]">
                  <Store size={12} />
                  <span>Mandi Rates</span>
                </div>
                <div className="flex items-center gap-1">
                  {details.trend === 'up' ? (
                    <TrendingUp size={14} className="text-[#2E7D32] animate-bounce" />
                  ) : (
                    <TrendingDown size={14} className="text-[#D32F2F] animate-bounce" />
                  )}
                  <span className={`text-[10px] font-black uppercase tracking-wider ${details.trend === 'up' ? 'text-[#2E7D32]' : 'text-[#D32F2F]'}`}>
                    {details.trend === 'up' ? `+₹${details.priceChange} Up` : `-₹${Math.abs(details.priceChange)} Down`}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-x-4 gap-y-2 pt-2 border-t border-emerald-500/5 text-xs">
                <div className="flex justify-between font-semibold">
                  <span className="text-slate-400 text-[10px]">Crop:</span>
                  <span className="text-slate-700 font-extrabold">{details.cropName}</span>
                </div>
                <div className="flex justify-between font-semibold">
                  <span className="text-slate-400 text-[10px]">Market:</span>
                  <span className="text-slate-700 font-extrabold truncate max-w-[90px]">{details.marketName}</span>
                </div>
                <div className="flex justify-between font-semibold col-span-2 pt-1 border-t border-slate-100/50">
                  <span className="text-slate-400 text-[10px]">Price per Quintal:</span>
                  <span className="text-slate-800 font-black text-sm">₹{details.pricePerQuintal}</span>
                </div>
              </div>
            </div>
          )}

          {/* Interactivity indicators */}
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
export default MarketFeedCard;
