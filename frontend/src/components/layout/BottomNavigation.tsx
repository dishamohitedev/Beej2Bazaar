import React from 'react';
import { Home, Sparkles, Droplet, MessageSquare, User } from 'lucide-react';

interface BottomNavigationProps {
  activeTab: string;
  onChangeTab: (tab: string) => void;
}

export const BottomNavigation: React.FC<BottomNavigationProps> = ({ activeTab, onChangeTab }) => {
  const tabs = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'recommend', label: 'Recommend', icon: Sparkles },
    { id: 'irrigation', label: 'Irrigation', icon: Droplet },
    { id: 'community', label: 'Community', icon: MessageSquare },
    { id: 'profile', label: 'Profile', icon: User },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 border-t border-[#2e7d32]/5 bg-white/95 pb-safe shadow-soft-lg backdrop-blur-lg">
      <div className="mx-auto flex h-16 max-w-lg items-center justify-around px-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onChangeTab(tab.id)}
              className={`flex flex-col items-center justify-center gap-0.5 w-16 h-12 rounded-xl transition-all duration-200 outline-none cursor-pointer ${
                isActive
                  ? 'text-[#2E7D32] scale-105 font-bold'
                  : 'text-slate-400 hover:text-slate-650'
              }`}
            >
              <Icon
                size={20}
                className={`transition-transform duration-200 ${
                  isActive ? 'stroke-[2.5px] text-[#2E7D32]' : 'stroke-[2px]'
                }`}
              />
              <span className="text-[10px] tracking-tight">{tab.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
