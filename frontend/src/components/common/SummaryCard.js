import React from 'react';
import PropTypes from 'prop-types';
import { Card, CardContent, Typography, Box } from '@mui/material';


import ReactIs from 'react-is';

const SummaryCard = ({ title, value, icon }) => (
	<Card sx={{ minHeight: 120, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', boxShadow: 2, borderRadius: 2 }}>
		<CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: 2 }}>
			<Box mb={1}>
				{ReactIs.isElement(icon) ? icon : null}
			</Box>
			<Typography variant="subtitle2" color="text.secondary" fontWeight={600} gutterBottom>
				{title}
			</Typography>
			<Typography variant="h5" fontWeight={700} color="primary">
				{value}
			</Typography>
		</CardContent>
	</Card>
);

SummaryCard.propTypes = {
	title: PropTypes.string.isRequired,
	value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
	icon: PropTypes.element,
};

export default SummaryCard;