import React from 'react';
import { CircularProgress, Box, BoxProps } from '@mui/material';

export interface SpinnerProps extends BoxProps {
  size?: number;
  color?: 'primary' | 'secondary' | 'inherit';
}

const Spinner: React.FC<SpinnerProps> = ({
  size = 40,
  color = 'primary',
  ...props
}) => {
  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      {...props}
    >
      <CircularProgress size={size} color={color} />
    </Box>
  );
};

export default Spinner;
