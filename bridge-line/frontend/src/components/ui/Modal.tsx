import React from 'react';
import { Dialog, DialogProps } from '@mui/material';

export interface ModalProps extends DialogProps {
  open: boolean;
  onClose: () => void;
}

const Modal: React.FC<ModalProps> = ({ children, ...props }) => {
  return <Dialog {...props}>{children}</Dialog>;
};

export default Modal;
