import React from 'react';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';

const Notification = ({ message, type = 'info', open, onClose, autoHideDuration = 4000 }) => {
	const isOpen = open !== undefined ? open : Boolean(message);
	return (
		<Snackbar
			open={isOpen}
			autoHideDuration={autoHideDuration}
			onClose={onClose}
			anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
		>
			<Alert onClose={onClose} severity={type} sx={{ width: '100%' }} variant="filled">
				{message}
			</Alert>
		</Snackbar>
	);
};

export default Notification;