import React from 'react';
import { Card } from '../ui/Card';
import { MandiRate } from '../../types';
import { Store, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MarketCardProps {
  rates: MandiRate[];
  delay?: number;
}

export const MarketCard: React.FC<MarketCardProps> = ({ rates, delay = 0 }) => {
  return (
    <Card delay={delay} className="flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Live Mandi Prices</h2>
          <div className="h-7 w-7 rounded-lg bg-amber-50 flex items-center justify-center text-[#F9A826]">
            <Store size={15} />
          </div>
        </div>

        <p className="text-xs text-slate-500 font-semibold mb-4">
          Current rates across regional APMC markets:
        </p>

        {/* Minimal Table layout */}
        <div className="divide-y divide-slate-100">
          {rates.map((item) => {
            const isUp = item.trend === 'up';
            const isDown = item.trend === 'down';
            
            return (
              <div key={item.id} className="py-3 flex justify-between items-center first:pt-0 last:pb-0">
                <div>
                  <h4 className="text-xs font-bold text-slate-800">{item.cropName}</h4>
                  <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">{item.marketName}</span>
                </div>
                
                <div className="text-right leading-none">
                  <span className="text-sm font-extrabold text-slate-800">₹{item.pricePerQuintal}/q</span>
                  <div className="flex items-center justify-end gap-1 mt-1 text-[9px] font-bold">
                    {isUp && (
                      <>
                        <TrendingUp size={10} className="text-[#2E7D32]" />
                        <span className="text-[#2E7D32]">+{item.priceChange}</span>
                      </>
                    )}
                    {isDown && (
                      <>
                        <TrendingDown size={10} className="text-[#D32F2F]" />
                        <span className="text-[#D32F2F]">{item.priceChange}</span>
                      </>
                    )}
                    {!isUp && !isDown && (
                      <>
                        <Minus size={10} className="text-slate-400" />
                        <span className="text-slate-400">Stable</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center text-[10px] text-slate-400 font-semibold">
        <span>Updated: Today, 12:45 PM</span>
        <button className="font-bold text-[#2E7D32] hover:underline cursor-pointer">
          See All Mandis →
        </button>
      </div>
    </Card>
  );
};
