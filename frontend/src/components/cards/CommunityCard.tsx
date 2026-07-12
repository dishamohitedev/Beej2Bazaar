import React from 'react';
import { Card } from '../ui/Card';
import { CommunityPost } from '../../types';
import { MessageSquare, Heart, MessageCircle } from 'lucide-react';
import { Badge } from '../ui/Badge';

interface CommunityCardProps {
  post: CommunityPost;
  delay?: number;
}

export const CommunityCard: React.FC<CommunityCardProps> = ({ post, delay = 0 }) => {
  const getRoleVariant = (role: string) => {
    switch (role) {
      case 'Expert':
        return 'primary';
      case 'Trader':
        return 'accent';
      default:
        return 'neutral';
    }
  };

  return (
    <Card delay={delay} className="flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Community Preview</h2>
          <div className="h-7 w-7 rounded-lg bg-purple-55 bg-purple-50 flex items-center justify-center text-purple-600">
            <MessageCircle size={15} />
          </div>
        </div>

        {/* Post details */}
        <div className="mt-2 space-y-3">
          <div className="flex items-center gap-2">
            {post.avatarUrl ? (
              <img 
                src={post.avatarUrl} 
                alt={post.authorName} 
                className="h-7 w-7 rounded-full object-cover border border-slate-100"
              />
            ) : (
              <div className="h-7 w-7 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-500">
                {post.authorName[0]}
              </div>
            )}
            <div className="flex flex-col">
              <span className="text-xs font-bold text-slate-800 leading-none">{post.authorName}</span>
              <span className="text-[8px] font-bold text-slate-400 mt-0.5 uppercase tracking-wider">
                {post.role}
              </span>
            </div>
            <div className="ml-auto">
              <Badge variant={getRoleVariant(post.role)}>{post.tag}</Badge>
            </div>
          </div>

          <p className="text-xs text-slate-600 font-semibold leading-relaxed line-clamp-3 italic">
            "{post.content}"
          </p>
        </div>
      </div>

      <div className="mt-6 border-t border-slate-100 pt-4 flex items-center gap-4 text-[10px] font-bold text-slate-400">
        <div className="flex items-center gap-1">
          <Heart size={12} className="text-slate-400" />
          <span>{post.likesCount} Likes</span>
        </div>
        <div className="flex items-center gap-1">
          <MessageSquare size={12} className="text-slate-400" />
          <span>{post.repliesCount} Replies</span>
        </div>
        <button className="ml-auto font-bold text-[#2E7D32] hover:underline cursor-pointer">
          Reply →
        </button>
      </div>
    </Card>
  );
};
