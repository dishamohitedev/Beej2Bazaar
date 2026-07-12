import React from 'react';
import { motion } from 'framer-motion';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  delay?: number;
}

export const Card: React.FC<CardProps> = ({ children, className = '', delay = 0, ...props }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.5, 
        delay: delay, 
        ease: [0.16, 1, 0.3, 1] 
      }}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
      className={`bg-white rounded-[24px] p-6 border border-[#2e7d32]/5 shadow-elevation hover:shadow-subtle transition-shadow duration-300 ${className}`}
      {...props}
    >
      {children}
    </motion.div>
  );
};
