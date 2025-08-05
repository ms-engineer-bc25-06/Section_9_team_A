import React from 'react';
import { Card as MuiCard, CardProps as MuiCardProps } from '@mui/material';

export interface CardProps extends Omit<MuiCardProps, 'variant'> {
  cardVariant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'small' | 'medium' | 'large';
}

export const Card: React.FC<CardProps> = ({
  cardVariant = 'default',
  padding = 'medium',
  children,
  sx,
  ...props
}) => {
  const getVariantProps = () => {
    switch (cardVariant) {
      case 'elevated':
        return { elevation: 4 };
      case 'outlined':
        return { variant: 'outlined' as const };
      default:
        return { elevation: 1 };
    }
  };

  const getPaddingProps = () => {
    switch (padding) {
      case 'none':
        return { sx: { p: 0 } };
      case 'small':
        return { sx: { p: 2 } };
      case 'large':
        return { sx: { p: 4 } };
      default:
        return { sx: { p: 3 } };
    }
  };

  return (
    <MuiCard
      {...getVariantProps()}
      sx={{
        borderRadius: 3,
        ...getPaddingProps().sx,
        ...sx,
      }}
      {...props}
    >
      {children}
    </MuiCard>
  );
};
