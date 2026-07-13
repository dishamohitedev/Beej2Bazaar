import React, { useState } from 'react';
import { FeedHeader } from '../../components/cards/FeedHeader';
import { CreatePostCard } from '../../components/cards/CreatePostCard';
import { CategoryTabs } from '../../components/cards/CategoryTabs';
import { FeedCard } from '../../components/cards/FeedCard';
import { DiseaseAlertFeedCard } from '../../components/cards/DiseaseAlertFeedCard';
import { GovernmentCard } from '../../components/cards/GovernmentCard';
import { MarketFeedCard } from '../../components/cards/MarketFeedCard';
import { CommentModal } from '../../components/cards/CommentModal';
import { mockFeedPosts, FeedPost, FeedComment } from './mockData';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Heart, RefreshCw } from 'lucide-react';

interface CommunityPageProps {
  onBackToDashboard: () => void;
  farmerDistrict?: string;
}

export const CommunityPage: React.FC<CommunityPageProps> = ({
  onBackToDashboard,
  farmerDistrict = 'Nashik'
}) => {
  const [posts, setPosts] = useState<FeedPost[]>(mockFeedPosts);
  const [activeCategory, setActiveCategory] = useState('all');
  const [selectedPostForComments, setSelectedPostForComments] = useState<FeedPost | null>(null);

  // Toggle Like state
  const handleLikeToggle = (postId: string) => {
    setPosts(prevPosts =>
      prevPosts.map(post => {
        if (post.id === postId) {
          const hasLiked = !post.hasLiked;
          return {
            ...post,
            hasLiked,
            likesCount: hasLiked ? post.likesCount + 1 : post.likesCount - 1
          };
        }
        return post;
      })
    );
  };

  // Trigger link copying simulation
  const handleShareClick = (post: FeedPost) => {
    navigator.clipboard.writeText(`${window.location.origin}/community/post/${post.id}`).then(
      () => {
        // Quick visual notice
        alert('Feed link copied to clipboard!');
      },
      () => {
        alert('Could not copy link.');
      }
    );
  };

  // Add Comment callback
  const handleAddComment = (postId: string, commentContent: string) => {
    const newComment: FeedComment = {
      id: `c_${Date.now()}`,
      authorName: 'Ramesh Patil', // Logged in farmer
      role: 'Farmer',
      content: commentContent,
      timestamp: 'Just now'
    };

    setPosts(prevPosts =>
      prevPosts.map(post => {
        if (post.id === postId) {
          const updatedComments = [...post.comments, newComment];
          const updatedPost = {
            ...post,
            comments: updatedComments,
            commentsCount: updatedComments.length
          };
          // Synchronize comments modal view state if currently open
          if (selectedPostForComments?.id === postId) {
            setSelectedPostForComments(updatedPost);
          }
          return updatedPost;
        }
        return post;
      })
    );
  };

  // Create new post callback
  const handlePostCreated = (content: string, type: 'update' | 'question', imageUrl?: string) => {
    const newPost: FeedPost = {
      id: `post_${Date.now()}`,
      authorName: 'Ramesh Patil',
      avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80',
      role: 'Farmer',
      isVerified: true,
      timestamp: 'Just now',
      postType: type,
      content,
      imageUrl,
      likesCount: 0,
      commentsCount: 0,
      comments: [],
      hasLiked: false
    };

    // Prepend new post
    setPosts(prevPosts => [newPost, ...prevPosts]);
  };

  // Filter posts based on active tab category
  const filteredPosts = posts.filter(post => {
    switch (activeCategory) {
      case 'nearby':
        // Show alerts / posts from the user's specific district
        const isNearbyDisease = post.postType === 'disease' && post.diseaseDetails?.district === farmerDistrict;
        const isNearbyMarket = post.postType === 'market' && post.marketDetails?.marketName.includes(farmerDistrict);
        const isFarmerPost = post.role === 'Farmer';
        return isNearbyDisease || isNearbyMarket || isFarmerPost;
        
      case 'questions':
        return post.postType === 'question';
        
      case 'diseases':
        return post.postType === 'disease';
        
      case 'government':
        return post.postType === 'government';
        
      case 'market':
        return post.postType === 'market';
        
      case 'weather':
        return post.postType === 'weather';
        
      default:
        return true;
    }
  });

  // Render card based on post type
  const renderFeedCard = (post: FeedPost, index: number) => {
    const delay = index * 0.05;
    
    switch (post.postType) {
      case 'disease':
        return (
          <DiseaseAlertFeedCard
            key={post.id}
            post={post}
            onLikeToggle={handleLikeToggle}
            onCommentClick={setSelectedPostForComments}
            onShareClick={handleShareClick}
            delay={delay}
          />
        );
      case 'government':
        return (
          <GovernmentCard
            key={post.id}
            post={post}
            onLikeToggle={handleLikeToggle}
            onCommentClick={setSelectedPostForComments}
            onShareClick={handleShareClick}
            delay={delay}
          />
        );
      case 'market':
        return (
          <MarketFeedCard
            key={post.id}
            post={post}
            onLikeToggle={handleLikeToggle}
            onCommentClick={setSelectedPostForComments}
            onShareClick={handleShareClick}
            delay={delay}
          />
        );
      default:
        return (
          <FeedCard
            key={post.id}
            post={post}
            onLikeToggle={handleLikeToggle}
            onCommentClick={setSelectedPostForComments}
            onShareClick={handleShareClick}
            delay={delay}
          />
        );
    }
  };

  return (
    <div className="space-y-6 max-w-lg mx-auto pb-10">
      {/* 1. Header */}
      <FeedHeader onBackToDashboard={onBackToDashboard} />

      {/* 2. Create Post Section */}
      <CreatePostCard onPostCreated={handlePostCreated} />

      {/* 3. Category scroll navigation */}
      <CategoryTabs activeTab={activeCategory} onTabChange={setActiveCategory} />

      {/* 4. Feeds Grid list */}
      <div className="space-y-5">
        <AnimatePresence mode="popLayout">
          {filteredPosts.length > 0 ? (
            filteredPosts.map((post, idx) => renderFeedCard(post, idx))
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="py-16 text-center bg-white rounded-3xl border border-slate-100/50 shadow-sm"
            >
              <MessageSquare size={36} className="mx-auto text-slate-300 mb-3 animate-pulse" />
              <h3 className="text-xs font-black text-slate-700 uppercase tracking-wide">No Updates Found</h3>
              <p className="text-[10px] font-semibold text-slate-450 mt-1 max-w-xs mx-auto">
                No active announcements fit this category right now. Share an update to start the feed!
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* 5. Interactive Comments Modal Sheet */}
      <AnimatePresence>
        {selectedPostForComments && (
          <CommentModal
            post={selectedPostForComments}
            onClose={() => setSelectedPostForComments(null)}
            onAddComment={handleAddComment}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default CommunityPage;
