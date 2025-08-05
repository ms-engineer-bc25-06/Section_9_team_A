import React from 'react';
import { Avatar as MuiAvatar, AvatarProps as MuiAvatarProps } from '@mui/material';

export interface AvatarProps extends MuiAvatarProps {
  size?: 'small' | 'medium' | 'large';
}

const Avatar: React.FC<AvatarProps> = ({ size = 'medium', ...props }) => {
  return <MuiAvatar {...props} />;
};

export default Avatar;
