import React from 'react';

interface SectionLabelProps {
  children: React.ReactNode;
  className?: string;
}

export const SectionLabel: React.FC<SectionLabelProps> = ({
  children,
  className = ''
}) => {
  return (
    <div className={`section-label ${className}`}>
      <span className="section-label-text">{children}</span>
    </div>
  );
};