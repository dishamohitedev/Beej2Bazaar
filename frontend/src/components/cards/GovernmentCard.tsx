import React from 'react';
import { Card } from '../ui/Card';
import { Heart, MessageSquare, Share2, ShieldCheck, Landmark } from 'lucide-react';
import { FeedPost } from '../../pages/Community/mockData';
import { Badge } from '../ui/Badge';

interface GovernmentCardProps {
  post: FeedPost;
  onLikeToggle: (postId: string) => void;
  onCommentClick: (post: FeedPost) => void;
  onShareClick: (post: FeedPost) => void;
  delay?: number;
}

export const GovernmentCard: React.FC<GovernmentCardProps> = ({
  post,
  onLikeToggle,
  onCommentClick,
  onShareClick,
  delay = 0
}) => {
  const details = post.governmentDetails;

  const getLevelVariant = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'critical':
        return 'danger';
      case 'warning':
        return 'accent';
      default:
        return 'primary';
    }
  };

  return (
    <Card delay={delay} className="border border-amber-100 bg-gradient-to-br from-white to-amber-50/10 hover:shadow-subtle duration-300 relative overflow-hidden">
      {/* Gold accent ribbon */}
      <div className="absolute top-0 left-0 w-1.5 h-full bg-[#F9A826]" />

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
              <span className="text-[8px] font-black uppercase tracking-wider px-1.5 py-0.5 rounded border bg-amber-50 text-amber-700 border-amber-100 shrink-0">
                Official Circular
              </span>
            </div>
            <span className="text-[10px] font-semibold text-slate-400">
              {post.timestamp}
            </span>
          </div>

          {/* Advisory content text */}
          <p className="text-xs font-semibold text-slate-650 leading-relaxed mt-2.5 whitespace-pre-wrap">
            {post.content}
          </p>

          {/* Government circular info box */}
          {details && (
            <div className="mt-3.5 p-3.5 bg-amber-500/[0.02] border border-amber-500/10 rounded-2xl">
              <div className="flex justify-between items-start gap-2 mb-2">
                <div className="flex items-center gap-1.5 text-[10px] font-black uppercase tracking-wider text-amber-700">
                  <Landmark size={12} />
                  <span>Official Notice</span>
                </div>
                <Badge variant={getLevelVariant(details.advisoryLevel)}>
                  {details.advisoryLevel} Level
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-x-4 gap-y-2 mt-2 pt-2 border-t border-amber-500/5 text-xs">
                <div className="flex justify-between font-semibold col-span-2">
                  <span className="text-slate-400 text-[10px]">Authority:</span>
                  <span className="text-slate-700 font-extrabold truncate max-w-[200px]" title={details.issuingAuthority}>
                    {details.issuingAuthority}
                  </span>
                </div>
                <div className="flex justify-between font-semibold col-span-2 pt-1 border-t border-slate-100/50">
                  <span className="text-slate-400 text-[10px]">Target Region:</span>
                  <span className="text-slate-700 font-extrabold">{details.targetRegion}</span>
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
export default GovernmentCard;
