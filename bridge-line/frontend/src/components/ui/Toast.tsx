import React from 'react';
import { Alert, AlertProps, Snackbar, SnackbarProps } from '@mui/material';

export interface ToastProps extends Omit<SnackbarProps, 'open'> {
  open: boolean;
  message: string;
  severity?: AlertProps['severity'];
  onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({
  open,
  message,
  severity = 'info',
  onClose,
  ...props
}) => {
  return (
    <Snackbar open={open} onClose={onClose} {...props}>
      <Alert onClose={onClose} severity={severity}>
        {message}
      </Alert>
    </Snackbar>
  );
};

export default Toast;
