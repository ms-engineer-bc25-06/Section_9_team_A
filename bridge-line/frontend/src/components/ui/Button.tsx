import React from 'react';
import { Button as MuiButton, ButtonProps as MuiButtonProps } from '@mui/material';

export interface ButtonProps extends Omit<MuiButtonProps, 'variant'> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'small' | 'medium' | 'large';
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  children,
  sx,
  ...props
}) => {
  const getVariantProps = () => {
    switch (variant) {
      case 'primary':
        return { variant: 'contained' as const, color: 'primary' as const };
      case 'secondary':
        return { variant: 'contained' as const, color: 'secondary' as const };
      case 'outline':
        return { variant: 'outlined' as const, color: 'primary' as const };
      case 'ghost':
        return { variant: 'text' as const, color: 'primary' as const };
      default:
        return { variant: 'contained' as const, color: 'primary' as const };
    }
  };

  const getSizeProps = () => {
    switch (size) {
      case 'small':
        return { size: 'small' as const };
      case 'large':
        return { size: 'large' as const };
      default:
        return { size: 'medium' as const };
    }
  };

  return (
    <MuiButton
      {...getVariantProps()}
      {...getSizeProps()}
      sx={{
        borderRadius: 2,
        textTransform: 'none',
        fontWeight: 600,
        ...sx,
      }}
      {...props}
    >
      {children}
    </MuiButton>
  );
};
