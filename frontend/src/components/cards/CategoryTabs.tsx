import React from 'react';
import { Sparkles, MapPin, HelpCircle, AlertOctagon, Landmark, TrendingUp, CloudSun } from 'lucide-react';

interface CategoryTabsProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export const CategoryTabs: React.FC<CategoryTabsProps> = ({
  activeTab,
  onTabChange
}) => {
  const tabs = [
    { id: 'all', label: 'All', icon: Sparkles, color: 'text-blue-500' },
    { id: 'nearby', label: 'Nearby', icon: MapPin, color: 'text-emerald-500' },
    { id: 'questions', label: 'Questions', icon: HelpCircle, color: 'text-purple-500' },
    { id: 'diseases', label: 'Diseases', icon: AlertOctagon, color: 'text-red-500' },
    { id: 'government', label: 'Government', icon: Landmark, color: 'text-amber-500' },
    { id: 'market', label: 'Market', icon: TrendingUp, color: 'text-green-600' },
    { id: 'weather', label: 'Weather', icon: CloudSun, color: 'text-sky-500' },
  ];

  return (
    <div className="w-full overflow-x-auto scrollbar-none flex gap-2.5 pb-2.5 pt-1 -mx-4 px-4 md:mx-0 md:px-0">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex items-center gap-1.5 px-4 py-2.5 rounded-full text-[10px] font-black uppercase tracking-wider transition-all duration-200 cursor-pointer border shrink-0 outline-none ${
              isActive
                ? 'bg-[#2E7D32] border-[#2E7D32] text-white shadow-sm'
                : 'bg-white text-slate-500 border-slate-100 hover:border-slate-300 hover:text-slate-700'
            }`}
          >
            <Icon size={12} className={isActive ? 'text-white' : tab.color} />
            <span>{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
};
export default CategoryTabs;
