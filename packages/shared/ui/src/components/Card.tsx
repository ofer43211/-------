import React from 'react';

export interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ title, children, className }) => {
  return (
    <div className={className} data-component="card">
      {title && <h3>{title}</h3>}
      <div>{children}</div>
    </div>
  );
};
