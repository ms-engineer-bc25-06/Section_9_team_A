import React from 'react';
import { Chip, ChipProps } from '@mui/material';

export interface BadgeProps extends Omit<ChipProps, 'variant'> {
  variant?: 'filled' | 'outlined';
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
}

const Badge: React.FC<BadgeProps> = ({
  variant = 'filled',
  color = 'primary',
  ...props
}) => {
  return <Chip variant={variant} color={color} {...props} />;
};

export default Badge;
